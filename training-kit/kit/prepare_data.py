"""Dataset Preparation: the work behind the "Dataset Preparation" program (prepare/dataset_preparation.py).

It gets a describing workspace (a folder of pictures with describing.json, see describe_package.py) ready for a
person to review, so they start from a good draft instead of an empty box. Two jobs, each run by itself or one after
the other:

1. CLEAN-UP (the "clean" command), for the workspace's new pictures (status "new", not cleaned before):
   - dark, blurry and near-identical pictures are SET ASIDE: their status becomes "skip" with the reason in the
     notes, so nothing is deleted and the person can bring one back in Describe pictures (Filter: Set aside);
     a picture that already has a description is never set aside, and of two near-identical pictures the sharper
     one is kept;
   - burned-in date stamps, TV station logos and fixed tickers (--overlays crop or fill) are found the same way the
     video tool finds them (video_frames.find_overlays: what stays fixed while the picture behind it changes), over
     each group of pictures of the same size (one camera or one programme); --overlay-box x,y,w,h (in percent) adds
     a box by hand, for a mark the finder cannot see (a logo on only a few pictures);
   - faces of people can be blurred (--blur-faces, OpenCV's YuNet face finder).
   A picture that is changed keeps its original in the hidden sub-folder ".originals" (never read for training).
   Stills from videos are cleaned by the video tool itself (video_frames.py); this is for pictures added any way.

2. DRAFTS (the "drafts" command): two, three or four picture models each write a DRAFT description of every new
   picture that has none, one model after the other (each is loaded once, describes every picture, and is let go,
   so a 16 GB graphics card is enough):
     qwen      Qwen3-VL 8B (the kit's own 8B model, Apache-2.0): long, plain descriptions; it does not refuse
               pictures of bodies or injuries;
     internvl  InternVL 3.5 8B (OpenGVLab, Apache-2.0): a different family of model, trained on different
               pictures, so its mistakes are different ones;
     florence  Florence-2 large (Microsoft, MIT): small and fast; a detailed caption and the text it can read;
     yours     your own trained describer: the kit's 4B (or 8B) model with the add-on of your newest finished
               training (only when a training has finished).
   Then, with --combine, Qwen3-VL 8B looks at the picture again with all the drafts and writes one starting
   description, keeping what is right, correcting what is wrong and adding what was missed. How much the drafts
   agree (0 to 1, from the words they share) is saved too: pictures whose drafts disagree need the most care, and
   Describe pictures can list them first.
   Everything goes into the picture's entry in describing.json as text (draft, draft_qwen, draft_internvl,
   draft_florence, draft_yours, draft_agreement, draft_engines), so it travels in packages to friends. A draft is
   never used for training: only a description a person saves (status "described" or "checked") is. Describe
   pictures puts the starting description into the Description box of a picture that has none and says that it is
   the computer's draft, to be checked and corrected.
   Stopped part-way, it carries on where it stopped: a picture that already has a model's draft is not done again.

Command line (kit\\run_prepare.cmd runs it in the kit's own Python):
    python prepare_data.py WORKSPACE clean [--no-set-aside] [--blur-faces] [--overlays keep|crop|fill]
        [--overlay-box X,Y,W,H ...]
    python prepare_data.py WORKSPACE drafts [--engines qwen,internvl,florence,yours] [--no-combine] [--redo]
    python prepare_data.py WORKSPACE all [the options of both]
    python prepare_data.py --self-test          (no graphics card needed: checks the parts that do not need one)
Every line it prints is plain words; lines starting "Finished" or "STOPPED" end a job, and "N of M" lines move the
program's progress bar.
"""

import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import describe_package as package  # noqa: E402

KIT = os.path.dirname(HERE)                         # the kit folder
WORK = os.path.join(KIT, "work")                    # models and the training's add-ons are kept here
ORIGINALS = ".originals"                            # the originals of changed pictures (hidden from training)

# The draft engines: key -> (name said to the person, Hugging Face repository, pinned commit, licence, size).
# "qwen" and "yours" use the kit's own models (train.MODELS), pinned there.
ENGINES = {
    "qwen": ("Qwen3-VL 8B", None, None, "Apache-2.0", "about 17 GB, the kit's own 8B model"),
    "internvl": ("InternVL 3.5 8B", "OpenGVLab/InternVL3_5-8B-HF", "741a7d03020411e666c6109218ab71e08151ef86",
                 "Apache-2.0", "about 17 GB"),
    "florence": ("Florence-2 large", "florence-community/Florence-2-large",
                 "4271c66b88cdbc05735372ec13b2360108de5317", "MIT", "about 1.5 GB"),
    "yours": ("your own trained describer", None, None, "your own", "the model of your newest finished training"),
}
ENGINE_ORDER = ("florence", "internvl", "yours", "qwen")     # the combining model (qwen) last: it stays loaded
DEFAULT_ENGINES = ("qwen", "internvl", "florence")
DRAFT_KEYS = ("draft", "draft_agreement", "draft_engines") + tuple(f"draft_{k}" for k in ENGINES)

# What the large models are told (besides the kit's SYSTEM text and the picture's question).
DRAFT_GUIDE = ("Describe what can be seen, plainly and accurately, for someone who cannot see the picture: what it "
               "is first, then the details that matter (people and what they are doing, objects, colours, the "
               "setting), and read out any text exactly. Say what you cannot make out instead of guessing. Do not "
               "guess who a person is.")
COMBINE_GUIDE = ("Other describers wrote the drafts below for this picture. Some of what they say may be wrong. "
                 "Look at the picture yourself and write ONE accurate description for someone who cannot see it: "
                 "keep what is right, correct what is wrong, add what all of them missed, and read out any text "
                 "exactly. Do not mention the drafts or the describers.")
DRAFT_TOKENS = 350
FLORENCE_TOKENS = 256
AGREE_LOW = 0.25          # drafts agreeing less than this are said to disagree (check those most carefully)

STOP_WORDS = set("""a an the and or but of in on at to for with from by is are was were be been being it its this
that these those there here as into onto over under near next some any one two three which who whom what where when
while has have had having do does did not no very also can could may might appears appear seems seem shows showing
shown image picture photo photograph visible background foreground left right top bottom side""".split())


def say(text=""):
    """Write one line, at once (the program reads the lines as they come)."""
    print(text, flush=True)
    import system_monitor
    system_monitor.note(text)               # the computer-use lines say which model they are about


def plural(count, one, many=None):
    """'1 picture', '2 pictures'."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


# ----------------------------------------------------------------- which pictures

def new_pictures(workspace):
    """The workspace's pictures that are new (no description yet) and still in the folder, in name order."""
    return [n for n in sorted(workspace.pictures, key=str.lower)
            if workspace.entry(n)["status"] == package.NEW and os.path.isfile(workspace.path(n))
            and not package.description(workspace, n)]


def keep_original(workspace, name):
    """Copy a picture into the hidden .originals folder before it is changed (once: the first original is kept)."""
    folder = os.path.join(workspace.folder, ORIGINALS)
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, name)
    if not os.path.exists(target):
        shutil.copy2(workspace.path(name), target)


def save_changed(workspace, name, img):
    """Save a changed picture over the old one (same name and kind) and record its new fingerprint."""
    path = workspace.path(name)
    kind = "PNG" if name.lower().endswith(".png") else "JPEG"
    if kind == "JPEG" and img.mode != "RGB":
        img = img.convert("RGB")
    img.save(path + ".new", kind, **({"quality": 92} if kind == "JPEG" else {}))
    os.replace(path + ".new", path)
    entry = workspace.entry(name)
    entry["hash"] = package.file_hash(path)
    entry["changed_at"] = package.now()


def open_upright(path):
    """A picture as RGB, turned the right way up (phone photos say how they were held)."""
    from PIL import Image, ImageOps
    with Image.open(path) as img:
        return ImageOps.exif_transpose(img).convert("RGB")


# ----------------------------------------------------------------- 1. clean-up

class StillFrame:
    """A still picture dressed as a video frame, so video_frames.OverlayWatch can watch a folder of pictures the
    way it watches a video (it needs width, height, rotation and to_ndarray)."""

    def __init__(self, img):
        """img: a Pillow RGB picture."""
        self.img, self.width, self.height, self.rotation = img, img.width, img.height, 0

    def to_ndarray(self, format="rgb24", width=None, height=None):  # noqa: A002 - PyAV's own argument name
        """The picture as a numpy array at width x height (rgb24 or gray)."""
        import numpy as np
        from PIL import Image
        img = self.img.resize((width or self.width, height or self.height), Image.BILINEAR)
        return np.asarray(img.convert("L") if format == "gray" else img)


def overlay_boxes(texts):
    """The --overlay-box values (x,y,w,h in percent) as boxes (x0, y0, x1, y1, shares of the picture)."""
    import video_frames
    return [video_frames.overlay_box(t) for t in texts or ()]


def clean(workspace, set_aside=True, blur_faces=False, overlays="keep", boxes=()):
    """Clean the workspace's new pictures that were not cleaned before (see the module docstring); returns a plain
    summary."""
    import video_frames as vf
    from PIL import Image
    workspace = package.open_workspace(workspace)
    names = [n for n in new_pictures(workspace) if workspace.entry(n).get("cleaned") != "yes"]
    if not names:
        return "There are no new pictures to clean up: every new picture was cleaned up before."
    say(f"Cleaning up {plural(len(names), 'new picture')}.")
    scores = {}
    for number, name in enumerate(names, 1):
        try:
            img = open_upright(workspace.path(name))
        except Exception as e:  # noqa: BLE001 - a damaged picture is set aside, not a reason to stop
            scores[name] = {"broken": str(e).splitlines()[0][:120] if str(e) else "it cannot be opened"}
            continue
        import numpy as np
        scale = min(1.0, vf.SCORE_SIDE / max(img.size))
        small = img.resize((max(2, int(img.width * scale)), max(2, int(img.height * scale))), Image.BILINEAR)
        gray = np.asarray(small.convert("L"))
        scores[name] = dict(vf.score(gray), size=img.size)
        if number % 50 == 0 or number == len(names):
            say(f"  {number} of {len(names)} pictures looked at")
    tally = {"dark": 0, "blurry": 0, "same": 0, "broken": 0, "stamps": 0, "faces": 0}
    if set_aside:
        tally.update(set_aside_pictures(workspace, names, scores))
    usable = [n for n in names if workspace.entry(n)["status"] == package.NEW]
    lines = []
    if overlays != "keep" or boxes:
        tally["stamps"], lines = remove_overlays(workspace, usable, scores, overlays if overlays != "keep" else
                                                 "fill", boxes)
    if blur_faces:
        tally["faces"] = blur_all_faces(workspace, usable)
    for name in names:
        workspace.entry(name)["cleaned"] = "yes"
    workspace.save()
    kept = sum(1 for n in names if workspace.entry(n)["status"] == package.NEW)
    parts = [f"{plural(kept, 'picture')} kept"]
    for key, words in (("dark", "too dark"), ("blurry", "blurry"), ("same", "the same as another picture"),
                       ("broken", "could not be opened")):
        if tally[key]:
            parts.append(f"{tally[key]} set aside as {words}")
    if tally["stamps"]:
        parts.append(f"date stamps or logos removed from {plural(tally['stamps'], 'picture')}")
    if tally["faces"]:
        parts.append(f"faces blurred in {plural(tally['faces'], 'picture')}")
    text = "Clean-up done: " + ", ".join(parts) + "."
    if any(tally[k] for k in ("dark", "blurry", "same", "broken")):
        text += (" Set-aside pictures are not deleted: in Describe pictures, choose Filter, Set aside, to see them and "
                 "bring one back with Needs another look.")
    if tally["stamps"] or tally["faces"]:
        text += " The originals of changed pictures are in the hidden folder .originals in the workspace."
    for line in lines:
        say("  " + line)
    return text


def set_aside_pictures(workspace, names, scores):
    """Set aside (status "skip", reason in the notes) the broken, dark, blurry and near-identical new pictures.
    Pictures that already have a description are never set aside; of two that look the same, the sharper stays."""
    import video_frames as vf
    tally = {"dark": 0, "blurry": 0, "same": 0, "broken": 0}
    looked = [scores[n] for n in names if "broken" not in scores[n]]
    limit = vf.blur_limit(looked) if looked else vf.SHARP_LEAST

    def aside(name, key, why):
        """Mark one picture set aside."""
        package.set_status(workspace, name, package.SKIP, "Dataset Preparation", f"Set aside by the clean-up: {why}.")
        tally[key] += 1

    kept = {}                    # fingerprint owner -> score, for near-identical pictures
    for name in names:
        s = scores[name]
        if "broken" in s:
            aside(name, "broken", f"it could not be opened ({s['broken']})")
        elif s["bright"] < vf.DARK:
            aside(name, "dark", "too dark to see")
        elif s["sharp"] < limit:
            aside(name, "blurry", "blurry")
    for name in [n for n in names if workspace.entry(n)["status"] == package.NEW]:
        s = scores[name]
        twin = next((other for other, o in kept.items() if vf.distance(o["hash"], s["hash"]) <= vf.SAME_BITS), None)
        if twin is None:
            kept[name] = s
        elif s["sharp"] > kept[twin]["sharp"]:
            aside(twin, "same", f"it looks the same as {name}, which is sharper")
            del kept[twin]
            kept[name] = s
        else:
            aside(name, "same", f"it looks the same as {twin}, which is sharper")
    return tally


def remove_overlays(workspace, names, scores, how, boxes):
    """Find and remove date stamps and logos in groups of pictures of the same size (see the module docstring).
    Returns (how many pictures were changed, report lines)."""
    import video_frames as vf
    groups = {}
    for name in names:
        groups.setdefault(tuple(scores[name]["size"]), []).append(name)
    changed, lines = 0, []
    for number, (size, group) in enumerate(sorted(groups.items(), key=lambda g: -len(g[1])), 1):
        overlays = vf.Overlays(how, boxes)
        if overlays.watch is not None:
            for name in group:
                overlays.watch.add(StillFrame(open_upright(workspace.path(name))))
        overlays.settle()
        label = f"pictures of {size[0]} by {size[1]} ({plural(len(group), 'picture')})"
        line = overlays.report(label)
        if line:
            lines.append(line)
        if overlays.used == "keep":
            continue
        for name in group:
            keep_original(workspace, name)
            save_changed(workspace, name, overlays(open_upright(workspace.path(name))))
            changed += 1
        say(f"  Group {number} of {len(groups)}: {line}")
    return changed, lines


def blur_all_faces(workspace, names):
    """Blur the faces in the given pictures; returns how many pictures had faces."""
    import video_frames as vf
    faces = vf.FaceBlur(say)
    changed = 0
    for number, name in enumerate(names, 1):
        before = faces.faces
        img = faces(open_upright(workspace.path(name)))
        if faces.faces > before:
            keep_original(workspace, name)
            save_changed(workspace, name, img)
            changed += 1
        if number % 50 == 0 or number == len(names):
            say(f"  {number} of {len(names)} pictures checked for faces")
    return changed


# ----------------------------------------------------------------- 2. drafts

def content_words(text):
    """The words of a text that carry meaning (lower case, without the small common ones), as a set."""
    return {w for w in re.findall(r"[a-z0-9']+", (text or "").lower()) if w not in STOP_WORDS and len(w) > 1}


def agreement(drafts):
    """How much the drafts agree, 0 to 1: the average, over each pair, of the share of meaningful words they have
    in common (Jaccard). One draft or none: 1."""
    sets = [content_words(d) for d in drafts if d and d.strip()]
    pairs = [(a, b) for i, a in enumerate(sets) for b in sets[i + 1:]]
    if not pairs:
        return 1.0
    return sum(len(a & b) / len(a | b) if a | b else 1.0 for a, b in pairs) / len(pairs)


def tidy(text):
    """A model's answer as plain text: no markdown marks, single spaces within lines, at most one blank line."""
    text = re.sub(r"(?m)^[ \t]*#+[ \t]*", "", text or "")
    text = re.sub(r"\*\*|__|`", "", text)
    text = re.sub(r"(?m)^[ \t]*[-*][ \t]+", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def finished_addon():
    """(base model key, add-on folder) of the newest finished training in the kit, or None."""
    import train
    state = train.State(WORK)
    runs = train.finished_runs(WORK, state)
    if not runs:
        return None
    run, final = runs[-1]
    return ("8b" if run.startswith("8b") else "4b"), final


def download(repo, revision, name):
    """Download a pinned model (once; carried on if stopped) into the kit's work folder; returns the folder."""
    from huggingface_hub import snapshot_download
    folder = os.path.join(WORK, "draft-models", repo.replace("/", "--"))
    say(f"  Getting {name} ready (downloaded once, then kept in the kit's work folder).")
    snapshot_download(repo, revision=revision, local_dir=folder)
    return folder


class Engine:
    """One draft model, loaded on the graphics card: describe(picture path, question) -> text."""

    def __init__(self, key):
        """Load the model for key (see ENGINES)."""
        import train
        self.key, self.name = key, ENGINES[key][0]
        self.florence = key == "florence"
        if key == "qwen":
            folder = train.download_model("8b", WORK)
            self.model, self.processor = train.load_model(folder)
        elif key == "yours":
            base, addon = finished_addon()
            folder = train.download_model(base, WORK)
            self.model, self.processor = train.load_model(folder, adapter=addon)
        elif key == "internvl":
            folder = download(ENGINES[key][1], ENGINES[key][2], self.name)
            self.model, self.processor = train.load_model(folder)
        else:
            import torch
            from transformers import AutoModelForImageTextToText, AutoProcessor
            folder = download(ENGINES[key][1], ENGINES[key][2], self.name)
            self.model = AutoModelForImageTextToText.from_pretrained(folder, dtype=torch.float16).to("cuda").eval()
            self.processor = AutoProcessor.from_pretrained(folder)

    def ask(self, img, text, system):
        """The model's answer to text about img (a Pillow picture), greedy, at most DRAFT_TOKENS."""
        import torch
        conversation = [{"role": "system", "content": [{"type": "text", "text": system}]},
                        {"role": "user", "content": [{"type": "image", "image": img}, {"type": "text", "text": text}]}]
        inputs = self.processor.apply_chat_template(conversation, tokenize=True, return_dict=True,
                                                    add_generation_prompt=True, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=DRAFT_TOKENS, do_sample=False)
        return self.processor.decode(out[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()

    def florence_task(self, img, task):
        """One Florence-2 task (<MORE_DETAILED_CAPTION>, <OCR>) on img; returns its text."""
        import torch
        inputs = self.processor(text=task, images=img, return_tensors="pt").to("cuda", torch.float16)
        with torch.no_grad():
            out = self.model.generate(input_ids=inputs["input_ids"], pixel_values=inputs["pixel_values"],
                                      max_new_tokens=FLORENCE_TOKENS, num_beams=3, do_sample=False)
        raw = self.processor.batch_decode(out, skip_special_tokens=False)[0]
        answer = self.processor.post_process_generation(raw, task=task, image_size=img.size)
        return str(answer.get(task, "") if isinstance(answer, dict) else answer).replace("<pad>", "").strip()

    def describe(self, path, question):
        """A draft description of the picture at path for the question."""
        import train
        img = open_upright(path)
        img.thumbnail((1536, 1536))
        if self.florence:
            caption = self.florence_task(img, "<MORE_DETAILED_CAPTION>")
            text = re.sub(r"\s+", " ", self.florence_task(img, "<OCR>")).strip()
            return caption + (f" Text in the picture: {text}" if len(content_words(text)) >= 2 else "")
        if self.key == "yours":                    # your describer answers the way it was trained
            return train.describe(self.model, self.processor, {"picture": path, "question": question}, "cuda")
        return self.ask(img, f"{question} {DRAFT_GUIDE}", train.SYSTEM)

    def combine(self, path, question, drafts):
        """One starting description from the picture and the drafts (only the qwen engine is asked)."""
        import train
        img = open_upright(path)
        img.thumbnail((1536, 1536))
        listed = "\n\n".join(f"Draft {i}: {d}" for i, d in enumerate(drafts, 1))
        return self.ask(img, f"{question} {COMBINE_GUIDE}\n\n{listed}", train.SYSTEM)

    def close(self):
        """Let the model go and give its graphics card memory back."""
        import train
        del self.model, self.processor
        train.free()


def write_drafts(workspace, engines=DEFAULT_ENGINES, combine=True, redo=False):
    """Draft descriptions for the workspace's new pictures (see the module docstring); returns a plain summary."""
    try:
        import torch
    except ImportError:
        return "STOPPED: the training tools are not installed in the kit yet. Start the kit once, then try again."
    if not torch.cuda.is_available():
        return "STOPPED: drafts need the NVIDIA graphics card, and it cannot be used now."
    workspace = package.open_workspace(workspace)
    names = new_pictures(workspace)
    if not names:
        return "There are no new pictures without a description, so no drafts are needed."
    engines = [e for e in ENGINE_ORDER if e in engines]
    if "yours" in engines and finished_addon() is None:
        say("Your own trained describer is left out: no training has finished in this kit yet.")
        engines.remove("yours")
    if not engines:
        return "STOPPED: no draft model was chosen."
    if redo:
        for name in names:
            for key in DRAFT_KEYS:
                workspace.entry(name).pop(key, None)
    say(f"Writing drafts for {plural(len(names), 'picture')} with {plural(len(engines), 'model')}: "
        + ", ".join(ENGINES[e][0] for e in engines) + ". Each model is loaded once and describes every picture.")
    engine = None
    for step, key in enumerate(engines, 1):
        todo = [n for n in names if not workspace.entry(n).get(f"draft_{key}")]
        if not todo:
            say(f"Model {step} of {len(engines)}: {ENGINES[key][0]} has written all its drafts before.")
            continue
        say(f"Model {step} of {len(engines)}: {ENGINES[key][0]} ({ENGINES[key][4]}).")
        if engine is not None:
            engine.close()
        try:
            engine = Engine(key)
        except Exception as e:  # noqa: BLE001 - one model that cannot be loaded does not stop the others
            say(f"  {ENGINES[key][0]} could not be loaded ({str(e).splitlines()[0][:200] if str(e) else e!r}); "
                "its drafts are left out this time.")
            engine = None
            continue
        for number, name in enumerate(todo, 1):
            try:
                text = tidy(engine.describe(workspace.path(name), package.question_of(workspace, name)))
            except Exception as e:  # noqa: BLE001 - one picture that fails does not stop the rest
                say(f"  {name} could not be described by {ENGINES[key][0]}: {str(e).splitlines()[0][:150]}")
                text = ""
            if text:
                workspace.entry(name)[f"draft_{key}"] = text
            if number % 10 == 0 or number == len(todo):
                workspace.save()
                say(f"  {number} of {len(todo)} pictures: drafts by {ENGINES[key][0]}")
    combined = 0
    if combine:
        wanted = [n for n in names if len(drafts_of(workspace.entry(n))) > 1 and not workspace.entry(n).get("draft")]
        if wanted:
            say(f"Combining the drafts of {plural(len(wanted), 'picture')} into one starting description each "
                "(Qwen3-VL 8B looks at each picture again).")
            if engine is None or engine.key != "qwen":
                if engine is not None:
                    engine.close()
                try:
                    engine = Engine("qwen")
                except Exception as e:  # noqa: BLE001 - said in plain words; the separate drafts are still there
                    say(f"  Qwen3-VL 8B could not be loaded ({str(e).splitlines()[0][:200]}); the drafts are not "
                        "combined, and the best single draft is used instead.")
                    engine = None
            for number, name in enumerate(wanted if engine is not None else (), 1):
                entry = workspace.entry(name)
                try:
                    entry["draft"] = tidy(engine.combine(workspace.path(name), package.question_of(workspace, name),
                                                         list(drafts_of(entry).values())))
                    combined += 1
                except Exception as e:  # noqa: BLE001
                    say(f"  The drafts of {name} could not be combined: {str(e).splitlines()[0][:150]}")
                if number % 10 == 0 or number == len(wanted):
                    workspace.save()
                    say(f"  {number} of {len(wanted)} pictures: drafts combined")
    if engine is not None:
        engine.close()
    disagree = 0
    for name in names:
        entry = workspace.entry(name)
        drafts = drafts_of(entry)
        if not drafts:
            continue
        entry["draft_engines"] = ",".join(drafts)
        score = agreement(list(drafts.values()))
        entry["draft_agreement"] = f"{score:.2f}"
        disagree += score < AGREE_LOW and len(drafts) > 1
        if not entry.get("draft"):
            entry["draft"] = best_single(drafts)
    workspace.save()
    drafted = sum(1 for n in names if workspace.entry(n).get("draft"))
    return (f"Drafts are ready for {plural(drafted, 'picture')}"
            + (f" ({combined} combined from several models)" if combined else "")
            + (f"; the drafts of {plural(disagree, 'picture')} disagree a lot, so check those most carefully "
               "(Describe pictures, Filter: Drafts that disagree first)" if disagree else "")
            + ". Nothing is used for training until a person checks and saves each description.")


def drafts_of(entry):
    """{engine key: draft} of an entry's drafts, in ENGINE_ORDER."""
    return {k: entry[f"draft_{k}"] for k in ENGINE_ORDER if entry.get(f"draft_{k}")}


def best_single(drafts):
    """The starting description when the drafts were not combined: the one sharing the most with the others (the
    most agreed-on), or the longest when there is only one."""
    if len(drafts) == 1:
        return next(iter(drafts.values()))
    return max(drafts.values(), key=lambda d: (agreement([d] + [o for o in drafts.values() if o != d]), len(d)))


# ----------------------------------------------------------------- the self-test and the command line

def self_test():
    """Check the parts that do not need a graphics card: agreement, tidy, the clean-up of a small made-up
    workspace (dark, blurry and repeated pictures are set aside, described ones never)."""
    import tempfile

    import numpy as np
    from PIL import Image, ImageDraw
    assert agreement(["A red bus on a street.", "A red bus parked on a street."]) > 0.5
    assert agreement(["A cat asleep on a sofa.", "A bowl of soup."]) < 0.1
    assert tidy("## Title\n**A** red `bus`\n\n\n\n- one") == "Title\nA red bus\n\none"
    with tempfile.TemporaryDirectory() as folder:
        space = package.make_workspace(folder, "Self-test")
        rng = np.random.default_rng(3)
        for i in range(6):
            img = Image.fromarray((rng.random((240, 320, 3)) * 255).astype("uint8"))
            ImageDraw.Draw(img).rectangle((20 + i * 30, 40, 80 + i * 30, 120), fill=(250, 250, 0))
            img.save(os.path.join(folder, f"sharp{i}.jpg"), quality=95)
        Image.new("RGB", (320, 240), (5, 5, 5)).save(os.path.join(folder, "dark.jpg"))
        Image.new("RGB", (320, 240), (128, 128, 128)).save(os.path.join(folder, "blurry.jpg"))
        Image.open(os.path.join(folder, "sharp0.jpg")).save(os.path.join(folder, "again.png"))
        with open(os.path.join(folder, "sharp5.txt"), "w", encoding="utf-8") as f:
            f.write("A described picture.")
        package.register_new(space)
        summary = clean(folder)
        space = package.open_workspace(folder)
        status = {n: space.entry(n)["status"] for n in space.pictures}
        assert status["dark.jpg"] == package.SKIP and status["blurry.jpg"] == package.SKIP, (status, summary)
        assert [status["again.png"], status["sharp0.jpg"]].count(package.SKIP) == 1, (status, summary)
        assert status["sharp5.jpg"] == package.DESCRIBED and status["sharp1.jpg"] == package.NEW, status
        entry = space.entry("sharp1.jpg")
        entry.update(draft_qwen="A red box.", draft_florence="A red box on noise.")
        assert best_single(drafts_of(entry))
    say("Self-test passed.")


def main(argv=None):
    """The command line (see the module docstring)."""
    if argv is None:
        argv = sys.argv[1:]
    if argv[:1] == ["--self-test"]:
        self_test()
        return 0
    parser = argparse.ArgumentParser(description="Get a describing workspace ready for review.")
    parser.add_argument("workspace", help="the describing workspace folder")
    parser.add_argument("job", choices=("clean", "drafts", "all"))
    parser.add_argument("--no-set-aside", action="store_true", help="keep dark, blurry and repeated pictures")
    parser.add_argument("--blur-faces", action="store_true")
    parser.add_argument("--overlays", choices=("keep", "crop", "fill"), default="keep")
    parser.add_argument("--overlay-box", action="append", default=[], help="x,y,w,h in percent")
    parser.add_argument("--engines", default=",".join(DEFAULT_ENGINES))
    parser.add_argument("--no-combine", action="store_true")
    parser.add_argument("--redo", action="store_true", help="write the drafts again, also those written before")
    args = parser.parse_args(argv)
    import system_monitor
    system_monitor.start(say)                 # computer use into the logs every 5 minutes (system_monitor.py)
    try:
        if not package.is_workspace(args.workspace):
            package.make_workspace(args.workspace)
        say(package.register_new(args.workspace))
        if args.job in ("clean", "all"):
            say(clean(args.workspace, not args.no_set_aside, args.blur_faces, args.overlays,
                      overlay_boxes(args.overlay_box)))
        if args.job in ("drafts", "all"):
            engines = [e.strip() for e in args.engines.split(",") if e.strip() in ENGINES]
            text = write_drafts(args.workspace, engines, not args.no_combine, args.redo)
            say(text)
            if text.startswith("STOPPED"):
                return 1
    except Exception as e:  # noqa: BLE001 - said in plain words
        say(f"STOPPED: {str(e).splitlines()[0][:300] if str(e) else type(e).__name__}")
        return 1
    say("Finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
