"""Picture Model Training Kit, picture-making part: teach a Stable Diffusion model (SDXL or SD 1.5) to draw pictures
from plain descriptions, by training a small add-on (a LoRA) on the described pictures of the kit's picture library,
on your own computer's NVIDIA graphics card.

Every step says what it does in plain words, on the screen and in training-log.txt (train.py's say()). A finished
step is not done again: if the computer restarts or the window is closed, start it again and it carries on where it
stopped (the training itself from its last save).

The steps (numbered like train.py's, so the wizard's progress bar works the same way):
  1. check the graphics card and the free disk space;
  2. download the base model from Hugging Face (only the files needed, in half-size form where offered; no login),
     for SDXL also the fp16-fix VAE, and the CLIP model used to score the test;
  3. read the described pictures of the chosen collections from the picture library (preparing any collection that
     is not there yet, as train.py does), keep only real DESCRIPTIONS (not short answers, not other languages, not
     safety advice), leave out every picture of a child (marked "child", or whose question or answer mentions a
     child: CHILD_WORDS; library and own pictures alike; counted in the log and the report), and shorten each to
     the 77 words-pieces the model reads; some are kept back for the test;
  4. turn every training picture into the model's compressed form (latents) and every description into the model's
     text form (embeddings), once, kept on disk; then make the test pictures with the base model ("before");
  5. train the add-on (LoRA rank 32 on the attention layers of the UNet), saving every so often;
  6. make the test pictures again with the add-on ("after") and score both sets with CLIP;
  7. write the report and put the add-on (Kohya/ComfyUI/Automatic1111 form, diffusers form, and the folder laid out
     for Accessible AI Studio: "Accessible AI Studio\trained-<name>" with trained.json), the test pictures,
     REPORT.txt, ATTRIBUTION.txt and HOW TO USE.txt in one zip in the "result" folder.

Command line:
  python train_pictures.py --base {sd15,sdxl} --library FOLDER --size {quick,normal,full} [--with-wikipedia]
                           [--with-nudity] [--with-medical] [--own FOLDER] [--own-only] [--limit N] [--work FOLDER]
                           [--personal-noncommercial] [--personal-research --accept-research-terms]

Review collections (review_sources.py, adult_review_sources.py) are NEVER used here: no picture of a review-only
"Describe pictures" workspace (own_data.check_folder with review=False), no picture or collection tagged "intimate" or
"sexual" (sources.PICTURE_MAKING_NEVER), whatever is chosen; there is no --review or --with-sexual option here.
never_for_review() is the last check, on every row, before a picture is learned from.

Graphic scenes (war, disasters, injuries and death) are NEVER used here either: no collection or row tagged "graphic"
(sources.PICTURE_MAKING_NEVER; never_for_review checks every row's "content"), none of the graphic-scenes packs at all
(sources.NOT_FOR_PICTURE_MAKING), and there is no --with-graphic option.

Personal-use collections (--personal-noncommercial, --personal-research): as in train.py, the add-on is then for
PERSONAL USE ONLY (its name gets "-personal"; REPORT.txt starts with the warning; ATTRIBUTION.txt lists them under their
own heading; the zip gets PERSONAL-USE-ONLY.txt). Only those whose keys are in personal_sources.py's
PERSONAL_PICTURE_MAKING_OK are used for picture-making.

Hidden options for the kit's own tests (tiny models on a computer without a graphics card): --base-repo REPO,
--clip-repo REPO, --steps N.
"""

import argparse
import contextlib
import datetime
import hashlib
import json
import math
import os
import random
import re
import shutil
import sys
import time
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sources  # noqa: E402 - the collections, beside this file
import train  # noqa: E402 - the describer's trainer: its library, logging, state and attribution are reused
from train import HERE, State, duration, free, keep_awake, say, stop  # noqa: E402

# The base models: ungated on Hugging Face (no login), pinned to a commit like train.py's MODELS.
BASES = {
    "sdxl": {
        "name": "Stable Diffusion XL base 1.0", "repo": "stabilityai/stable-diffusion-xl-base-1.0",
        "revision": "462165984030d82259a11f4367a4eed129e94a7b",
        "vae": ("madebyollin/sdxl-vae-fp16-fix", "207b116dae70ace3637169f1ddd2434b91b3a8cd"),
        "licence": "CreativeML Open RAIL++-M (huggingface.co/stabilityai/stable-diffusion-xl-base-1.0, LICENSE.md)",
        "steps": {"quick": 500, "normal": 4000, "full": 12000}, "batch": 1, "accumulate": 2, "save_every": 250,
        "seconds": 2.8, "memory": 12, "disk": 25, "download": "about 7 GB", "guidance": 7.0,
        "kohya": ("sdxl_base_v1-0", "stable-diffusion-xl-v1-base/lora"),
    },
    "sd15": {
        "name": "Stable Diffusion 1.5", "repo": "stable-diffusion-v1-5/stable-diffusion-v1-5",
        "revision": "451f4fe16113bff5a5d2269ed5ad43b0592e9a14", "vae": None,
        "licence": "CreativeML Open RAIL-M (huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5, LICENSE)",
        "steps": {"quick": 400, "normal": 3000, "full": 9000}, "batch": 4, "accumulate": 1, "save_every": 500,
        "seconds": 0.7, "memory": 8, "disk": 15, "download": "about 2 GB", "guidance": 7.5,
        "kohya": ("sd_v1", "stable-diffusion-v1/lora"),
    },
}
CLIP = ("openai/clip-vit-large-patch14", "32bd64288804d66eefd0ccbe215aa642df71cc41")    # MIT, for the test score
RANK = 32                      # LoRA rank; alpha is the same, so the add-on's strength is 1 in every program
RATE = 1e-4
SNR_GAMMA = 5.0                # min-SNR weighting of the loss
TARGETS = ["to_k", "to_q", "to_v", "to_out.0"]      # the UNet's attention layers
TEST_COUNT = 12
TEST_STEPS = 25
SEED = 7
SAY_EVERY = 60                 # seconds between progress lines
LICENCE_NOTE = ("The base model's licence has use restrictions (its Attachment A: no unlawful use, no harm to "
                "people, no deceiving people with made-up pictures of real ones ...). They apply to this add-on and "
                "to every picture made with it, and must be passed on to anyone who gets it.")


# ----------------------------------------------------------------- 3. the descriptions

DESCRIBE_QUESTION = re.compile(r"^(describe (this|the) (picture|photo|photograph|image)|write a short description)",
                               re.IGNORECASE)
YES_NO_QUESTION = re.compile(r"^(is|are|was|were|does|do|did|can|could|will|should|has|have)\b", re.IGNORECASE)
SHORT_ANSWER = re.compile(r"^(yes|no|maybe|probably|not sure|unanswerable|unsuitable|i can't|i cannot)\b",
                          re.IGNORECASE)
SAFETY = re.compile(r"^(do not|don't|never|always|please|ask (a|your)|check (the|its|it)|consult|seek|be careful|"
                    r"if (in doubt|unsure|you are unsure)|to be (safe|sure)|throw (it|them) away)\b", re.IGNORECASE)
COMMON = set("the a an of and in on with is are to at by for from it this that its his her their there two three one "
             "some has have near behind front next which who wearing white black red blue green brown small large "
             "man woman people person picture photo image shows showing holding standing sitting".split())
DESCRIPTIVE = set("with in on of wearing holding standing sitting shows showing behind front near against under "
                  "above beside".split())


# Words that show a picture is of a child (whole words, any case). A picture-making model may learn facial
# expressions and body language from adults, but never from pictures of children: a row marked "child" (the
# expression packs set it) or whose question or answer has one of these words is left out, with its picture.
CHILD_WORDS = re.compile(r"\b(child|children|kids?|boys?|girls?|bab(y|ies)|infant|toddler|newborn|teen|teenager|son|"
                         r"daughter|schoolchild|pupil|youngster|little one)\b", re.IGNORECASE)
CHILDREN_NOTE = ("{count} picture{s} that mention children {were} left out: a picture-making model never learns from "
                 "pictures of children.")


def mentions_child(row):
    """True when a row is about a child: marked "child", or its question or answer (caption, description) has a
    child word (CHILD_WORDS)."""
    if row.get("child"):
        return True
    text = " ".join(str(row.get(k) or "") for k in ("question", "answer", "caption", "description"))
    return bool(CHILD_WORDS.search(text))


def children_note(count):
    """The plain sentence about the pictures of children left out (for the log and the report)."""
    return CHILDREN_NOTE.format(count=count, s="" if count == 1 else "s", were="was" if count == 1 else "were")


def sentences(text):
    """The sentences of a text (split after . ! or ? followed by a space)."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def english(text):
    """True when text reads as English: nearly all its letters are plain ASCII ones, and at least a fifth of its words
    are common English words (Dutch, Swedish, Japanese and Chinese descriptions fail one or the other)."""
    letters = [c for c in text if c.isalpha()]
    words = train.words_of(text)
    if not letters or not words:
        return False
    ascii_share = sum(c.isascii() for c in letters) / len(letters)
    return ascii_share >= 0.97 and sum(w in COMMON for w in words) / len(words) >= 0.2


def caption_of(row, own=False):
    """The description of one row to train on, or None when the row is not a description: translated rows, short
    or yes/no answers, other languages, "I can't tell", and questions that are not about how the picture looks.
    Safety advice ("Do not eat it.", "Check the packaging or ask a pharmacist to be sure.") is taken off the end.
    own: the person's own rows, which are trusted to be descriptions (only emptiness is checked)."""
    answer = sources.clean(row.get("answer") or row.get("caption") or row.get("description"))
    question = (row.get("question") or "").strip()
    if not answer or (row.get("split") == "no-test" and not own):        # "no-test": a machine-translated twin
        return None
    if sources.CANNOT_TELL.lower() in answer.lower():
        return None
    kept = [s for s in sentences(answer) if not SAFETY.match(s) and "pharmacist" not in s.lower()]
    text = " ".join(kept).strip()
    count = len(text.split())
    if own:
        return text if count >= 2 else None
    if count < 4 or SHORT_ANSWER.match(text) or text.endswith("?") or not english(text):
        return None
    if DESCRIBE_QUESTION.match(question) or question in (sources.DETAILED, sources.BRIEF, sources.NARRATE,
                                                          sources.ALT_TEXT, sources.READ_TEXT):
        return text
    if count >= 8 and not YES_NO_QUESTION.match(question) and DESCRIPTIVE & set(train.words_of(text)):
        return text
    return None


def fit(text, tokenizer, room=None):
    """text shortened to what the text encoder reads (77 pieces with its start and end marks), or to room pieces
    when given: whole sentences from the start while they fit, or, when even the first sentence is too long, its
    first words."""
    limit = tokenizer.model_max_length - 2 if room is None else room

    def size(t):
        """How many pieces t is."""
        return len(tokenizer(t, add_special_tokens=False).input_ids)
    if size(text) <= limit:
        return text
    out = ""
    for sentence in sentences(text):
        if size((out + " " + sentence).strip()) > limit:
            break
        out = (out + " " + sentence).strip()
    if not out:
        for word in text.split():
            if size((out + " " + word).strip()) > limit:
                break
            out = (out + " " + word).strip()
        out = out.rstrip(",;:")
    return out


# A short "What is this?" answer of a collection whose photos show the place ("This is a kitchen."), used as a
# caption only when the row has a place: "Photo taken in Kenya. A kitchen." teaches what a kitchen in Kenya looks like.
NAMED_THING = re.compile(r"^(this is|these are) (.{3,80}?)\.?$", re.IGNORECASE)


def place_caption(row, own=False):
    """A caption for a row that is not a description but names what a place photo shows (see NAMED_THING), or
    None."""
    if not row.get("place") or (row.get("source") not in getattr(sources, "PLACE_VISIBLE", ())):
        return None
    if (row.get("question") or "") not in ("What is this?", "What kind of place is this?"):
        return None
    m = NAMED_THING.match(sources.clean(row.get("answer")))
    return (m.group(2)[0].upper() + m.group(2)[1:] + ".") if m else None


def with_place(row, caption, tokenizer):
    """The caption to train on, fitted to the 77 pieces, with the row's place: "Photo taken in Kyoto, Japan. <the
    description>" for a photo, "<the description> Made in Japan." for an object (place_kind "origin"), "<the
    description> It shows Kyoto, Japan." for a picture of a place ("depicted"). The place always stays: the
    description is shortened to the room left. A "market" place (the country of the shop that sells a product) is
    left out: it is not where the photo was taken."""
    place = sources.clean(row.get("place")).strip(" ,.")
    if not place or row.get("place_kind") == "market":
        return fit(caption, tokenizer)
    kind = row.get("place_kind") or "photo"
    words = sources.place_words(place) if hasattr(sources, "place_words") else place
    if kind == "origin":
        before, after = "", f"Made in {words}."
    elif kind == "depicted":
        before, after = "", f"It shows {words}."
    else:
        before, after = f"Photo taken in {words}.", ""
    marks = before or after
    room = tokenizer.model_max_length - 2 - len(tokenizer(" " + marks, add_special_tokens=False).input_ids)
    text = fit(caption, tokenizer, room) if room > 0 else ""
    return " ".join(t for t in (before, text, after) if t)


def chosen_sources(args):
    """The collections to use: sources.chosen with the nudity, medical and personal-use choices when this kit's
    sources.py knows them (a newer one), otherwise the older chosen(with_wikipedia). A personal-use collection
    ("noncommercial" or "research") is only used when its key is in PERSONAL_PICTURE_MAKING_OK
    (personal_sources.py); NOT_FOR_PICTURE_MAKING always wins."""
    personal = {"with_noncommercial": getattr(args, "personal_noncommercial", False),
                "with_research": getattr(args, "personal_research", False)}
    try:
        try:
            found = sources.chosen(with_wikipedia=args.with_wikipedia, with_nudity=args.with_nudity,
                                   with_medical=args.with_medical, **personal)
        except TypeError:                                # a sources.py without the personal-use choices
            if any(personal.values()):
                say("  (This kit's list of collections has no personal-use collections yet; they are left out.)")
            found = sources.chosen(with_wikipedia=args.with_wikipedia, with_nudity=args.with_nudity,
                                   with_medical=args.with_medical)
        # Pictures of children (childhood illnesses) help a describer tell a carer what a rash looks like, but a
        # picture-making model must never learn to make pictures of children's bodies: never used here.
        never = set(getattr(sources, "NOT_FOR_PICTURE_MAKING", ()))
        # Personal-use collections only when their terms allow picture-making (PERSONAL_PICTURE_MAKING_OK).
        making_ok = set(getattr(sources, "PERSONAL_PICTURE_MAKING_OK", ()) or ())
        # Intimate, sexual and graphic collections are never for picture-making, whatever is chosen.
        banned = set(getattr(sources, "PICTURE_MAKING_NEVER", REVIEW_NEVER)) | set(REVIEW_NEVER)
        return [s for s in found if s.key not in never and getattr(s, "content", "") not in banned and
                (getattr(s, "group", "") not in ("noncommercial", "research") or s.key in making_ok)]
    except TypeError:
        if args.with_nudity or args.with_medical:
            say("  (This kit's list of collections has no nudity or medical choice yet; they are left out.)")
        return sources.chosen(args.with_wikipedia)


def library_rows(work, args):
    """(training rows, test rows) of every chosen collection, from the picture library. A collection already there at
    any size is read as it is (the biggest there; nothing downloaded); one that is not there is prepared like
    train.py's prepare_data does, and one that cannot be prepared now is said and left out."""
    data_dir = train.data_root(work)
    os.makedirs(data_dir, exist_ok=True)
    bigger = [s for s in sorted(sources.SIZES, key=sources.SIZES.get) if sources.SIZES[s] >= sources.SIZES[args.size]]
    smaller = [s for s in sorted(sources.SIZES, key=sources.SIZES.get, reverse=True) if s not in bigger]
    sizes = bigger[::-1] + smaller                # the biggest prepared first; a smaller one rather than a download
    train_rows, test_rows = [], []
    chosen = chosen_sources(args)
    for number, source in enumerate(chosen, 1):
        size = next((s for s in sizes if os.path.exists(os.path.join(data_dir, f"{source.key}-{s}.jsonl"))), None)
        say(f"  Collection {number} of {len(chosen)}: {source.name}"
            + (" (in the picture library)." if size else f" (downloads {source.download})."))
        try:
            rows, test = sources.prepare_source(source, data_dir, train.downloads_root(work), size or args.size)
        except Exception as e:  # noqa: BLE001 - one collection failing does not stop the others
            say(f"    This collection could not be prepared now ({str(e).splitlines()[0][:200]}); it is left out.")
            continue
        train_rows += rows
        test_rows += test
    return train_rows, test_rows


# The content tags never used here, even with a sources.py older than this file (which may not list them all).
REVIEW_NEVER = ("intimate", "sexual", "graphic")


def never_for_review(row):
    """True for a row that a picture-making model must never learn from: a row of a review collection (it has
    "review", or its source is "review"), one tagged "intimate", "sexual" or "graphic" (its "contents" or
    "content"), or one of a collection whose own content is one of those."""
    tags = set(row.get("contents") or []) | {str(row.get("content") or "").lower()}
    if hasattr(sources, "content_of") and row.get("source"):
        tags.add(sources.content_of(row["source"]))
    never = set(getattr(sources, "PICTURE_MAKING_NEVER", REVIEW_NEVER)) | set(REVIEW_NEVER)
    return bool(row.get("review") or row.get("source") == "review" or tags & never)


def own_rows(folder, args=None):
    """The person's own described pictures (own_data.check_folder, without smaller copies: the pictures are read at
    full size), with its summary and any problems said. Rows marked "test" are kept back for the test. args: the
    command line's choices (its nudity and medical choices allow pictures tagged so; nothing else tagged is used,
    and no picture of a review collection)."""
    try:
        import own_data
    except ImportError:
        stop("This kit cannot read your own pictures yet (own_data.py is missing). Update the kit.")
    if not os.path.isdir(folder):
        stop(f"The folder of your own pictures was not found: {folder}")
    say(f"  Your own pictures: reading {folder}.")
    # Never a review collection's picture, nor an intimate, sexual or graphic one (only nudity and medical when chosen).
    banned = set(getattr(sources, "PICTURE_MAKING_NEVER", REVIEW_NEVER)) | set(REVIEW_NEVER)
    try:
        allowed = sources.allowed_contents(getattr(args, "with_nudity", False),
                                           getattr(args, "with_medical", False)) - banned
        rows, _problems, summary = own_data.check_folder(folder, contents=allowed, review=False)
    except TypeError:                                    # an older own_data.py without the review rules
        rows, _problems, summary = own_data.check_folder(folder)
    rows = [r for r in rows if not never_for_review(r)]
    for line in str(summary or "").splitlines():
        say("    " + line)
    return [dict(r, source="own", picture=r.get("original") or r["picture"]) for r in rows]


def spread(items, count, seed):
    """At most count items taken in turn from each collection (shuffled within each), so small collections are in
    too and no single big one fills the training."""
    rng = random.Random(seed)
    groups = {}
    for item in items:
        groups.setdefault(item["source"], []).append(item)
    for group in groups.values():
        rng.shuffle(group)
    out, lists = [], [groups[k] for k in sorted(groups)]
    while len(out) < count and any(lists):
        for group in lists:
            if group and len(out) < count:
                out.append(group.pop())
    return out


def choose_items(train_rows, test_rows, mine, tokenizer, args, wanted):
    """(training items, test items, how many pictures of children were left out), each item {"picture", "caption",
    "source"}: the descriptions of the library's rows (and the person's own), shortened to fit. The test captions come
    from the collections' test pictures (or, with --own-only, a few of the person's own kept back); the training items
    are the person's own first, then the library's spread over the collections, up to wanted (and --limit).
    Every picture with a row about a child (mentions_child), in the library or the person's own, is left out
    altogether, whatever its other rows say."""
    children = {r.get("picture") for r in [*train_rows, *test_rows, *mine] if mentions_child(r)}
    # The last check: never a review collection's picture, nor an intimate, sexual or graphic one.
    train_rows, test_rows, mine = ([r for r in rows if not never_for_review(r)] for rows in (train_rows, test_rows,
                                                                                               mine))

    def items_of(rows, own=False):
        """The rows that are descriptions (and not of a picture of a child), as items."""
        out = []
        for row in rows:
            if row.get("picture") in children:
                continue
            caption = caption_of(row, own) or place_caption(row, own)
            if caption and row.get("picture"):
                item = {"picture": row["picture"], "caption": with_place(row, caption, tokenizer),
                        "source": row["source"]}
                if row.get("place") and row.get("place_kind") != "market":     # a shop's country is not taught
                    item["place"] = row["place"]
                out.append(item)
        return out
    own_items = items_of([r for r in mine if r.get("split") != "test"], own=True)
    if args.own_only:
        tests = spread(items_of([r for r in mine if r.get("split") == "test"], own=True), TEST_COUNT, SEED)
        tests = tests or own_items[:1]                    # one or two pictures: test on one of them
        training = own_items
    else:
        library = items_of(train_rows)
        tests = spread(items_of(test_rows), TEST_COUNT, SEED)
        if len(tests) < TEST_COUNT:                       # too few test descriptions: keep some training ones back
            extra = spread(library, TEST_COUNT - len(tests), SEED + 1)
            tests += extra
            library = [i for i in library if i not in extra]
        tested = {t["picture"] for t in tests}
        library = [i for i in library if i["picture"] not in tested]    # no test picture is trained on
        training = own_items + spread(library, max(0, wanted - len(own_items)), SEED)
    random.Random(SEED + 2).shuffle(training)
    if args.limit:
        training = training[:args.limit]
    return training, tests, len(children)


# ----------------------------------------------------------------- 2. the models

def slug(text):
    """A folder-safe form of a repository name."""
    return re.sub(r"[^\w.-]+", "-", text).strip("-")


def download(repo, revision, folder, components=("unet", "vae", "text_encoder", "text_encoder_2")):
    """Download only the files a pipeline needs (configs, tokenizers, the scheduler, and one weight file of each part:
    half size when offered, safetensors before .bin) into folder; returns {part: variant} ("fp16" or None), kept in
    folder/kit-variants.json so a restart does not ask Hugging Face again."""
    from huggingface_hub import HfApi, snapshot_download
    remembered = os.path.join(folder, "kit-variants.json")
    if os.path.exists(remembered):
        with open(remembered, encoding="utf-8") as f:
            return json.load(f)
    files = set(HfApi().list_repo_files(repo, revision=revision))
    patterns, variants = ["model_index.json", "scheduler/*", "tokenizer/*", "tokenizer_2/*"], {}
    for part in components:
        stem, old = ("diffusion_pytorch_model",) * 2 if part in ("unet", "vae") else ("model", "pytorch_model")
        for name, variant in ((f"{stem}.fp16.safetensors", "fp16"), (f"{stem}.safetensors", None),
                              (f"{old}.fp16.bin", "fp16"), (f"{old}.bin", None)):
            if f"{part}/{name}" in files:
                patterns += [f"{part}/config.json", f"{part}/{name}"]
                variants[part] = variant
                break
    snapshot_download(repo, revision=revision, local_dir=folder, allow_patterns=patterns)
    with open(remembered, "w", encoding="utf-8") as f:
        json.dump(variants, f)
    return variants


def download_single(repo, revision, folder, weights):
    """Download one model kept as config files plus one weight file (the first of weights the repository has)."""
    from huggingface_hub import HfApi, snapshot_download
    if os.path.exists(os.path.join(folder, "kit-done.txt")):
        return folder
    files = set(HfApi().list_repo_files(repo, revision=revision))
    name = next(w for w in weights if w in files)
    snapshot_download(repo, revision=revision, local_dir=folder, allow_patterns=["*.json", "*.txt", name])
    with open(os.path.join(folder, "kit-done.txt"), "w", encoding="utf-8") as f:
        f.write(name)
    return folder


class Base:
    """The base model on disk: its folder, which parts are half size, its VAE (the fp16-fix one for SDXL), whether it
    is SDXL, and its picture size."""

    def __init__(self, key, folder, variants, vae_folder):
        """Read the configs to know the picture size (sample size times the VAE's shrink) and the buckets."""
        self.key, self.folder, self.variants, self.vae_folder = key, folder, variants, vae_folder
        self.sdxl = "text_encoder_2" in variants
        with open(os.path.join(folder, "unet", "config.json"), encoding="utf-8") as f:
            unet = json.load(f)
        with open(os.path.join(folder, "vae", "config.json"), encoding="utf-8") as f:
            vae = json.load(f)
        shrink = 2 ** (len(vae["block_out_channels"]) - 1)
        self.resolution = unet["sample_size"] * shrink
        multiple = shrink * 2 ** (len(unet["block_out_channels"]) - 1)
        self.buckets = make_buckets(self.resolution, max(multiple, 64) if self.resolution >= 512 else multiple)

    def vae(self, dtype):
        """The VAE (the fp16-fix one for SDXL)."""
        from diffusers import AutoencoderKL
        if self.vae_folder:
            return AutoencoderKL.from_pretrained(self.vae_folder, torch_dtype=dtype)
        return AutoencoderKL.from_pretrained(self.folder, subfolder="vae", variant=self.variants["vae"],
                                             torch_dtype=dtype)

    def unet(self, dtype):
        """The UNet."""
        from diffusers import UNet2DConditionModel
        return UNet2DConditionModel.from_pretrained(self.folder, subfolder="unet", variant=self.variants["unet"],
                                                    torch_dtype=dtype)

    def text(self, dtype):
        """([tokenizers], [text encoders]): one of each for SD 1.5, two for SDXL (the second with its projection)."""
        from transformers import CLIPTextModel, CLIPTextModelWithProjection, CLIPTokenizer
        tokenizers = [CLIPTokenizer.from_pretrained(self.folder, subfolder="tokenizer")]
        encoders = [CLIPTextModel.from_pretrained(self.folder, subfolder="text_encoder",
                                                  variant=self.variants["text_encoder"], dtype=dtype)]
        if self.sdxl:
            tokenizers.append(CLIPTokenizer.from_pretrained(self.folder, subfolder="tokenizer_2"))
            encoders.append(CLIPTextModelWithProjection.from_pretrained(
                self.folder, subfolder="text_encoder_2", variant=self.variants["text_encoder_2"], dtype=dtype))
        return tokenizers, encoders

    def pipeline(self, device, dtype):
        """A picture-making pipeline of the base model (no safety checker: the kit runs locally for the owner)."""
        from diffusers import DPMSolverMultistepScheduler, StableDiffusionPipeline, StableDiffusionXLPipeline
        tokenizers, encoders = self.text(dtype)
        scheduler = DPMSolverMultistepScheduler.from_pretrained(self.folder, subfolder="scheduler")
        if self.sdxl:
            pipe = StableDiffusionXLPipeline(vae=self.vae(dtype), text_encoder=encoders[0],
                                             text_encoder_2=encoders[1], tokenizer=tokenizers[0],
                                             tokenizer_2=tokenizers[1], unet=self.unet(dtype), scheduler=scheduler)
        else:
            pipe = StableDiffusionPipeline(vae=self.vae(dtype), text_encoder=encoders[0], tokenizer=tokenizers[0],
                                           unet=self.unet(dtype), scheduler=scheduler, safety_checker=None,
                                           feature_extractor=None, requires_safety_checker=False)
        pipe.set_progress_bar_config(disable=True)
        return pipe.to(device)


def make_buckets(resolution, multiple):
    """The picture shapes trained on, (width, height): square and six others (landscape and portrait) of about the
    same area as resolution x resolution, rounded to multiple pixels."""
    out = []
    for ratio in (1.0, 9 / 7, 7 / 9, 19 / 13, 13 / 19, 7 / 4, 4 / 7):
        shape = tuple(max(multiple, round(resolution * r / multiple) * multiple)
                      for r in (math.sqrt(ratio), 1 / math.sqrt(ratio)))
        if shape not in out:
            out.append(shape)
    return out


def bucket_for(width, height, buckets):
    """The bucket whose shape is closest to a picture's."""
    return min(buckets, key=lambda b: abs(math.log(width / height) - math.log(b[0] / b[1])))


# ----------------------------------------------------------------- 4. latents and embeddings, once

def picture_path(path, base):
    """The picture to use: for SDXL the library's larger copy when there is one (the training copies are at most 896
    pixels), otherwise the training copy."""
    larger = sources.archive_path(path) if base.resolution > sources.LONG_SIDE else None
    return larger if larger and os.path.exists(larger) else path


def picture_tensor(path, bucket):
    """(the picture as a tensor from -1 to 1, scaled to cover bucket and cut in the middle, (original height, width,
    crop top, crop left)) for SDXL's size conditioning."""
    import numpy as np
    import torch
    from PIL import Image, ImageOps
    with Image.open(path) as opened:
        img = ImageOps.exif_transpose(opened).convert("RGB")
    width, height = img.size
    scale = max(bucket[0] / width, bucket[1] / height)
    size = (max(bucket[0], round(width * scale)), max(bucket[1], round(height * scale)))
    img = img.resize(size, Image.LANCZOS)
    left, top = (size[0] - bucket[0]) // 2, (size[1] - bucket[1]) // 2
    img = img.crop((left, top, left + bucket[0], top + bucket[1]))
    pixels = torch.from_numpy(np.asarray(img).copy()).permute(2, 0, 1).float() / 127.5 - 1
    return pixels, (height, width, top, left)


def key_of(*parts):
    """A short file name for a picture or a description (stable across restarts)."""
    return hashlib.sha1("|".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:24]


def cache(items, base, cache_dir, device, dtype):
    """Turn every item's picture into latents and its description into embeddings, kept in cache_dir (latents/,
    text/) so a restart does not do them again; returns the items that could be read, each with "latent", "text"
    and "bucket". Pictures too small for the base model (under a quarter of its area) or unreadable are left out."""
    import torch
    from PIL import Image
    from safetensors.torch import save_file
    lat_dir, txt_dir = os.path.join(cache_dir, "latents"), os.path.join(cache_dir, "text")
    os.makedirs(lat_dir, exist_ok=True)
    os.makedirs(txt_dir, exist_ok=True)
    vae, ready, started, last_said = None, [], time.time(), time.time()
    for number, item in enumerate(items, 1):
        path = picture_path(item["picture"], base)
        try:
            with Image.open(path) as img:
                width, height = img.size
                if img.getexif().get(0x0112) in (5, 6, 7, 8):          # turned on its side by its EXIF mark
                    width, height = height, width
        except Exception:  # noqa: BLE001 - a missing or damaged picture is left out
            continue
        bucket = bucket_for(width, height, base.buckets)
        if width * height < bucket[0] * bucket[1] / 4:
            continue
        name = key_of(path, bucket) + ".safetensors"
        target = os.path.join(lat_dir, name)
        if not os.path.exists(target):
            if vae is None:
                vae = base.vae(dtype).to(device).eval()
            try:
                pixels, info = picture_tensor(path, bucket)
            except Exception:  # noqa: BLE001
                continue
            with torch.no_grad():
                latent = vae.encode(pixels[None].to(device, dtype)).latent_dist.sample().float()[0]
            latent = latent * vae.config.scaling_factor
            save_file({"latent": latent.half().contiguous().cpu(), "info": torch.tensor(info, dtype=torch.int32)},
                      target + ".part")
            os.replace(target + ".part", target)
        ready.append(dict(item, latent=name, bucket=list(bucket), text=key_of(item["caption"]) + ".safetensors"))
        if time.time() - last_said > SAY_EVERY:
            last_said = time.time()
            per = (time.time() - started) / number
            say(f"    {number} of {len(items)} pictures prepared; about {duration(per * (len(items) - number))} left")
    del vae
    free()
    say(f"    All {len(ready)} pictures are prepared. Now the descriptions.")
    tokenizers, encoders = base.text(dtype)
    encoders = [e.to(device).eval() for e in encoders]
    for item in ready:
        target = os.path.join(txt_dir, item["text"])
        if os.path.exists(target):
            continue
        hidden, pooled = encode_text(item["caption"], tokenizers, encoders, base.sdxl, device)
        tensors = {"hidden": hidden.half().contiguous().cpu()}
        if pooled is not None:
            tensors["pooled"] = pooled.half().contiguous().cpu()
        save_file(tensors, target + ".part")
        os.replace(target + ".part", target)
    del encoders
    free()
    return ready


def encode_text(caption, tokenizers, encoders, sdxl, device):
    """(the text embeddings (77 x width), the pooled embedding for SDXL or None), as the diffusers pipelines make
    them: SD 1.5 the last layer; SDXL the second-to-last layer of both encoders side by side, and the second
    encoder's pooled output."""
    import torch
    hidden, pooled = [], None
    with torch.no_grad():
        for tokenizer, encoder in zip(tokenizers, encoders):
            ids = tokenizer(caption, padding="max_length", max_length=tokenizer.model_max_length, truncation=True,
                            return_tensors="pt").input_ids.to(device)
            out = encoder(ids, output_hidden_states=True)
            hidden.append(out.hidden_states[-2] if sdxl else out[0])
            pooled = out[0] if sdxl else None
    return torch.cat(hidden, dim=-1)[0].float(), (pooled[0].float() if pooled is not None else None)


# ----------------------------------------------------------------- 5. training

def plan_batches(items, batch, count, seed):
    """count batches of item numbers, each from one bucket (one picture shape), in a shuffled order that is the same
    every time (so a restarted training carries on with the same pictures); new passes are added as needed."""
    out, epoch = [], 0
    while len(out) < count:
        rng = random.Random(f"{seed}-{epoch}")
        order = list(range(len(items)))
        rng.shuffle(order)
        groups = {}
        for index in order:
            groups.setdefault(tuple(items[index]["bucket"]), []).append(index)
        batches = [g[k:k + batch] for g in groups.values() for k in range(0, len(g), batch)]
        rng.shuffle(batches)
        out += batches
        epoch += 1
    return out[:count]


def load_batch(items, numbers, cache_dir, base, device, dtype):
    """(latents, text embeddings, extra conditioning for SDXL or None) of a batch, from the cache."""
    import torch
    from safetensors.torch import load_file
    latents, hidden, pooled, time_ids = [], [], [], []
    for number in numbers:
        item = items[number]
        lat = load_file(os.path.join(cache_dir, "latents", item["latent"]))
        txt = load_file(os.path.join(cache_dir, "text", item["text"]))
        latents.append(lat["latent"])
        hidden.append(txt["hidden"])
        if base.sdxl:
            pooled.append(txt["pooled"])
            h, w, top, left = lat["info"].tolist()
            time_ids.append(torch.tensor([h, w, top, left, item["bucket"][1], item["bucket"][0]], dtype=torch.float32))
    latents = torch.stack(latents).to(device, torch.float32)
    hidden = torch.stack(hidden).to(device, dtype)
    extra = None
    if base.sdxl:
        extra = {"text_embeds": torch.stack(pooled).to(device, dtype),
                 "time_ids": torch.stack(time_ids).to(device, dtype)}
    return latents, hidden, extra


def lora_state(unet):
    """The add-on's weights (PEFT names, without the adapter name), as float32 tensors on the processor."""
    from peft.utils import get_peft_model_state_dict
    return {k: v.detach().float().contiguous().cpu() for k, v in get_peft_model_state_dict(unet).items()}


def train_lora(base, items, cache_dir, run_dir, steps, device, dtype):
    """Train the LoRA for steps steps (each: batch x accumulate pictures), saving it with the optimizer every
    save_every steps into run_dir/checkpoints (the newest two kept) and carrying on from the newest after a stop.
    Returns (the trained UNet's LoRA weights, seconds over every start, the mean error of the last 100 steps)."""
    import torch
    from diffusers import DDPMScheduler
    from diffusers.training_utils import compute_snr
    from peft import LoraConfig
    from peft.utils import set_peft_model_state_dict
    from safetensors.torch import load_file, save_file
    settings = BASES[base.key]
    batch, accumulate = settings["batch"], settings["accumulate"]
    save_every = min(settings["save_every"], max(1, steps // 2))
    unet = base.unet(dtype).to(device)
    unet.requires_grad_(False)
    unet.add_adapter(LoraConfig(r=RANK, lora_alpha=RANK, init_lora_weights="gaussian", target_modules=TARGETS))
    params = [p for p in unet.parameters() if p.requires_grad]
    for p in params:
        p.data = p.data.float()                          # the add-on learns in full precision, the model is bf16
    unet.enable_gradient_checkpointing()
    unet.train()
    try:
        import bitsandbytes as bnb
        if device != "cuda":
            raise RuntimeError("8-bit AdamW needs the graphics card")
        optimizer = bnb.optim.AdamW8bit(params, lr=RATE, weight_decay=1e-2)
    except Exception:  # noqa: BLE001 - no bitsandbytes (the kit's own tests on a processor)
        optimizer = torch.optim.AdamW(params, lr=RATE, weight_decay=1e-2)
    warmup = max(1, min(100, steps // 20))

    def rate_at(step):
        """Warm up, then a cosine fall to nothing."""
        if step < warmup:
            return (step + 1) / warmup
        return 0.5 * (1 + math.cos(math.pi * (step - warmup) / max(1, steps - warmup)))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, rate_at)
    noise_scheduler = DDPMScheduler.from_pretrained(base.folder, subfolder="scheduler")
    noise_scheduler.alphas_cumprod = noise_scheduler.alphas_cumprod.to(device)
    prediction = noise_scheduler.config.prediction_type
    batches = plan_batches(items, batch, steps * accumulate, SEED)
    checkpoints = os.path.join(run_dir, "checkpoints")
    os.makedirs(checkpoints, exist_ok=True)
    position, earlier, losses = 0, 0.0, []
    saved = sorted(d for d in os.listdir(checkpoints) if d.startswith("step-") and
                   os.path.exists(os.path.join(checkpoints, d, "progress.json")))
    if saved:
        newest = os.path.join(checkpoints, saved[-1])
        with open(os.path.join(newest, "progress.json"), encoding="utf-8") as f:
            progress = json.load(f)
        position, earlier, losses = progress["step"], progress["seconds"], progress.get("losses", [])
        set_peft_model_state_dict(unet, load_file(os.path.join(newest, "lora.safetensors")), adapter_name="default")
        for p in params:
            p.data = p.data.float()
        state = torch.load(os.path.join(newest, "optimizer.pt"), map_location="cpu", weights_only=False)
        optimizer.load_state_dict(state["optimizer"])
        scheduler.load_state_dict(state["scheduler"])
        say(f"  Carrying on from step {position} of {steps}.")

    def precision():
        """bf16 mixed precision on the graphics card; plain float32 on the processor (tests)."""
        return torch.autocast("cuda", dtype=torch.bfloat16) if device == "cuda" else contextlib.nullcontext()
    start, started_at, last_said = time.time(), position, time.time()
    per_step = batch * accumulate
    timer = train.system_monitor.Timer()      # where the time goes: written into the logs with each progress line
    line_from = position                      # the step of the last progress line
    for step in range(position, steps):
        total = 0.0
        for part in range(accumulate):
            index = step * accumulate + part
            began = time.time()
            latents, hidden, extra = load_batch(items, batches[index], cache_dir, base, device, dtype)
            timer.add("reading pictures from the disk", time.time() - began)
            began = time.time()
            generator = torch.Generator().manual_seed(SEED * 1_000_003 + index)
            noise = torch.randn(latents.shape, generator=generator).to(device)
            timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (latents.shape[0],),
                                      generator=generator).to(device)
            noisy = noise_scheduler.add_noise(latents, noise, timesteps)
            target = noise if prediction == "epsilon" else noise_scheduler.get_velocity(latents, noise, timesteps)
            with precision():
                predicted = unet(noisy.to(dtype), timesteps, hidden, added_cond_kwargs=extra).sample
            loss = torch.nn.functional.mse_loss(predicted.float(), target.float(), reduction="none")
            loss = loss.mean(dim=list(range(1, loss.ndim)))
            snr = compute_snr(noise_scheduler, timesteps)
            weight = torch.clamp(snr, max=SNR_GAMMA) / (snr if prediction == "epsilon" else snr + 1)
            loss = (loss * weight).mean()
            (loss / accumulate).backward()
            total += loss.item() / accumulate        # waits for the graphics card, so the timing is true
            timer.add("graphics card work", time.time() - began)
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad(set_to_none=True)
        losses = (losses + [total])[-100:]
        done = step + 1
        if time.time() - last_said > SAY_EVERY or done == steps:
            last_said = time.time()
            per = (time.time() - start) / (done - started_at)
            left = f"; about {duration(per * (steps - done))} left" if done < steps else ""
            say(f"    {done * per_step} of {steps * per_step} pictures trained ({done * 100 // steps} percent, step "
                f"{done} of {steps}){left}. Mistake score {sum(losses) / len(losses):.3f} (lower is better; it "
                "goes up and down; this is not an error).")
            say("    " + timer.line(max(1, (done - line_from) * per_step), "pictures"))
            line_from = done
        if done % save_every == 0 or done == steps:
            folder = os.path.join(checkpoints, f"step-{done:06d}")
            os.makedirs(folder, exist_ok=True)
            save_file(lora_state(unet), os.path.join(folder, "lora.safetensors"))
            torch.save({"optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict()},
                       os.path.join(folder, "optimizer.pt"))
            with open(os.path.join(folder, "progress.json"), "w", encoding="utf-8") as f:   # written last: complete
                json.dump({"step": done, "seconds": earlier + time.time() - start, "losses": losses}, f)
            for old in sorted(d for d in os.listdir(checkpoints) if d.startswith("step-"))[:-2]:
                shutil.rmtree(os.path.join(checkpoints, old), ignore_errors=True)
            if done != steps:
                say(f"    Saved at step {done}.")
    weights = lora_state(unet)
    config = unet.peft_config["default"].to_dict()
    del unet, optimizer
    free()
    return weights, config, earlier + time.time() - start, sum(losses) / max(len(losses), 1)


def save_lora(base, weights, config, final, name):
    """Write the add-on twice into final: name.safetensors in the Kohya form that ComfyUI, Automatic1111 and Forge
    load (lora_unet_..., .lora_down.weight, .lora_up.weight, .alpha; half size), and pytorch_lora_weights.safetensors
    in the diffusers form (load_lora_weights)."""
    from diffusers import StableDiffusionPipeline, StableDiffusionXLPipeline
    from diffusers.utils import convert_state_dict_to_diffusers, convert_state_dict_to_kohya
    from safetensors.torch import save_file
    os.makedirs(final, exist_ok=True)
    pipeline = StableDiffusionXLPipeline if base.sdxl else StableDiffusionPipeline
    config = {k: (sorted(v) if isinstance(v, set) else v) for k, v in config.items()}
    pipeline.save_lora_weights(final, unet_lora_layers=convert_state_dict_to_diffusers(weights),
                               unet_lora_adapter_metadata=config)
    kohya = convert_state_dict_to_kohya({f"unet.{k}": v for k, v in weights.items()})
    kohya = {k: (v.float() if k.endswith(".alpha") else v.half()).contiguous() for k, v in kohya.items()}
    version, architecture = BASES[base.key]["kohya"]
    metadata = {"ss_network_module": "networks.lora", "ss_network_dim": str(RANK), "ss_network_alpha": str(RANK),
                "ss_base_model_version": version, "modelspec.architecture": architecture,
                "modelspec.title": name, "modelspec.sai_model_spec": "1.0.0"}
    save_file(kohya, os.path.join(final, f"{name}.safetensors"), metadata=metadata)


# ----------------------------------------------------------------- 4 and 6. the test pictures

def make_pictures(pipe, captions, folder, guidance, label):
    """Make one picture for each test caption into folder/NN.png (the same seed for each number, so before and after
    differ only by the add-on); pictures already there are kept (a restarted test carries on)."""
    import torch
    os.makedirs(folder, exist_ok=True)
    for number, caption in enumerate(captions, 1):
        path = os.path.join(folder, f"{number:02d}.png")
        if os.path.exists(path):
            continue
        generator = torch.Generator("cpu").manual_seed(SEED * 1000 + number)
        image = pipe(caption, num_inference_steps=TEST_STEPS, guidance_scale=guidance, generator=generator).images[0]
        image.save(path + ".part.png")
        os.replace(path + ".part.png", path)
        say(f"    {label}: picture {number} of {len(captions)} made")


def clip_scores(folder, captions, picture_dirs, device):
    """The mean CLIP score (from 0 to 1: how well each picture matches its description, as CLIP sees it) of each
    folder of test pictures."""
    import torch
    from PIL import Image
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained(folder).to(device).eval()
    processor = CLIPProcessor.from_pretrained(folder)
    length = min(77, model.config.text_config.max_position_embeddings)
    out = []
    for pictures in picture_dirs:
        images = [Image.open(os.path.join(pictures, f"{n:02d}.png")).convert("RGB")
                  for n in range(1, len(captions) + 1)]
        inputs = processor(text=captions, images=images, return_tensors="pt", padding="max_length", truncation=True,
                           max_length=length).to(device)
        with torch.no_grad():
            result = model(**inputs)
        image = torch.nn.functional.normalize(result.image_embeds.float(), dim=-1)
        text = torch.nn.functional.normalize(result.text_embeds.float(), dim=-1)
        out.append(float((image * text).sum(-1).clamp(min=0).mean()))
    del model
    free()
    return out


def clip_verdict(before, after):
    """The CLIP result in plain words."""
    if before is None:
        return "The pictures could not be scored this time (the CLIP model was not available); look at them instead."
    if after > before + 0.005:
        return (f"The add-on's pictures matched their descriptions better than the base model's: {after:.3f} against "
                f"{before:.3f}.")
    if after < before - 0.005:
        return (f"The add-on's pictures matched their descriptions less well than the base model's: {after:.3f} "
                f"against {before:.3f}.")
    return (f"The add-on's pictures matched their descriptions about as well as the base model's: {after:.3f} "
            f"against {before:.3f}.")


# ----------------------------------------------------------------- 7. the report and the zip

def personal_lines(info):
    """The PERSONAL USE ONLY block (train.personal_lines when this kit's train.py has it)."""
    return train.personal_lines(info) if hasattr(train, "personal_lines") else []


def write_report(path, info):
    """REPORT.txt: what was trained, on what, how long, the CLIP verdict, the licence and the test captions; it starts
    with the PERSONAL USE ONLY block when a personal-use choice was made."""
    block = personal_lines(info)
    lines = [*block, *([""] if block else []), "Picture Model Training Kit: picture-making add-on report", "",
             f"Finished: {datetime.datetime.now():%d %B %Y at %H:%M}",
             f"Base model: {info['base_name']} ({info['repo']}, commit {info['revision'][:12]})",
             f"Graphics card: {info['card']}",
             (f"Training pictures: {info['train']} described pictures"
              + (f", {info['own']} of them your own" if info["own"] else "") + f"; size: {info['size']}"),
             (f"Training: {info['steps']} steps of {info['per_step']} pictures; LoRA rank {RANK}, learning rate "
              f"{RATE}, min-SNR weighting (gamma {SNR_GAMMA:g}), {info['precision']}"),
             f"Training time: {duration(info['seconds'])}; final error {info['loss']:.3f}",
             *([children_note(info["children_left_out"])] if info.get("children_left_out") else []),
             *([f"Pictures with a place (their description starts with where they were taken, or ends with where "
                f"they were made): {info['places']}"] if info.get("places") else []), "",
             "RESULT: " + info["verdict"],
             ("(CLIP score: how well each test picture matches its description, as the CLIP model sees it, from 0 to "
              "1; a rough measure. The test pictures are in test-before and test-after, with captions.txt; the "
              "toolkit's picture describer can describe them.)"), "",
             "Licence: " + info["licence"], LICENCE_NOTE]
    if info["share_alike"]:
        lines.append("It also learned from Wikipedia's text, so it is shared under CC BY-SA 4.0 as well.")
    lines += content_lines(info)
    lines += ["", "Collections it learned from (pictures each):"]
    for key, count in sorted(info["collections"].items(), key=lambda kv: -kv[1]):
        lines.append(f"  {'Your own pictures' if key == 'own' else train.source_name(key)}: {count}")
    lines += ["", "Test descriptions (the same seed before and after):"]
    lines += [f"  {n:02d}. {c}" for n, c in enumerate(info["captions"], 1)]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def content_lines(info):
    """The content choices and the own-pictures note (train.content_lines when this kit's train.py has it)."""
    if hasattr(train, "content_lines"):
        return train.content_lines(info)
    if info["own"]:
        return ["Includes your own pictures: for personal use only; do not publish this add-on."]
    return []


def attribution_text(info):
    """ATTRIBUTION.txt: the base model and its licence, then train.py's credits of every collection used (its first
    lines, about the describer's licence, are replaced by the base model's)."""
    keys = list(info["collections"])
    try:
        credits = train.attribution(keys, info["share_alike"], info)
    except TypeError:                                   # an older train.py
        credits = train.attribution(keys, info["share_alike"])
    marker = "It learned from"
    body = credits[credits.index(marker):] if marker in credits else credits
    head = [f"Picture-making add-on (LoRA) for {info['base_name']}", "",
            f"Base model: {info['repo']}, licence {info['licence']}.", LICENCE_NOTE]
    if info.get("vae"):
        head.append(f"Pictures were prepared with the fp16-fix VAE ({info['vae']}, MIT licence).")
    if info["share_alike"]:
        head.append("It learned from Wikipedia's CC BY-SA 4.0 text, so it is shared under CC BY-SA 4.0 as well.")
    if personal_lines(info):                      # personal use only: said at the top too
        head.append(sources.PERSONAL_WARNING)
    return "\n".join(head) + "\n\n" + body


def how_to_use(info, name):
    """HOW TO USE.txt for ComfyUI, Automatic1111/Forge and diffusers."""
    base = info["base_name"]
    checkpoint = "sd_xl_base_1.0.safetensors" if info["key"] == "sdxl" else "v1-5-pruned-emaonly.safetensors"
    loader = "StableDiffusionXLPipeline" if info["key"] == "sdxl" else "StableDiffusionPipeline"
    return f"""How to use this add-on (a LoRA for {base})

It makes {base} draw what a plain description says. Write the prompt as a plain description, like the ones in
captions.txt. A strength between 0.7 and 1.0 is a good start.

ComfyUI
  1. Copy {name}.safetensors into ComfyUI\\models\\loras.
  2. Between "Load Checkpoint" ({checkpoint}) and the text and sampler nodes, add a "Load LoRA" node and choose
     {name}.safetensors; set strength_model to 0.8 (strength_clip does nothing: only the picture part learned).

Automatic1111 and Forge
  1. Copy {name}.safetensors into the models\\Lora folder.
  2. Choose the {base} checkpoint ({checkpoint}), and add <lora:{name}:0.8> to the prompt (or pick it in the
     Lora tab).

diffusers (Python)
  import torch
  from diffusers import {loader}
  pipe = {loader}.from_pretrained("{info['repo']}", torch_dtype=torch.float16).to("cuda")
  pipe.load_lora_weights("diffusers", weight_name="pytorch_lora_weights.safetensors")
  image = pipe("A red bicycle leaning against a white wall.", num_inference_steps=25).images[0]

Licence: {info['licence']}. {LICENCE_NOTE}
""" + ("\nIt learned from your own pictures: for personal use only.\n" if info["own"] else "") + (
        "\n" + "\n".join(personal_lines(info)) + "\n" if personal_lines(info) else "")


# Accessible AI Studio (mark-getbraille/accessible-AI-image-and-video-generation): its own "Train add-ons" keeps each
# add-on in models\trained-<slug>\ with pytorch_lora_weights.safetensors (the diffusers form, loaded with
# load_lora_weights), trained.json and .complete (its app/training.py register()); the zip carries the same folder.
STUDIO_FOLDER = "Accessible AI Studio"
STUDIO_FAMILY = {"sdxl": "sdxl", "sd15": "sd15"}       # the kit's base -> Accessible AI Studio's model family


def studio_slug(name):
    """The folder name Accessible AI Studio gives an add-on of this name (its app/training.py slug(): lower case,
    every run of other characters one hyphen, at most 40 characters)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "add-on"


def studio_trained_json(info, name):
    """trained.json for Accessible AI Studio: the fields its register() writes (name, family, trigger, kind,
    trained_on_real) and, for people reading it, where the add-on came from. trained_on_real is true: the kit learns
    from real photographs, so Accessible AI Studio checks every job that uses it as if a real photo were given (its
    second content rule). There is no trigger word: the add-on learns to follow plain descriptions."""
    return json.dumps({"name": name, "family": STUDIO_FAMILY[info["key"]], "trigger": "", "kind": "style",
                       "trained_on_real": True, "made_by": "Picture Describer Training Wizard (picture-making)",
                       "base_repo": info["repo"], "base_revision": info.get("revision", ""),
                       "licence": info.get("licence", ""), "share_alike": bool(info.get("share_alike")),
                       "personal_use": bool(personal_lines(info) or info.get("own")),
                       "trained": datetime.date.today().isoformat()}, indent=2)


def studio_how_to(info, name):
    """The steps for Accessible AI Studio, in plain words."""
    folder = f"trained-{studio_slug(name)}"
    return f"""How to use this add-on in Accessible AI Studio

The folder "{folder}" here is laid out exactly like an add-on that Accessible AI Studio trained itself: the add-on
(pytorch_lora_weights.safetensors), trained.json (its name, the model family: {info['base_name']}) and .complete.

1. In Accessible AI Studio, use "Add a trained add-on from a file..." in the Models and settings window ("Your own
   models") and choose this zip, or the folder "{folder}" in it.
2. It is then in the AI picture model box as "Your add-on: {name} with <model>", once for each {info['base_name']}
   picture model you have downloaded. Describe the picture in plain words, like the ones in captions.txt.

It is marked "trained on real photos", because it learned from real photographs: Accessible AI Studio then checks
every picture made with it as if a real photo were given, as its content rules say.
To use it on another computer, copy this zip there and add it the same way.
"""


def package(run_dir, final, name, info, report):
    """The zip to send, in the kit's "result" folder: the add-on in both forms, the test pictures, captions.txt,
    REPORT.txt, ATTRIBUTION.txt, HOW TO USE.txt, settings.json, the log, and the folder "Accessible AI Studio" (the
    add-on in that program's own layout, with its steps); returns its path."""
    folder = os.path.join(HERE, "result")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{name}-{datetime.date.today():%Y-%m-%d}.zip")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(final, f"{name}.safetensors"), f"{name}.safetensors")
        z.write(os.path.join(final, "pytorch_lora_weights.safetensors"), "diffusers/pytorch_lora_weights.safetensors")
        for part in ("test-before", "test-after"):
            for picture in sorted(os.listdir(os.path.join(run_dir, part))):
                if picture.endswith(".png") and ".part" not in picture:
                    z.write(os.path.join(run_dir, part, picture), f"{part}/{picture}")
        z.write(os.path.join(run_dir, "captions.txt"), "captions.txt")
        z.write(report, "REPORT.txt")
        z.writestr("ATTRIBUTION.txt", attribution_text(info))
        z.writestr("HOW TO USE.txt", how_to_use(info, name))
        if personal_lines(info):
            z.writestr("PERSONAL-USE-ONLY.txt", "\n".join(personal_lines(info)) + "\n")
        z.writestr("settings.json", json.dumps({k: v for k, v in info.items() if k != "captions"}, indent=1))
        # The add-on in Accessible AI Studio's own layout (see STUDIO_FOLDER).
        studio = f"{STUDIO_FOLDER}/trained-{studio_slug(name)}/"
        z.write(os.path.join(final, "pytorch_lora_weights.safetensors"), studio + "pytorch_lora_weights.safetensors")
        z.writestr(studio + "trained.json", studio_trained_json(info, name))
        z.writestr(studio + ".complete", "trained by the Picture Describer Training Wizard\n")
        z.writestr(f"{STUDIO_FOLDER}/HOW TO USE IN ACCESSIBLE AI STUDIO.txt", studio_how_to(info, name))
        if os.path.exists(train.LOG):
            z.write(train.LOG, "training-log.txt")
    return path


# ----------------------------------------------------------------- all steps

def plural(count, word):
    """ "1 test picture", "12 test pictures". """
    return f"{count} {word}{'' if count == 1 else 's'}"


def check_computer(settings, work, testing):
    """(card name, device, dtype): the NVIDIA card in bf16, or, for the kit's own tests only, the processor in
    float32. Stops with a plain reason when the card or the disk is too small."""
    import torch
    if not torch.cuda.is_available():
        if testing:
            say("No graphics card: testing on the processor (tiny test models only).")
            return "none (processor test)", "cpu", torch.float32
        stop("No NVIDIA graphics card can be used. Picture training needs an NVIDIA card with at least "
             f"{settings['memory']} GB of memory and an up-to-date NVIDIA driver (from nvidia.com).")
    props = torch.cuda.get_device_properties(0)
    memory = props.total_memory / 1024 ** 3
    say(f"Graphics card: {props.name}, {memory:.0f} GB of memory.")
    if memory < settings["memory"] - 0.5 and not testing:
        stop(f"{settings['name']} needs a card with at least {settings['memory']} GB of memory; this card has "
             f"{memory:.0f} GB." + (" Try SD 1.5 instead." if settings is BASES["sdxl"] else ""))
    free_gb = shutil.disk_usage(work).free / 1024 ** 3
    say(f"Free disk space on this drive: {free_gb:.0f} GB.")
    if free_gb < settings["disk"] and not testing:
        stop(f"Picture training needs about {settings['disk']} GB of free disk space here; there is {free_gb:.0f} GB.")
    torch.backends.cuda.matmul.allow_tf32 = True
    return props.name, "cuda", torch.bfloat16


def main(argv=None):
    """Run the steps (see the module docstring)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", choices=sorted(BASES), default="sdxl")
    parser.add_argument("--library", default="", help="the permanent picture library folder")
    parser.add_argument("--size", choices=sorted(sources.SIZES), default="normal")
    parser.add_argument("--with-wikipedia", action="store_true", help="also learn from Wikipedia (CC BY-SA 4.0)")
    parser.add_argument("--with-nudity", action="store_true", help="also the collections with nudity")
    parser.add_argument("--with-medical", action="store_true", help="also the medical collections")
    parser.add_argument("--own", default="", help="a folder of your own described pictures to add")
    parser.add_argument("--own-only", action="store_true", help="learn only from your own pictures")
    parser.add_argument("--limit", type=int, default=0, help="train on at most this many pictures")
    parser.add_argument("--personal-noncommercial", action="store_true",
                        help="also non-commercial collections (the add-on is for personal use only)")
    parser.add_argument("--personal-research", action="store_true",
                        help="also research-only collections (personal use only; needs --accept-research-terms)")
    parser.add_argument("--accept-research-terms", action="store_true",
                        help="you have read the research-only collections' terms and will use the result only for "
                             "personal, non-commercial purposes")
    parser.add_argument("--work", default="", help="the work folder (the kit's work folder when not given)")
    parser.add_argument("--base-repo", default="", help=argparse.SUPPRESS)     # tests: a tiny diffusers model
    parser.add_argument("--clip-repo", default="", help=argparse.SUPPRESS)     # tests: a tiny CLIP model
    parser.add_argument("--steps", type=int, default=0, help=argparse.SUPPRESS)  # tests: this many steps exactly
    args = parser.parse_args(argv)
    if args.own_only and not args.own:
        parser.error("--own-only needs --own FOLDER")
    personal = args.personal_noncommercial or args.personal_research
    if args.personal_research and not args.accept_research_terms:
        stop("Research-only collections were chosen, but their terms were not accepted. Read their terms and agree "
             "to use the result only for personal, non-commercial purposes (in the program: tick Include "
             "research-only collections and press Agree; on the command line: add --accept-research-terms).")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    sources.say = say
    work = os.path.abspath(args.work) if args.work else os.path.join(HERE, "work")
    os.makedirs(work, exist_ok=True)
    keep_awake(True)
    train.system_monitor.start(say)           # computer use into the logs every 5 minutes (system_monitor.py)
    if args.library:
        train.open_library(work, args.library)       # before Hugging Face is imported: it reads HF_HOME once
    try:
        from diffusers.utils import logging as diffusers_logging
        diffusers_logging.set_verbosity_error()          # only the kit's own plain sentences on the screen
        from transformers.utils import logging as transformers_logging
        transformers_logging.set_verbosity_error()
    except ImportError:
        stop("The picture-making tools are not installed (kit\\requirements-pictures.txt). Start the kit again.")
    settings = BASES[args.base]
    testing = bool(args.base_repo)
    repo, revision = (args.base_repo, "main") if testing else (settings["repo"], settings["revision"])
    root = os.path.join(work, "pictures")
    tag = "".join(f"-{w}" for w, on in (("wikipedia", args.with_wikipedia), ("nudity", args.with_nudity),
                                         ("medical", args.with_medical)) if on)
    tag += "-own-only" if args.own_only else ("-own" if args.own else "")
    tag += "-personal" if personal else ""          # personal use only: its own training, never mixed up
    tag += f"-limit{args.limit}" if args.limit else ""
    run = f"{args.base}-{args.size}{tag}" + (f"-test-{slug(repo)}" if testing else "")
    run_dir = os.path.join(root, run)
    os.makedirs(run_dir, exist_ok=True)
    state = State(run_dir)
    batch, accumulate = settings["batch"], settings["accumulate"]
    per_step = batch * accumulate
    say("")
    say(f"Picture Model Training Kit started: a picture-making add-on for {settings['name']}, size {args.size}"
        + (", from your own pictures only." if args.own_only else "."))
    if personal:
        say("Personal-use collections included: this training will be for personal use only.")
    say("Windows will not go to sleep while this runs; the screen may turn off. You can close this window at any time "
        "and start the kit again later: it carries on where it stopped.")

    say("Step 1 of 7: checking the graphics card and the disk.")
    card, device, dtype = check_computer(settings, work, testing)

    say(f"Step 2 of 7: downloading {settings['name']} ({'a tiny test model' if testing else settings['download']}; "
        "carries on if stopped).")
    folder = os.path.join(root, "base-" + (slug(repo) if testing else args.base))
    variants = download(repo, revision, folder)
    vae_folder = None
    if settings["vae"] and not testing:
        vae_folder = download_single(*settings["vae"], os.path.join(root, "vae-fp16-fix"),
                                     ["diffusion_pytorch_model.safetensors"])
    base = Base(args.base, folder, variants, vae_folder)
    if base.sdxl != (args.base == "sdxl"):
        stop(f"The model {repo} is not a {args.base.upper()} model.")
    clip_repo, clip_revision = (args.clip_repo, "main") if args.clip_repo else CLIP
    clip_folder = None
    try:
        clip_folder = download_single(clip_repo, clip_revision, os.path.join(root, "clip-" + slug(clip_repo)),
                                      ["model.safetensors", "pytorch_model.bin"])
    except Exception as e:  # noqa: BLE001 - the score is a help, not a need
        say(f"  The CLIP model for the test score could not be downloaded ({str(e).splitlines()[0][:150]}); the "
            "test pictures are still made.")

    items_path, tests_path = os.path.join(run_dir, "items.json"), os.path.join(run_dir, "tests.json")
    wanted = (args.steps or settings["steps"][args.size]) * per_step
    if not state.done("items"):
        say("Step 3 of 7: choosing the described pictures (only real descriptions, in English) from the picture "
            "library.")
        train_rows, test_rows = ([], []) if args.own_only else library_rows(work, args)
        mine = own_rows(args.own, args) if args.own else []
        if mine:
            say("  A reminder: pictures of children are left out automatically when their description mentions a "
                "child; also leave out pictures of anyone who has not agreed.")
        from transformers import CLIPTokenizer
        tokenizer = CLIPTokenizer.from_pretrained(folder, subfolder="tokenizer")
        items, tests, children = choose_items(train_rows, test_rows, mine, tokenizer, args, wanted)
        if children:
            say("  " + children_note(children))
        state.mark("children", children)          # for the report, also after a restart
        if not items or not tests:
            stop("There are no described pictures to learn from. Prepare the picture library first (Start Training), "
                 "or give a folder of your own described pictures.")
        with open(items_path, "w", encoding="utf-8") as f:
            json.dump(items, f)
        with open(tests_path, "w", encoding="utf-8") as f:
            json.dump(tests, f)
        state.mark("items", len(items))
    else:
        say("Step 3 of 7: the described pictures were chosen before.")
    with open(tests_path, encoding="utf-8") as f:
        tests = json.load(f)
    captions = [t["caption"] for t in tests]
    with open(os.path.join(run_dir, "captions.txt"), "w", encoding="utf-8") as f:
        f.write("".join(f"{n:02d}. {c}\n" for n, c in enumerate(captions, 1)))
    say(f"  Ready: {state.data['items']} descriptions for training, {len(tests)} for the test.")

    cache_dir = os.path.join(root, "cache-" + (slug(repo) if testing else args.base))
    ready_path = os.path.join(run_dir, "ready.json")
    if not state.done("cached"):
        say("Step 4 of 7: preparing the pictures and descriptions for training (once; they are kept on disk).")
        with open(items_path, encoding="utf-8") as f:
            items = json.load(f)
        ready = cache(items, base, cache_dir, device, dtype)
        if not ready:
            stop("None of the chosen pictures could be read.")
        epochs = 20 if args.own_only else 2          # a small folder of one's own pictures needs more passes
        steps = args.steps or min(settings["steps"][args.size], max(1, math.ceil(epochs * len(ready) / per_step)))
        with open(ready_path, "w", encoding="utf-8") as f:
            json.dump(ready, f)
        state.mark("cached", {"pictures": len(ready), "steps": steps})
    else:
        say("Step 4 of 7: the pictures and descriptions were prepared before.")
    with open(ready_path, encoding="utf-8") as f:
        ready = json.load(f)
    steps = state.data["cached"]["steps"]
    if not state.done("before"):
        say(f"  Making the {plural(len(captions), 'test picture')} with the base model, before training.")
        pipe = base.pipeline(device, dtype)
        make_pictures(pipe, captions, os.path.join(run_dir, "test-before"), settings["guidance"], "before training")
        del pipe
        free()
        state.mark("before")

    name = f"described-pictures-{args.base}{tag}"
    final = os.path.join(run_dir, "final")
    if not state.done("train"):
        say(f"Step 5 of 7: training on {len(ready)} pictures: {steps} steps of {per_step} pictures, about "
            f"{duration(steps * settings['seconds'])} on an RTX 5060 Ti. This is the long part; the time left is said "
            "every minute or so.")
        weights, config, seconds, loss = train_lora(base, ready, cache_dir, run_dir, steps, device, dtype)
        save_lora(base, weights, config, final, name)
        state.mark("train", {"seconds": seconds, "loss": loss})
    else:
        say("Step 5 of 7: training is done (done before).")

    if not state.done("after"):
        say(f"Step 6 of 7: making the {plural(len(captions), 'test picture')} again, with the add-on.")
        pipe = base.pipeline(device, dtype)
        pipe.load_lora_weights(final, weight_name="pytorch_lora_weights.safetensors")
        make_pictures(pipe, captions, os.path.join(run_dir, "test-after"), settings["guidance"], "after training")
        del pipe
        free()
        scores = [None, None]
        if clip_folder:
            try:
                scores = clip_scores(clip_folder, captions, [os.path.join(run_dir, "test-before"),
                                                             os.path.join(run_dir, "test-after")], device)
            except Exception as e:  # noqa: BLE001
                say(f"  The test pictures could not be scored ({str(e).splitlines()[0][:150]}).")
        state.mark("after", {"before": scores[0], "after": scores[1]})
    scores = state.data["after"]
    if scores["before"] is not None:
        say(f"  Score after training: {scores['after']:.3f} (before: {scores['before']:.3f}; CLIP, higher is better).")

    say("Step 7 of 7: writing the report and the zip to send.")
    collections = {}
    for item in ready:
        collections[item["source"]] = collections.get(item["source"], 0) + 1
    info = {"key": args.base, "base_name": settings["name"], "repo": repo, "revision": revision, "card": card,
            "vae": settings["vae"][0] if vae_folder else None, "licence": settings["licence"],
            "train": len(ready), "own": collections.get("own", 0), "size": args.size, "steps": steps,
            "per_step": per_step, "seconds": state.data["train"]["seconds"], "loss": state.data["train"]["loss"],
            "share_alike": args.with_wikipedia, "collections": collections, "captions": captions,
            "with_nudity": args.with_nudity, "with_medical": args.with_medical,
            "with_noncommercial": args.personal_noncommercial, "with_research": args.personal_research,
            "own_pictures": collections.get("own", 0), "own_only": args.own_only,
            "children_left_out": state.data.get("children") or 0,
            "places": sum(1 for item in ready if item.get("place")),
            "clip_before": scores["before"], "clip_after": scores["after"],
            "verdict": clip_verdict(scores["before"], scores["after"]),
            "precision": "bf16 mixed precision, 8-bit AdamW" if device == "cuda" else "float32 on the processor (test)",
            "settings": {"rank": RANK, "alpha": RANK, "rate": RATE, "batch": batch, "accumulate": accumulate,
                         "snr_gamma": SNR_GAMMA, "targets": TARGETS, "resolution": base.resolution,
                         "buckets": base.buckets, "test_steps": TEST_STEPS}}
    report = os.path.join(HERE, f"report-pictures-{run}.txt")
    write_report(report, info)
    path = package(run_dir, final, name, info, report)
    keep_awake(False)
    say("")
    say("FINISHED. " + info["verdict"])
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
