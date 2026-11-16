"""Videos into training pictures: take good still pictures out of videos and give each one a description, so the
Picture Model Training Kit can learn from them (as "your own pictures", read by own_data.py).

There are three ways to use it.

1. Your own videos (the main use). You film while talking about what is in front of you, for example with Meta
   smart glasses in a shop: "these are Granny Smith apples, a dollar twenty-nine a pound". For each video:
     - about 4 pictures a second are looked at; dark, blurry and near-identical pictures are left out, and at most
       one picture is kept for every --every seconds (2 by default): the sharpest one;
     - your speech is turned into text (faster-whisper, on the graphics card when it can, otherwise the processor);
     - each picture gets what you said at that moment, or what you started saying up to 3 seconds later (people
       look first, then speak), lightly tidied, in a text file of the same name: Shop_00-12.5.jpg with
       Shop_00-12.5.txt. That is layout a) of own_data.py, so the output folder can be chosen as "your own
       pictures" straight away.
     - pictures with nothing said near them get no text file; they are listed in "NO DESCRIPTION YET.txt". With
       --draft-descriptions the kit's own picture model writes a DRAFT for them into Shop_00-12.5.draft.txt, which
       is not used for training until a person has checked it and renamed it to .txt.
     - the whole transcript, with times, goes into transcript.txt.
     - --blur-faces blurs the faces of other people (OpenCV's YuNet face finder).

2. Online videos with an open licence (--share-alike, --speech, --from-search): an archive.org item (address or
   identifier), a Wikimedia Commons video page (File:....webm) or a NASA video (images.nasa.gov). Only public
   domain, CC0 and CC BY videos are used (CC BY-SA only with --share-alike); anything else is refused, with the
   reason. The video is read straight from the web, a moment at a time, so only the parts needed are fetched.
   These stills get no description: they are listed in stills-for-describers.jsonl for the Picture Describers
   website, with their credit, and every still is credited in CREDITS.txt. With --speech the narration near each
   still is written to <name>.narration.txt (never .txt: narration rarely describes the picture).

3. Audio-described videos you already have (--described), for PERSONAL training only. Professional audio
   description says what is on the screen in the pauses between the dialogue, which makes good picture
   descriptions. The description comes from a) an audio track of the video marked as audio description (found by
   its title or flag, or chosen with --ad-track N), b) a separate description sound file (--ad-audio FILE), or
   c) a WebVTT or SRT description text file (--ad-text FILE). When the description track is the full mix (the film's
   sound plus the narrator), both tracks are turned into text and the lines that are not in the plain soundtrack at
   the same time are the narrator's. For each narrator line, the sharpest picture while it is said is kept, and
   the line goes into the picture's own .txt file, and question.txt gives the folder's question "Describe what is happening in this
   picture." PERSONAL-USE.txt is written beside them. Nothing is downloaded from streaming services and nothing is
   unlocked: only video files you already have.

Burned-in overlays, in all three (--overlays crop or fill; the default, keep, changes nothing): a camcorder's date
and time stamp, a TV station's logo or a fixed ticker is found by what stays the same while the picture behind it
changes, in the pictures already looked at (no AI; see find_overlays()). Only marks near an edge or corner are
taken, and only when most of the picture changes over the video (a still camera: nothing is looked for, and that is
said). They are cropped off (the largest part of the picture around its middle without them; filled in when that would
lose more than a fifth of the picture) or filled in from around them (OpenCV's inpainting). --overlay-box x,y,w,h (in
percent) adds a box by hand. What was found and done for each video is said and written into OVERLAYS.txt. Faces
are blurred after, in the picture that is saved.

Command line:
    python video_frames.py VIDEO_OR_FOLDER_OR_ADDRESS ... --out FOLDER [--every SECONDS] [--max N] [--no-speech]
        [--language en] [--blur-faces] [--draft-descriptions] [--speech] [--share-alike]
        [--overlays keep|crop|fill [--overlay-box X,Y,W,H ...]]
        [--from-search "words" --collection prelinger --max-videos N]
        [--described [--ad-track N | --ad-audio FILE | --ad-text FILE]]

For the wizard: make_pictures(...) and make_described_pictures(...) do the work and return a summary in plain
words; audio_tracks(video) lists a video's sound tracks.

A video done before (its pictures are already in the output folder) is skipped, so descriptions you have
corrected are never written over. Delete its pictures to make them again.

Needs the packages in requirements-video.txt (besides requirements.txt for --draft-descriptions).
"""

import argparse
import csv
import datetime
import gc
import hashlib
import json
import math
import os
import re
import sys
import urllib.parse

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))      # the kit folder
WORK = os.path.join(KIT, "work")                                       # downloads (speech model, face finder)
USER_AGENT = "PictureModelTrainingKit/2"                               # the same plain name sources.py uses

# Choosing pictures.
SAMPLE_RATE = 4            # pictures looked at per second of video
LONG_SIDE = 2048           # the largest side of a saved picture, in pixels
SCORE_SIDE = 640           # the size pictures are scored at (smaller is faster, and enough to judge)
DARK = 40                  # mean brightness (0 to 255) below which a picture is too dark
SHARP_LEAST = 12.0         # sharpness (variance of the Laplacian) below which a picture is always too blurry
SHARP_SHARE = 0.35         # ... or below this share of the video's usual sharpness
SAME_BITS = 10             # pictures whose fingerprints differ in this many of 64 bits or fewer look the same
JPEG_QUALITY = 92

# Matching speech to pictures.
SPEAK_AFTER = 3.0          # seconds after a picture within which speech that starts still belongs to it
PAUSE = 0.8                # a pause this long (seconds) between words starts a new phrase

# Online videos.
ONLINE_MOST = 20           # pictures from one online video when --max is not given
SPOT_LENGTH = 1.0          # seconds read at each spot of an online video
ONLINE_QUESTION = ""       # the describers' site asks its own question

# Audio-described videos.
AD_QUESTION = "Describe what is happening in this picture."
AD_SHARED = 0.4            # a description-track line sharing less than this share of words with the soundtrack ...
AD_NEAR = 1.5              # ... within this many seconds is the narrator's
AD_FROM = 0.3              # the picture for a line is looked for from this many seconds after it starts ...
AD_SHORT = 2.0             # ... to its end, or to this many seconds after its start for short lines
AD_TRACK_WORDS = ("audio description", "audio-description", "descriptive", "described", "description", "ad", "dv")
PERSONAL_USE = ("These pictures and descriptions come from videos you supplied. They are for training your own "
                "personal model only. Don't share the pictures or descriptions, and don't publish a model trained "
                "on them, unless you have the rights.")

# The draft describer: the kit's own picture model (train.py MODELS), asked a short question.
DRAFT_QUESTION = "What is this? Answer in one or two sentences, and read any label or price."

VIDEO_ENDINGS = (".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".3gp", ".mts", ".m2ts", ".wmv", ".ogv")

# The speech recogniser (faster-whisper models, MIT licence), pinned to a commit: (repository, commit, size).
WHISPER_MODELS = {
    "large-v3-turbo": ("dropbox-dash/faster-whisper-large-v3-turbo", "0a363e9161cbc7ed1431c9597a8ceaf0c4f78fcf",
                       "about 1.6 GB"),
    "medium.en": ("Systran/faster-whisper-medium.en", "a29b04bd15381511a9af671baec01072039215e3", "about 1.5 GB"),
    "tiny.en": ("Systran/faster-whisper-tiny.en", "0d3d19a32d3338f10357c0889762bd8d64bbdeba", "about 75 MB"),
}
WHISPER_DEFAULT = "large-v3-turbo"

# The face finder: OpenCV's YuNet (opencv_zoo, MIT licence), from OpenCV's Hugging Face copy, pinned by commit and
# by the SHA-256 of the file.
YUNET = ("opencv/face_detection_yunet", "3cc26e7f1014a5ee5d74a42acee58bafc9d0a310",
         "face_detection_yunet_2023mar.onnx", "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4")

# Burned-in overlays (camcorder date stamps, station logos, fixed tickers): found by what stays the same while the
# picture behind it changes, in the pictures already looked at (no AI). See find_overlays().
OVERLAY_CHOICES = ("keep", "crop", "fill")
OVERLAY_SIDE = 256         # the size (long side, pixels) the pictures are compared at
OVERLAY_LEAST = 12         # fewer pictures than this: too short to tell what stays fixed
OVERLAY_MOVING_STD = 14.0  # a spot whose colour varies more than this (0 to 255) over the video has changed ...
OVERLAY_MOVING = 0.6       # ... and at least this share of the picture must have changed (a moving camera)
OVERLAY_STILL_STD = 9.0    # a spot whose colour varies less than this stays the same
OVERLAY_EDGE = 24.0        # an edge: brightness changing by this much (0 to 255) over 2 pixels
OVERLAY_EDGE_STILL = 0.6   # a spot that stays the same and is an edge in this share of the pictures is an overlay
OVERLAY_EDGE_ALWAYS = 0.92 # ... and any spot that is an edge in this share of the pictures (see-through logos)
OVERLAY_JOIN = 0.035       # pieces closer than this share of the picture are joined (the digits of a date stamp)
OVERLAY_NEAR_EDGE = 0.15   # an overlay lies within this share of the picture from an edge
OVERLAY_EACH = 0.08        # an overlay takes at most this share of the picture ...
OVERLAY_ALL = 0.15         # ... and all of them together at most this
OVERLAY_LEAST_SHARE = 0.0005  # smaller marks are noise
OVERLAY_PAD = 0.012        # each overlay box is made this share of the picture bigger on every side
CROP_MOST_LOST = 0.20      # cropping that loses more than this share of the picture fills in instead
CROP_ASPECT = 1.34         # a cropped still's shape may differ from the video's by at most this factor

# File names in the output folder.
NO_DESCRIPTION = "NO DESCRIPTION YET.txt"
TRANSCRIPT = "transcript.txt"
CREDITS = "CREDITS.txt"
DESCRIBERS_LIST = "stills-for-describers.jsonl"
CAPTIONS = "captions.csv"
QUESTION_FILE = "question.txt"     # the question for a folder's pictures (own_data.py reads it)
PLACE_FILE = "place.txt"           # where in the world the folder's pictures are from (own_data.py reads it)
OWN_QUESTION = "What is this?"     # your own narrated videos: what you said is the answer to this
PERSONAL_FILE = "PERSONAL-USE.txt"
OVERLAYS_FILE = "OVERLAYS.txt"     # what was found and done about date stamps and logos, one line per video


class VideoProblem(Exception):
    """A problem to say to the person in plain words (a refused licence, an unreadable video ...)."""


# ----------------------------------------------------------------- small helpers

def plural(count, one, many=None):
    """ "1 picture", "3 pictures"."""
    return f"{count} {one if count == 1 else (many or one + 's')}"


def clock(seconds):
    """A time in a video for people: "1:05.5"."""
    tenths = round(max(seconds, 0) * 10)
    minutes, rest = divmod(tenths, 600)
    return f"{minutes}:{rest // 10:02d}.{rest % 10}"


def time_name(seconds):
    """A time in a video for a file name: "01-05.5" (minutes, then seconds, with a dash, as Windows allows)."""
    tenths = round(max(seconds, 0) * 10)
    minutes, rest = divmod(tenths, 600)
    return f"{minutes:02d}-{rest // 10:02d}.{rest % 10}"


def safe_stem(name, most=60):
    """A name that is safe in a Windows file name: no \\ / : * ? " < > |, no dots or spaces at the end."""
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]+', "_", name).strip(" .")
    return (name[:most].strip(" .") or "video")


def spread(items, count):
    """count items picked evenly from items (all of them when there are not more)."""
    if count <= 0 or len(items) <= count:
        return list(items)
    if count == 1:
        return [items[len(items) // 2]]
    return [items[round(i * (len(items) - 1) / (count - 1))] for i in range(count)]


def video_files(paths):
    """The video files among paths: files as given, and the videos in folders (and their sub-folders), sorted."""
    found = []
    for path in paths:
        if os.path.isdir(path):
            for base, dirs, files in os.walk(path):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                found += [os.path.join(base, f) for f in sorted(files)
                          if f.lower().endswith(VIDEO_ENDINGS) and not f.startswith(".")]
        else:
            found.append(path)
    return found


def done_before(out, stem):
    """True when pictures of the video named stem are already in the output folder."""
    prefix = stem + "_"
    return any(n.startswith(prefix) and n.lower().endswith(".jpg") for n in os.listdir(out))


def write_text(path, text):
    """Write text to path (UTF-8, ending with a new line)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.rstrip("\n") + "\n")


def append_text(path, text):
    """Add text to the end of path (made when missing)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(text.rstrip("\n") + "\n\n")


# ----------------------------------------------------------------- tidying spoken words

FILLERS = re.compile(r"\b(?:um+|uh+|erm+|er|hmm+|mm+)\b[,.]?\s*", re.IGNORECASE)
LEAD_WORDS = re.compile(r"^(?:okay|ok|so|and|now|right|alright|all right|well)\b[,.]?\s+", re.IGNORECASE)
TENS = "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
UNITS = "one|two|three|four|five|six|seven|eight|nine"


PRICE_WORDS = {"is", "it's", "that's", "are", "was", "were", "be", "costs", "cost", "for", "about", "just", "only",
               "under", "over", "than", "and", "or", "to", "at", "says", "say"}


def price_comma(match):
    """A comma between a thing and its price ("apples a dollar" -> "apples, a dollar"), but not after a word that
    leads into the price ("it's a dollar", "for $3")."""
    word = match.group(1)
    return word + (" " if word.lower() in PRICE_WORDS else ", ")


def tidy(text, spoken=True):
    """Lightly tidy a description: spaces, a capital letter at the start and a full stop at the end. For speech
    (spoken) also: "um" and "uh" left out, a leading "okay", "so" or "and" left out, "twenty nine" written
    "twenty-nine", "i" written "I", and a comma before a price ("apples a dollar" -> "apples, a dollar"). The
    words themselves are kept: nothing is added."""
    text = " ".join(str(text or "").split())
    if spoken:
        text = " ".join(FILLERS.sub("", text).split())
        for _ in range(3):
            text = LEAD_WORDS.sub("", text)
        text = re.sub(rf"\b({TENS})[ -]({UNITS})\b", r"\1-\2", text, flags=re.IGNORECASE)
        text = re.sub(r"\bi\b", "I", text)
        text = re.sub(r"\b([A-Za-z']+)\s+(?=(?:a|one) dollar\b|[$£€]\d)", price_comma, text, flags=re.IGNORECASE)
    text = text.strip(" ,;:-")
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    if text[-1] not in ".!?":
        text += "."
    return text


def norm_words(text):
    """The words of a text in lower case, without punctuation (for comparing)."""
    return re.findall(r"[a-z0-9']+", str(text).lower())


# ----------------------------------------------------------------- scoring a picture (numpy only)

_DCT = {}


def dct_matrix(size=32):
    """The DCT-II matrix of size x size (for the picture fingerprint)."""
    import numpy as np
    if size not in _DCT:
        n = np.arange(size)
        _DCT[size] = np.cos(np.pi * (2 * n[None, :] + 1) * n[:, None] / (2 * size)).astype(np.float32)
    return _DCT[size]


def sharpness(gray):
    """How sharp a grey picture (2-D array) is: the variance of its Laplacian (edges); blurry pictures score low."""
    import numpy as np
    g = gray.astype(np.float32)
    lap = g[1:-1, :-2] + g[1:-1, 2:] + g[:-2, 1:-1] + g[2:, 1:-1] - 4 * g[1:-1, 1:-1]
    return float(lap.var())


def fingerprint(gray):
    """A 64-bit perceptual fingerprint (pHash) of a grey picture: pictures that look alike have close fingerprints."""
    import numpy as np
    from PIL import Image
    small = np.asarray(Image.fromarray(gray).resize((32, 32), Image.BILINEAR), dtype=np.float32)
    d = dct_matrix() @ small @ dct_matrix().T
    low = d[:8, :8].flatten()
    bits = low > np.median(low[1:])
    return int("".join("1" if b else "0" for b in bits), 2)


def distance(a, b):
    """How many of the 64 bits of two fingerprints differ."""
    return (a ^ b).bit_count()


def score(gray):
    """{"sharp", "bright", "hash"} of a grey picture."""
    return {"sharp": sharpness(gray), "bright": float(gray.mean()), "hash": fingerprint(gray)}


def gray_of(frame):
    """A small grey copy of a video frame (at most SCORE_SIDE pixels on its long side), for scoring."""
    w, h = frame.width, frame.height
    scale = min(1.0, SCORE_SIDE / max(w, h))
    w, h = max(2, int(w * scale) // 2 * 2), max(2, int(h * scale) // 2 * 2)
    return frame.to_ndarray(format="gray", width=w, height=h)


# ----------------------------------------------------------------- reading videos (PyAV, which includes FFmpeg)

def network_options():
    """FFmpeg's settings for reading a video from the web: the certificate list (certifi's, or the one the
    computer names), a proxy when the computer uses one, reconnecting, and the kit's plain name."""
    options = {"user_agent": USER_AGENT, "reconnect": "1", "reconnect_delay_max": "10",
               "reconnect_on_http_error": "429,5xx"}
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if not ca:
        try:
            import certifi
            ca = certifi.where()
        except ImportError:
            ca = ""
    if ca:
        options["ca_file"] = ca
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy and proxy.startswith("http://"):
        options["http_proxy"] = proxy
    return options


def open_media(source):
    """Open a video or sound file, or an https address, with PyAV."""
    import av
    if source.startswith(("https://", "http://")):
        return av.open(source, options=network_options(), timeout=60)
    return av.open(source)


def video_stream(container, source):
    """The first video stream of a container (decoded with several threads), or a VideoProblem."""
    if not container.streams.video:
        raise VideoProblem(f"{os.path.basename(source)} has no pictures (it is a sound file).")
    stream = container.streams.video[0]
    stream.thread_type = "AUTO"
    return stream


def stream_start(stream):
    """The time of the first frame of a stream, in seconds (most videos: 0)."""
    return float(stream.start_time * stream.time_base) if stream.start_time is not None else 0.0


def picture_of(frame):
    """A video frame as an upright picture (the video's rotation flag applied, as players do), at most LONG_SIDE
    pixels on its long side."""
    from PIL import Image
    img = frame.to_image()
    turn = (frame.rotation or 0) % 360
    if turn:
        img = img.rotate(turn, expand=True)              # PyAV gives the turn anticlockwise, as FFmpeg's players
    img.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
    return img.convert("RGB")


def scan(source, watch=None):
    """Look at about SAMPLE_RATE pictures a second of a whole video file: [{"t", "pts", "sharp", "bright",
    "hash"}] and the video's length in seconds. Each picture looked at is also given to watch (an OverlayWatch,
    which looks for date stamps and logos), when given."""
    samples = []
    with open_media(source) as container:
        stream = video_stream(container, source)
        start = stream_start(stream)
        due = 0.0
        for frame in container.decode(stream):
            if frame.time is None:
                continue
            t = frame.time - start
            if t + 1e-6 < due:
                continue
            due = math.floor(t * SAMPLE_RATE + 1e-6) / SAMPLE_RATE + 1 / SAMPLE_RATE
            samples.append(dict(score(gray_of(frame)), t=t, pts=frame.pts))
            if watch is not None:
                watch.add(frame)
        length = float(container.duration / 1e6) if container.duration else (samples[-1]["t"] if samples else 0)
    return samples, length


def grab(source, wanted):
    """{pts: upright picture} of the frames whose pts are in wanted (a second pass through the video)."""
    found = {}
    wanted = set(wanted)
    if not wanted:
        return found
    with open_media(source) as container:
        stream = video_stream(container, source)
        for frame in container.decode(stream):
            if frame.pts in wanted and frame.pts not in found:
                found[frame.pts] = picture_of(frame)
                if len(found) == len(wanted):
                    break
    return found


def blur_limit(samples):
    """The sharpness below which a picture of this video counts as blurry: SHARP_SHARE of the usual (median)
    sharpness of its pictures that are not dark, and never below SHARP_LEAST."""
    values = sorted(s["sharp"] for s in samples if s["bright"] >= DARK)
    if not values:
        return SHARP_LEAST
    return max(SHARP_LEAST, SHARP_SHARE * values[len(values) // 2])


def choose(samples, every):
    """The pictures to keep from scan(): dark and blurry ones left out, the sharpest one in each stretch of every
    seconds, and pictures that look the same as the one before joined into one (the sharper is kept; "span" says
    which stretch of the video it stands for). A picture that looks the same as an earlier kept one is left out.
    Returns (kept, counts) where counts says how many were left out and why."""
    limit = blur_limit(samples)
    counts = {"dark": 0, "blurry": 0, "same": 0}
    windows = {}
    for s in samples:
        windows.setdefault(int(s["t"] // every), []).append(s)
    kept = []
    for key in sorted(windows):
        group = windows[key]
        usable = [s for s in group if s["bright"] >= DARK]
        if not usable:
            counts["dark"] += 1
            continue
        best = max(usable, key=lambda s: s["sharp"])
        if best["sharp"] < limit:
            counts["blurry"] += 1
            continue
        best = dict(best, span=(best["t"], best["t"]))
        if kept and distance(kept[-1]["hash"], best["hash"]) <= SAME_BITS:
            last = kept[-1]
            span = (last["span"][0], best["t"])
            kept[-1] = dict(best if best["sharp"] > last["sharp"] else last, span=span)
            counts["same"] += 1
            continue
        if any(distance(k["hash"], best["hash"]) <= SAME_BITS for k in kept[:-1]):
            counts["same"] += 1
            continue
        kept.append(best)
    return kept, counts


def spot(container, stream, start, point, watch=None):
    """The sharpest picture that is not dark in about SPOT_LENGTH seconds from point (seconds) of an open video:
    (scores with "t", the frame), or (None, why: "dark" or "blurry"). The pictures looked at also go to watch
    (an OverlayWatch), when given."""
    try:
        container.seek(int((point + start) / stream.time_base), stream=stream, backward=True)
    except Exception:  # noqa: BLE001 - a spot that cannot be reached is left out
        return None, "blurry"
    best, best_frame, due, any_light = None, None, point, False
    for frame in container.decode(stream):
        if frame.time is None:
            continue
        t = frame.time - start
        if t + 1e-6 < due:
            continue
        if t > point + SPOT_LENGTH:
            break
        due = t + 1 / SAMPLE_RATE
        values = dict(score(gray_of(frame)), t=t)
        if watch is not None:
            watch.add(frame)
        if values["bright"] < DARK:
            continue
        any_light = True
        if best is None or values["sharp"] > best["sharp"]:
            best, best_frame = values, frame
    if best is None:
        return None, "blurry" if any_light else "dark"
    if best["sharp"] < SHARP_LEAST:
        return None, "blurry"
    return best, best_frame


def spots(source, points, step, watch=None):
    """Read an online video only around the given times (seconds): at each one, jump there, look at about
    SPOT_LENGTH seconds of it and keep the sharpest picture that is not dark or blurry and does not look like one
    kept before; when there is none, try once more a third of step later. Returns ([{"t", "sharp", "hash",
    "picture", "span"}], counts of what was left out, length in seconds). watch: see spot()."""
    kept, counts = [], {"dark": 0, "blurry": 0, "same": 0}
    with open_media(source) as container:
        stream = video_stream(container, source)
        start = stream_start(stream)
        length = float(container.duration / 1e6) if container.duration else 0.0
        for point in points:
            why = ""
            for when in (point, point + step / 3):
                if length and when > length - 0.5:
                    break
                best, frame = spot(container, stream, start, when, watch)
                if best is None:
                    why = frame
                    continue
                if any(distance(k["hash"], best["hash"]) <= SAME_BITS for k in kept):
                    why = "same"
                    continue
                kept.append(dict(best, picture=picture_of(frame), span=(best["t"], best["t"])))
                why = ""
                break
            if why:
                counts[why] += 1
    return kept, counts, length


# ----------------------------------------------------------------- the sound tracks

def audio_tracks(source):
    """The sound tracks of a video: [{"number" (1, 2 ... among the sound tracks), "title", "language",
    "described" (True when marked as audio description by its flag or its title), "default"}]."""
    tracks = []
    with open_media(source) as container:
        for number, stream in enumerate(container.streams.audio, 1):
            meta = {k.lower(): v for k, v in dict(stream.metadata).items()}
            title = meta.get("title") or ""
            handler = meta.get("handler_name") or meta.get("handler") or ""
            flags = int(stream.disposition)
            words = set(norm_words(f"{title} {handler}"))
            named = " ".join(norm_words(f"{title} {handler}"))
            described = bool(flags & 256) or any(w in words for w in AD_TRACK_WORDS if " " not in w) or \
                any(w in named for w in AD_TRACK_WORDS if " " in w)
            if handler in ("SoundHandler", "Core Media Audio") and not title:
                handler = ""                               # FFmpeg's and Apple's default names say nothing
            tracks.append({"number": number, "title": title or handler, "language": stream.language or "",
                           "described": described, "default": bool(flags & 1)})
    return tracks


def tracks_text(tracks):
    """The sound tracks in plain words, one per line."""
    if not tracks:
        return "  This video has no sound track."
    lines = []
    for t in tracks:
        bits = [t["title"] or "no title", f"language {t['language']}" if t["language"] not in ("", "und") else
                "language not given"]
        if t["described"]:
            bits.append("marked as audio description")
        lines.append(f"  Sound track {t['number']}: " + ", ".join(bits) + ".")
    return "\n".join(lines)


def decode_sound(source, number=1):
    """Sound track number (1, 2 ... among the sound tracks) of a video or sound file as 16 kHz mono samples
    (numpy float32), as the speech recogniser wants; None when there is no such track."""
    import av
    import numpy as np
    with open_media(source) as container:
        if len(container.streams.audio) < number:
            return None
        stream = container.streams.audio[number - 1]
        resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
        chunks = []
        for frame in container.decode(stream):
            for out in resampler.resample(frame):
                chunks.append(out.to_ndarray().reshape(-1))
        for out in resampler.resample(None):
            chunks.append(out.to_ndarray().reshape(-1))
    if not chunks:
        return None
    return np.concatenate(chunks).astype(np.float32) / 32768.0


# ----------------------------------------------------------------- speech into text (faster-whisper)

def cuda_libraries():
    """On Windows, let faster-whisper's engine (CTranslate2) find NVIDIA's cuBLAS and cuDNN, which come with the
    kit's PyTorch: loading PyTorch loads them."""
    if os.name != "nt":
        return
    try:
        import torch
        lib = os.path.join(os.path.dirname(torch.__file__), "lib")
        if os.path.isdir(lib):
            os.add_dll_directory(lib)
    except Exception:  # noqa: BLE001, S110 - without PyTorch the processor is used
        pass


class Listener:
    """The speech recogniser, loaded once when first needed (on the graphics card in float16 when it can, otherwise
    on the processor in int8)."""

    def __init__(self, model_name=WHISPER_DEFAULT, language="en", say=print):
        """Remember the choice; nothing is loaded yet. An English-only model is swapped for the default one when
        the language is not English."""
        if model_name.endswith(".en") and language not in ("", "en"):
            model_name = WHISPER_DEFAULT
        self.name, self.language, self.say = model_name, language or None, say
        self.model, self.device = None, None

    def folder(self):
        """Download the model at its pinned commit into the kit's work folder (once); returns the folder."""
        from huggingface_hub import snapshot_download
        repo, revision, size = WHISPER_MODELS[self.name]
        folder = os.path.join(WORK, f"whisper-{self.name}")
        if not os.path.exists(os.path.join(folder, "model.bin")):
            self.say(f"  Downloading the speech recogniser ({self.name}, {size}; once).")
        os.makedirs(WORK, exist_ok=True)
        snapshot_download(repo, revision=revision, local_dir=folder)
        return folder

    def load(self, device):
        """Load the model on device ("cuda" or "cpu")."""
        from faster_whisper import WhisperModel
        folder = self.folder()
        if device == "cuda":
            self.model = WhisperModel(folder, device="cuda", compute_type="float16")
        else:
            self.model = WhisperModel(folder, device="cpu", compute_type="int8",
                                      cpu_threads=max(1, (os.cpu_count() or 2) // 2))
        self.device = device

    def words(self, sound):
        """The words in sound (16 kHz samples): [{"start", "end", "text", "raw", "last"}] ("raw": the word with
        the recogniser's spacing; "last": the last word of a stretch of speech). Stretches that are probably not
        speech are left out."""
        if sound is None or len(sound) < 1600:
            return []
        if self.model is None:
            cuda_libraries()
            import ctranslate2
            self.load("cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu")
        try:
            return self._words(sound)
        except Exception as e:  # the graphics card could not be used: the processor is
            if self.device != "cuda":
                raise
            self.say(f"  The graphics card could not run the speech recogniser ({str(e).splitlines()[0][:120]}); "
                     "using the processor instead (slower).")
            self.model = None
            gc.collect()
            self.load("cpu")
            return self._words(sound)

    def _words(self, sound):
        """words() on the loaded model."""
        segments, _ = self.model.transcribe(sound, language=self.language, word_timestamps=True, vad_filter=True,
                                            beam_size=5, condition_on_previous_text=False)
        out = []
        for segment in segments:
            if segment.no_speech_prob > 0.6 and segment.avg_logprob < -1.0:
                continue
            words = [w for w in (segment.words or []) if w.word.strip()]
            for n, w in enumerate(words):
                out.append({"start": float(w.start), "end": float(w.end), "text": w.word.strip(), "raw": w.word,
                            "last": n == len(words) - 1})
        return out

    def close(self):
        """Let the model go (frees its memory before the picture model is loaded for drafts)."""
        self.model = None
        gc.collect()


def joined(words):
    """The text of words as the recogniser spaced it (" twenty" "-nine" -> "twenty-nine")."""
    if all("raw" in w for w in words):
        return " ".join("".join(w["raw"] for w in words).split())
    return " ".join(w["text"] for w in words)


def phrases(words, pause=PAUSE):
    """Join words into phrases ({"start", "end", "text"}): a phrase ends at a full stop, question or exclamation
    mark, at a pause of more than pause seconds, or at the end of a stretch of speech."""
    out, current = [], []
    for n, w in enumerate(words):
        current.append(w)
        after = words[n + 1] if n + 1 < len(words) else None
        if (w["text"].endswith((".", "?", "!")) or w.get("last") or after is None or
                after["start"] - w["end"] > pause):
            out.append({"start": current[0]["start"], "end": current[-1]["end"], "text": joined(current)})
            current = []
    return out


def align(frames, said, after=SPEAK_AFTER):
    """For each kept picture (with "span": the stretch of video it stands for), the phrases said at that time, or
    else the first phrase started up to `after` seconds later when no other kept picture comes first (people look,
    then speak). Sets frame["said"] to [phrases] (maybe empty)."""
    starts = sorted(f["span"][0] for f in frames)
    for frame in frames:
        a, b = frame["span"]
        during = [p for p in said if p["start"] <= b + 0.25 and p["end"] >= a - 0.25]
        if not during:
            later = [p for p in said if b < p["start"] <= b + after]
            if later:
                first = later[0]
                if not any(b < s <= first["start"] for s in starts):
                    during = [first]
        frame["said"] = during
    return frames


def separate(described, main, shared=AD_SHARED, near=AD_NEAR):
    """The narrator's phrases: the phrases of the description track (described) that share less than `shared` of
    their words with the plain soundtrack's words (main) said within `near` seconds."""
    out = []
    for p in described:
        words = norm_words(p["text"])
        if not words:
            continue
        nearby = set()
        for w in main:
            if w["start"] <= p["end"] + near and w["end"] >= p["start"] - near:
                nearby.update(norm_words(w["text"]))
        share = sum(1 for w in words if w in nearby) / len(words)
        if share < shared:
            out.append(p)
    return out


def transcript_text(name, said):
    """The transcript of one video, with times, for transcript.txt."""
    lines = [f"{name} (made {datetime.datetime.now():%d %B %Y})"]           # noqa: DTZ005 - the computer's time
    lines += [f"[{clock(p['start'])} to {clock(p['end'])}] {p['text']}" for p in said] or ["(nothing was said)"]
    return "\n".join(lines)


# ----------------------------------------------------------------- audio description lines

TIME = r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})"


def seconds_of(match, first):
    """Seconds from a matched subtitle time (groups starting at first: hours, minutes, seconds, fraction)."""
    hours, minutes, secs, frac = match.group(first, first + 1, first + 2, first + 3)
    return int(hours or 0) * 3600 + int(minutes) * 60 + int(secs) + int(frac.ljust(3, "0")) / 1000


def read_description_text(path):
    """The lines of a WebVTT or SRT description file: [{"start", "end", "text"}] (tags such as <v Narrator> and
    {\\an8} left out)."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        text = f.read().replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for block in re.split(r"\n\s*\n", text):
        rows = [r for r in block.split("\n") if r.strip()]
        for n, row in enumerate(rows):
            m = re.match(rf"\s*{TIME}\s*-->\s*{TIME}", row)
            if m:
                words = " ".join(rows[n + 1:])
                words = re.sub(r"<[^>]*>|\{[^}]*\}", "", words)
                words = " ".join(words.replace("&amp;", "&").replace("&nbsp;", " ").split())
                if words:
                    lines.append({"start": seconds_of(m, 1), "end": seconds_of(m, 5), "text": words})
                break
    return sorted(lines, key=lambda x: x["start"])


def narrator_lines(lines, join_gap=2.0):
    """Tidy the narrator's lines: lines that are pieces of one sentence are joined (one not ending with . ! or ?
    followed within join_gap seconds by the next), and lines under 3 words or that are only a name are left out."""
    joined = []
    for line in lines:
        text = " ".join(line["text"].split())
        if joined and not joined[-1]["text"].endswith((".", "!", "?")) and \
                line["start"] - joined[-1]["end"] <= join_gap:
            joined[-1] = {"start": joined[-1]["start"], "end": line["end"],
                          "text": joined[-1]["text"] + " " + text}
        else:
            joined.append(dict(line, text=text))
    kept = []
    for line in joined:
        words = re.findall(r"[^\W\d_][\w'-]*|\d+", line["text"])
        if len(words) < 3:
            continue
        if len(words) <= 4 and all(w[0].isupper() for w in words):
            continue                                       # only a name ("Mary Ann Smith.")
        kept.append(dict(line, text=tidy(line["text"], spoken=False)))
    return kept


# ----------------------------------------------------------------- faces

class FaceBlur:
    """Blur faces with OpenCV's YuNet face finder. The small model file is downloaded once into the kit's work
    folder and checked against its pinned SHA-256."""

    def __init__(self, say=print):
        """Get the model file (once) and remember it; the finder is made when first used."""
        import cv2  # noqa: F401 - fail early, in plain words, when OpenCV is missing
        repo, revision, name, digest = YUNET
        folder = os.path.join(WORK, "face-finder")
        path = os.path.join(folder, name)
        if not os.path.exists(path) or self.sha256(path) != digest:
            from huggingface_hub import hf_hub_download
            say("  Downloading the face finder (YuNet, 0.2 MB; once).")
            os.makedirs(folder, exist_ok=True)
            hf_hub_download(repo, name, revision=revision, local_dir=folder)
            if self.sha256(path) != digest:
                os.remove(path)
                raise VideoProblem("The face finder that was downloaded is not the expected file, so faces cannot "
                                   "be blurred. Try again later.")
        self.path, self.finder = path, None
        self.faces = self.pictures = 0

    @staticmethod
    def sha256(path):
        """The SHA-256 of a file, as hexadecimal text."""
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def __call__(self, img):
        """img (a Pillow picture) with every face found blurred beyond recognition; counts them."""
        import cv2
        import numpy as np
        from PIL import Image
        bgr = np.ascontiguousarray(np.asarray(img)[:, :, ::-1])
        h, w = bgr.shape[:2]
        if self.finder is None:
            self.finder = cv2.FaceDetectorYN.create(self.path, "", (w, h), 0.6, 0.3, 5000)
        self.finder.setInputSize((w, h))
        _, faces = self.finder.detect(bgr)
        if faces is None or len(faces) == 0:
            return img
        for face in faces:
            x, y, fw, fh = (float(v) for v in face[:4])
            grow = 0.25
            x0, y0 = int(max(0, x - fw * grow)), int(max(0, y - fh * grow))
            x1, y1 = int(min(w, x + fw * (1 + grow))), int(min(h, y + fh * (1 + grow)))
            if x1 - x0 < 4 or y1 - y0 < 4:
                continue
            part = bgr[y0:y1, x0:x1]
            tiny = cv2.resize(part, (max(1, (x1 - x0) // 16), max(1, (y1 - y0) // 16)), interpolation=cv2.INTER_AREA)
            part = cv2.resize(tiny, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
            k = max(3, ((min(x1 - x0, y1 - y0) // 4) | 1))
            bgr[y0:y1, x0:x1] = cv2.GaussianBlur(part, (k, k), 0)
            self.faces += 1
        self.pictures += 1
        return Image.fromarray(bgr[:, :, ::-1].copy())


# ----------------------------------------------------------------- date stamps, logos and other burned-in overlays

class OverlayWatch:
    """Keeps running totals over the pictures of one video, at a small size (OVERLAY_SIDE), to find what stays
    fixed while the picture behind it changes: per spot, the sum and sum of squares of its colour (for how much it
    varies) and how often it is an edge. Only totals are kept, so long videos take no more memory."""

    def __init__(self):
        """Nothing seen yet."""
        self.count, self.turn = 0, 0
        self.sum = self.squares = self.edges = None

    def add(self, frame):
        """Add one video frame (PyAV) to the totals."""
        import numpy as np
        w, h = frame.width, frame.height
        scale = min(1.0, OVERLAY_SIDE / max(w, h))
        w, h = max(8, int(w * scale) // 2 * 2), max(8, int(h * scale) // 2 * 2)
        rgb = frame.to_ndarray(format="rgb24", width=w, height=h).astype(np.float32)
        if self.sum is None or self.sum.shape != rgb.shape:
            if self.sum is not None:                     # the size changed in the middle: start again
                self.count = 0
            self.sum = np.zeros(rgb.shape, np.float64)
            self.squares = np.zeros(rgb.shape, np.float64)
            self.edges = np.zeros(rgb.shape[:2], np.int32)
        self.turn = (frame.rotation or 0) % 360
        self.sum += rgb
        self.squares += rgb * rgb
        self.edges += edge_map(rgb.mean(axis=2)) > OVERLAY_EDGE
        self.count += 1


def edge_map(gray):
    """How strong the edge is at each spot of a grey picture (2-D array): the change in brightness across 2 pixels,
    across and down, added."""
    import numpy as np
    across, down = np.zeros_like(gray), np.zeros_like(gray)
    across[:, 1:-1] = np.abs(gray[:, 2:] - gray[:, :-2])
    down[1:-1, :] = np.abs(gray[2:, :] - gray[:-2, :])
    return across + down


def find_overlays(watch):
    """The burned-in overlays of a video from its OverlayWatch: (boxes, note). boxes: [(x0, y0, x1, y1)] as shares
    of the upright picture (0 to 1); note: why none were looked for, in plain words, or "".

    How: a spot is part of an overlay when it stays the same over the video (its colour hardly varies) and is an
    edge in most pictures (the outline of letters and logos), or when it is an edge in nearly every picture
    (see-through logos). This only means something when the rest of the picture changes, so when most of the
    picture stays the same (a still camera) nothing is looked for. The spots are joined into marks (a date stamp's
    changing seconds join its fixed digits); only compact marks near an edge or corner of the picture are kept,
    each at most OVERLAY_EACH of the picture and all at most OVERLAY_ALL (the smaller ones first)."""
    import cv2
    import numpy as np
    if watch is None or watch.count < OVERLAY_LEAST:
        return [], "the video is too short to tell what stays fixed, so none were looked for"
    n = watch.count
    mean = watch.sum / n
    spread_ = np.sqrt(np.maximum(watch.squares / n - mean * mean, 0)).max(axis=2)
    edges = watch.edges / n
    turns = watch.turn // 90
    if turns:                                            # the same turn picture_of() gives the stills
        spread_, edges = np.rot90(spread_, turns), np.rot90(edges, turns)
    moving = float((spread_ > OVERLAY_MOVING_STD).mean())
    if moving < OVERLAY_MOVING:
        return [], (f"the picture hardly changes (the camera barely moved: only {round(moving * 100)}% of the "
                    "picture changed), so a date stamp or logo cannot be told apart from the scene; none were "
                    "looked for")
    marks = ((spread_ < OVERLAY_STILL_STD) & (edges >= OVERLAY_EDGE_STILL)) | (edges >= OVERLAY_EDGE_ALWAYS)
    marks = np.ascontiguousarray(marks.astype(np.uint8))
    h, w = marks.shape
    size = max(3, round(min(w, h) * OVERLAY_JOIN)) | 1
    joined = cv2.morphologyEx(marks, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (size, size)))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
    found = []
    for label in range(1, count):
        x, y, bw, bh, _area = (int(v) for v in stats[label])
        share = bw * bh / (w * h)
        seeds = int(marks[labels == label].sum())
        if share < OVERLAY_LEAST_SHARE or share > OVERLAY_EACH or min(bw, bh) < 3 or seeds < 6:
            continue
        gap = min(x / w, y / h, (w - x - bw) / w, (h - y - bh) / h)
        if gap > OVERLAY_NEAR_EDGE:
            continue
        found.append((share, (x / w, y / h, (x + bw) / w, (y + bh) / h)))
    boxes, total = [], 0.0
    for share, box in sorted(found):
        if total + share > OVERLAY_ALL:
            break
        total += share
        boxes.append(pad_box(box, OVERLAY_PAD + 1 / min(w, h)))
    return boxes, ""


def pad_box(box, pad):
    """A box (shares of the picture) made bigger by pad on every side, inside the picture."""
    x0, y0, x1, y1 = box
    return (max(0.0, x0 - pad), max(0.0, y0 - pad), min(1.0, x1 + pad), min(1.0, y1 + pad))


def overlay_box(text):
    """A box given on the command line as "x,y,w,h" in percent of the picture (from the top left corner) ->
    (x0, y0, x1, y1) as shares; ValueError when it is not one."""
    parts = [float(p) for p in str(text).replace("%", "").split(",")]
    if len(parts) != 4:
        raise ValueError("give four numbers: x,y,width,height in percent")
    x, y, bw, bh = parts
    if min(parts) < 0 or bw <= 0 or bh <= 0 or x + bw > 100.001 or y + bh > 100.001:
        raise ValueError("the box must lie inside the picture (0 to 100 percent)")
    return (x / 100, y / 100, min(1.0, (x + bw) / 100), min(1.0, (y + bh) / 100))


def where(box):
    """Where a box is, in plain words: "the top right corner", "a band along the bottom", "the left edge"."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    across = "left" if cx < 1 / 3 else "right" if cx > 2 / 3 else ""
    down = "top" if cy < 1 / 3 else "bottom" if cy > 2 / 3 else ""
    if x1 - x0 >= 0.5 and down:
        return f"a band along the {down}"
    if y1 - y0 >= 0.5 and across:
        return f"a band down the {across} side"
    if across and down:
        return f"the {down} {across} corner"
    if down:
        return f"the {down} edge, in the middle"
    if across:
        return f"the {across} edge, half way down"
    return "the middle of the picture"


def percent(share):
    """A share of the picture for people: "about 6%" ("less than 1%" for small ones)."""
    return "less than 1%" if share < 0.005 else f"about {max(1, round(share * 100))}%"


def centred_crop(boxes):
    """The largest rectangle that keeps the middle of the picture, leaves out every box (shares of the picture) and
    whose shape (width against height) differs from the picture's by at most CROP_ASPECT: (x0, y0, x1, y1) as
    shares, or None when there is none. Only the sides with a box are cut (a logo at the top cuts the top, not the
    bottom too); when the shape has to be kept, the narrowed side stays as near the middle as it can. A box that
    covers the middle of the picture cannot be cropped off."""
    lefts = {0.0} | {bx[2] for bx in boxes if bx[2] <= 0.5}
    rights = {1.0} | {bx[0] for bx in boxes if bx[0] >= 0.5}
    tops = {0.0} | {bx[3] for bx in boxes if bx[3] <= 0.5}
    bottoms = {1.0} | {bx[1] for bx in boxes if bx[1] >= 0.5}

    def fit(lo, hi, size):
        """A stretch of length size inside lo..hi, as near the middle (0.5) as it can be."""
        start = min(max(0.5 - size / 2, lo), hi - size)
        return start, start + size
    best, best_area = None, 0.0
    for x0 in lefts:
        for x1 in rights:
            for y0 in tops:
                for y1 in bottoms:
                    if not all(bx[2] <= x0 or bx[0] >= x1 or bx[3] <= y0 or bx[1] >= y1 for bx in boxes):
                        continue
                    w, h = x1 - x0, y1 - y0             # as shares, so w / h is the shape against the picture's
                    left, right, top, bottom = x0, x1, y0, y1
                    if w > h * CROP_ASPECT:              # making a side shorter still leaves out every box
                        left, right = fit(x0, x1, h * CROP_ASPECT)
                    elif h > w * CROP_ASPECT:
                        top, bottom = fit(y0, y1, w * CROP_ASPECT)
                    area = (right - left) * (bottom - top)
                    if area > best_area:
                        best, best_area = (left, top, right, bottom), area
    return best


class Overlays:
    """What is done about the burned-in overlays of one video: how ("keep", "crop" or "fill"), the boxes given
    by hand (shares of the picture), and, once settle() has run, the boxes found and the crop or fill used. Called
    with a still picture, it returns the picture with the overlays removed."""

    def __init__(self, how="keep", manual=()):
        """Ready to watch the video (an OverlayWatch is made only when something is to be removed)."""
        self.how, self.manual = how, [tuple(b) for b in manual]
        self.watch = OverlayWatch() if how != "keep" else None
        self.found, self.note, self.used, self.crop, self.settled = [], "", how, None, False
        self.lost = 0.0                                  # the share cropping would have lost (when filled instead)

    def settle(self):
        """Find the overlays in what was watched and decide between cropping and filling in."""
        self.settled = True
        if self.how == "keep":
            return
        self.found, self.note = find_overlays(self.watch)
        boxes = self.found + self.manual
        if not boxes:
            self.used = "keep"
            return
        if self.how == "crop":
            crop = centred_crop(boxes)
            area = (crop[2] - crop[0]) * (crop[3] - crop[1]) if crop else 0.0
            if area >= 1 - CROP_MOST_LOST:
                self.crop, self.used = crop, "crop"
            else:
                self.used, self.lost = "fill", 1 - area
        self.watch = None                                # the totals are no longer needed

    def __call__(self, img):
        """img (a Pillow picture) with the overlays cropped off or filled in."""
        if not self.settled:
            self.settle()
        boxes = self.found + self.manual
        if self.used == "keep" or not boxes:
            return img
        w, h = img.size
        if self.used == "crop":
            x0, y0, x1, y1 = self.crop
            return img.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))
        import cv2
        import numpy as np
        from PIL import Image
        bgr = np.ascontiguousarray(np.asarray(img)[:, :, ::-1])
        mask = np.zeros((h, w), np.uint8)
        grow = max(2, round(min(w, h) * 0.006))         # a little bigger, to cover soft outlines
        for x0, y0, x1, y1 in boxes:
            mask[max(0, int(y0 * h) - grow):min(h, math.ceil(y1 * h) + grow),
                 max(0, int(x0 * w) - grow):min(w, math.ceil(x1 * w) + grow)] = 255
        filled = cv2.inpaint(bgr, mask, max(3, round(min(w, h) * 0.01)), cv2.INPAINT_TELEA)
        return Image.fromarray(filled[:, :, ::-1].copy())

    def report(self, name):
        """One line in plain words for the summary and OVERLAYS.txt: what was found in the video name and what was
        done; "" when nothing was asked for."""
        if self.how == "keep":
            return ""
        if not self.settled:
            self.settle()
        parts = [f"in {where(b)}, {percent((b[2] - b[0]) * (b[3] - b[1]))} of the picture" for b in self.found]
        parts += [f"your box in {where(b)}, {percent((b[2] - b[0]) * (b[3] - b[1]))} of the picture"
                  for b in self.manual]
        if self.found:
            text = f"{name}: found {plural(len(self.found), 'date stamp or logo', 'date stamps or logos')}"
        elif self.note:
            text = f"{name}: {self.note}"
        else:
            text = f"{name}: no date stamp or logo found"
        if self.manual:
            text += f"; {plural(len(self.manual), 'box', 'boxes')} given by you"
        if parts:
            text += " (" + "; ".join(parts) + ")"
        if self.used == "crop":
            x0, y0, x1, y1 = self.crop
            text += f". Cropped off: the stills keep {round((x1 - x0) * (y1 - y0) * 100)}% of the picture."
        elif self.used == "fill" and self.how == "crop":
            text += (f". Filled in, because cropping would have lost {round(self.lost * 100)}% of the picture "
                     "(check the filled spots: they can look smudged).")
        elif self.used == "fill":
            text += ". Filled in (check the filled spots: they can look smudged)."
        else:
            text += ". Nothing was changed."
        return text


def overlay_report(out, overlays, name, lines, say):
    """Say what overlays found in the video name and what was done, and write it into OVERLAYS.txt in out and
    lines (for the summary). Nothing when overlays is None or nothing was asked for."""
    if overlays is None:
        return
    text = overlays.report(name)
    if text:
        say("  " + text)
        lines.append(text)
        with open(os.path.join(out, OVERLAYS_FILE), "a", encoding="utf-8") as f:
            f.write(text + "\n")


def check_overlays(how, boxes):
    """VideoProblem when the overlay choice is not one of OVERLAY_CHOICES, or boxes are given with "keep"."""
    if how not in OVERLAY_CHOICES:
        raise VideoProblem(f"The overlay choice must be one of {', '.join(OVERLAY_CHOICES)}, not {how}.")
    if boxes and how == "keep":
        raise VideoProblem("A box to remove (--overlay-box) needs --overlays crop or --overlays fill.")


def save_picture(img, path, faces=None, overlays=None):
    """Save a picture as a JPEG: date stamps and logos removed first when overlays (an Overlays) is given, then
    faces blurred when faces (a FaceBlur) is given, so faces are blurred in the picture that is saved (filling in
    could otherwise bring back part of a face beside a logo)."""
    if overlays is not None:
        img = overlays(img)
    if faces is not None:
        img = faces(img)
    img.save(path, "JPEG", quality=JPEG_QUALITY)


# ----------------------------------------------------------------- drafts by the kit's picture model

def write_drafts(pictures, say=print):
    """Write a DRAFT description for each picture into <name>.draft.txt with the kit's own picture model (the 4B
    model train.py trains, loaded the same way). Needs an NVIDIA graphics card. Returns how many were written."""
    if not pictures:
        return 0
    try:
        import torch
    except ImportError:
        say("  Drafts need the training tools (kit\\requirements.txt): none were written.")
        return 0
    if not torch.cuda.is_available():
        say("  Drafts need an NVIDIA graphics card: none were written.")
        return 0
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import train
    say(f"  Writing draft descriptions for {plural(len(pictures), 'picture')} with the kit's picture model "
        "(the first time, the model is downloaded: about 9 GB).")
    os.makedirs(WORK, exist_ok=True)
    folder = train.download_model("4b", WORK)
    model, processor = train.load_model(folder)
    written = 0
    for number, picture in enumerate(pictures, 1):
        text = train.describe(model, processor, {"picture": picture, "question": DRAFT_QUESTION}, "cuda")
        text = tidy(text, spoken=False)
        if text:
            write_text(os.path.splitext(picture)[0] + ".draft.txt", text)
            written += 1
        if number % 10 == 0 or number == len(pictures):
            say(f"    {number} of {len(pictures)} drafts written")
    del model, processor
    train.free()
    return written


# ----------------------------------------------------------------- licences of online videos

def licence_of(text):
    """(kind, name) of a licence given as an address or words: kind is "pd" (public domain), "cc0", "by",
    "by-sa", "nc" (non-commercial), "nd" (no changes allowed) or "unknown"; name is for people ("CC BY 4.0")."""
    lower = str(text or "").lower().strip()
    if not lower:
        return "unknown", ""
    version = re.search(r"(\d\.\d)", lower)
    version = f" {version.group(1)}" if version else ""
    if re.search(r"(?:^|[/\s_-])nc(?:[/\s_-]|$)|noncommercial|non-commercial", lower):
        return "nc", "a non-commercial licence"
    if re.search(r"(?:^|[/\s_-])nd(?:[/\s_-]|$)|noderiv|no derivatives|no-derivatives", lower):
        return "nd", "a no-changes (ND) licence"
    if "publicdomain/zero" in lower or re.search(r"\bcc0\b|cc-zero|cc zero", lower):
        return "cc0", "CC0"
    if re.search(r"publicdomain|public domain|\bpd-|\bpdm\b|no known copyright", lower):
        return "pd", "Public domain"
    if re.search(r"licenses/by-sa/|\bcc[- ]by[- ]sa\b", lower):
        return "by-sa", f"CC BY-SA{version}"
    if re.search(r"licenses/by/|\bcc[- ]by\b", lower):
        return "by", f"CC BY{version}"
    return "unknown", str(text).strip()[:80]


def check_licence(kind, name, share_alike):
    """None when a licence may be used, otherwise the reason it may not, in plain words."""
    if kind in ("pd", "cc0", "by"):
        return None
    if kind == "by-sa":
        return None if share_alike else (f"its licence is {name}, which is share-alike: use --share-alike to accept "
                                         "it (the stills are then marked share-alike in CREDITS.txt)")
    if kind == "nc":
        return "its licence does not allow commercial use (NC), so it cannot be used for training here"
    if kind == "nd":
        return "its licence does not allow changes (ND), so stills cannot be made from it"
    return ("its licence is not known" + (f" (it says: {name})" if name else " (none is given)") +
            "; only public domain, CC0 and CC BY videos are used")


def get_json(url, params=None, tries=4):
    """A JSON answer from a web address (the kit's plain name as the browser name). When the website says "too
    many requests" or is busy, it waits as long as the website asks (at most a minute) and tries again."""
    import time

    import requests
    for attempt in range(tries):
        r = requests.get(url, params=params, timeout=60, headers={"User-Agent": USER_AGENT})
        if r.status_code in (429, 503) and attempt + 1 < tries:
            wait = r.headers.get("Retry-After", "")
            time.sleep(min(60, int(wait) if wait.isdigit() else 10 * (attempt + 1)))
            continue
        r.raise_for_status()
        return r.json()
    return {}


def strip_html(text):
    """Text without HTML tags."""
    return " ".join(re.sub(r"<[^>]+>", " ", str(text or "")).replace("&amp;", "&").split())


def first(value):
    """The first item of a list, or the value itself."""
    return (value[0] if value else "") if isinstance(value, list) else (value or "")


def online_kind(source):
    """("archive", id), ("commons", "File:..."), ("nasa", id) or None (a file on this computer)."""
    if os.path.exists(source):
        return None
    s = source.strip()
    m = re.match(r"https?://(?:www\.)?archive\.org/(?:details|download|embed)/([^/?#]+)", s)
    if m:
        return "archive", urllib.parse.unquote(m.group(1))
    if s.lower().startswith("archive:"):
        return "archive", s.split(":", 1)[1].strip()
    m = re.match(r"https?://commons\.(?:m\.)?wikimedia\.org/wiki/(File:[^?#]+)", s)
    if m:
        return "commons", urllib.parse.unquote(m.group(1)).replace("_", " ")
    if s.startswith("File:"):
        return "commons", s.replace("_", " ")
    m = re.match(r"https?://images\.nasa\.gov/details/([^?#]+)", s)
    if m:
        return "nasa", urllib.parse.unquote(m.group(1)).strip("/")
    if s.lower().startswith("nasa:"):
        return "nasa", s.split(":", 1)[1].strip()
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,99}", s) and not s.lower().endswith(VIDEO_ENDINGS):
        return "archive", s                                    # a bare archive.org identifier
    return None


ARCHIVE_FORMATS = ("h.264", "MPEG4", "h.264 HD", "512Kb MPEG4", "HiRes MPEG4", "WebM", "Ogg Video")


def archive_item(identifier, share_alike):
    """An archive.org item as a video to read: {"site", "id", "title", "creator", "licence", "kind", "licence_url",
    "page", "video"}; VideoProblem when it is not a usable video or its licence is not accepted."""
    data = get_json(f"https://archive.org/metadata/{urllib.parse.quote(identifier)}")
    meta = data.get("metadata") or {}
    if not meta:
        raise VideoProblem(f"archive.org has no item named {identifier}.")
    title = strip_html(first(meta.get("title"))) or identifier
    collections = meta.get("collection") or []
    collections = [collections] if isinstance(collections, str) else collections
    url = first(meta.get("licenseurl"))
    kind, name = licence_of(url)
    if kind == "unknown" and not url and "prelinger" in [c.lower() for c in collections]:
        kind, name = "pd", "Public domain (Prelinger Archives)"
    if kind == "unknown" and not url and meta.get("rights"):
        kind, name = licence_of(first(meta.get("rights")))
        if kind == "pd":                                       # free-text "public domain" is only a claim
            kind, name = "unknown", strip_html(first(meta.get("rights")))[:80]
    problem = check_licence(kind, name, share_alike)
    if problem:
        raise VideoProblem(f"The archive.org video {title} ({identifier}) is not used: {problem}.")
    files = [f for f in data.get("files", []) if str(f.get("name", "")).lower().endswith(VIDEO_ENDINGS)]
    chosen = None
    for wanted in ARCHIVE_FORMATS:
        chosen = next((f for f in files if f.get("format") == wanted), None)
        if chosen:
            break
    chosen = chosen or (files[0] if files else None)
    if not chosen:
        raise VideoProblem(f"The archive.org item {title} ({identifier}) has no video file.")
    return {"site": "archive.org", "id": identifier, "title": title,
            "creator": strip_html(first(meta.get("creator"))), "licence": name, "kind": kind, "licence_url": url,
            "page": f"https://archive.org/details/{identifier}",
            "video": f"https://archive.org/download/{urllib.parse.quote(identifier)}/"
                     f"{urllib.parse.quote(chosen['name'])}"}


def commons_file(title, share_alike):
    """A Wikimedia Commons video file as a video to read (see archive_item)."""
    data = get_json("https://commons.wikimedia.org/w/api.php",
                    {"action": "query", "titles": title, "prop": "imageinfo|videoinfo", "format": "json",
                     "formatversion": "2", "iiprop": "url|extmetadata|mediatype", "viprop": "derivatives|url"})
    pages = (data.get("query") or {}).get("pages") or []
    if not pages or pages[0].get("missing"):
        raise VideoProblem(f"Wikimedia Commons has no file named {title}.")
    page = pages[0]
    info = (page.get("imageinfo") or [{}])[0]
    meta = info.get("extmetadata") or {}
    def value(key):
        """One field of the file's description, as plain text."""
        return strip_html((meta.get(key) or {}).get("value", ""))
    if info.get("mediatype") not in (None, "VIDEO"):
        raise VideoProblem(f"{title} on Wikimedia Commons is not a video.")
    if value("NonFree").lower() == "true":
        raise VideoProblem(f"{title} on Wikimedia Commons is not used: it is marked as not free.")
    kind, name = licence_of(value("LicenseShortName") or value("License"))
    problem = check_licence(kind, name, share_alike)
    if problem:
        raise VideoProblem(f"{title} on Wikimedia Commons is not used: {problem}.")
    video = info.get("url", "")
    derivatives = ((page.get("videoinfo") or [{}])[0].get("derivatives") or [])
    small = [d for d in derivatives if 360 <= int(d.get("height") or 0) <= 720 and d.get("src")]
    if small:
        video = max(small, key=lambda d: int(d.get("height") or 0))["src"]
    if not video:
        raise VideoProblem(f"{title} on Wikimedia Commons has no video file to read.")
    return {"site": "Wikimedia Commons", "id": page.get("title", title), "title": value("ObjectName") or title,
            "creator": value("Artist"), "licence": name, "kind": kind, "licence_url": value("LicenseUrl"),
            "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"), safe=":/"),
            "video": video}


SITE_KEYS = {"archive.org": "archive", "Wikimedia Commons": "commons", "NASA Images": "nasa"}   # file name starts
NASA_SIZES = ("~medium.mp4", "~mobile.mp4", "~small.mp4", "~large.mp4", "~orig.mp4")


def nasa_video(nasa_id):
    """A NASA Images video as a video to read (see archive_item). NASA's own media are not under copyright; one
    whose title, caption or credit names a copyright, or names someone else as its maker, is refused."""
    found = get_json("https://images-api.nasa.gov/search", {"nasa_id": nasa_id})
    items = (found.get("collection") or {}).get("items") or []
    if not items:
        raise VideoProblem(f"NASA Images has nothing named {nasa_id}.")
    data = (items[0].get("data") or [{}])[0]
    if data.get("media_type") != "video":
        raise VideoProblem(f"{nasa_id} on NASA Images is not a video.")
    words = " ".join(str(data.get(k, "")) for k in ("title", "description", "photographer", "secondary_creator"))
    if "copyright" in words.lower() or "©" in words:
        raise VideoProblem(f"The NASA video {data.get('title', nasa_id)} is not used: it names a copyright (it was "
                           "probably not made by NASA).")
    assets = get_json(f"https://images-api.nasa.gov/asset/{urllib.parse.quote(nasa_id)}")
    hrefs = [i.get("href", "") for i in (assets.get("collection") or {}).get("items", [])]
    video = next((h for size in NASA_SIZES for h in hrefs if h.endswith(size)), None)
    video = video or next((h for h in hrefs if h.lower().endswith(".mp4")), None)
    if not video:
        raise VideoProblem(f"The NASA item {nasa_id} has no MP4 video file.")
    video = urllib.parse.quote(video.replace("http://", "https://", 1), safe=":/~%")
    creator = strip_html(data.get("secondary_creator") or data.get("photographer") or "") or \
        f"NASA {data.get('center', '')}".strip()
    return {"site": "NASA Images", "id": nasa_id, "title": strip_html(data.get("title")) or nasa_id,
            "creator": creator, "licence": "NASA (not under copyright)", "kind": "pd",
            "licence_url": "https://www.nasa.gov/nasa-brand-center/images-and-media/",
            "page": f"https://images.nasa.gov/details/{urllib.parse.quote(nasa_id)}", "video": video}


def online_video(source, share_alike):
    """The video to read for an online address or identifier (see archive_item)."""
    kind, key = online_kind(source)
    if kind == "archive":
        return archive_item(key, share_alike)
    if kind == "commons":
        return commons_file(key, share_alike)
    return nasa_video(key)


def search_archive(words, collection="", most=5, share_alike=False):
    """archive.org identifiers of videos matching words (and in collection, when given) whose licence is public
    domain or CC BY (CC BY-SA too with share_alike), most downloaded first; up to three times most, as some may
    still be refused."""
    licences = ["licenseurl:*publicdomain*", r"licenseurl:*licenses\/by\/*", "collection:prelinger"]
    if share_alike:
        licences.append(r"licenseurl:*licenses\/by-sa\/*")              # "/" must be written "\/" here
    query = f"({words}) AND mediatype:(movies) AND ({' OR '.join(licences)})"
    if collection:
        query += f" AND collection:({collection})"
    data = get_json("https://archive.org/advancedsearch.php",
                    {"q": query, "fl[]": "identifier", "rows": str(max(most, 1) * 3), "sort[]": "downloads desc",
                     "output": "json"})
    if "response" not in data:
        raise VideoProblem(f"archive.org's search did not answer ({str(data.get('error', ''))[:100]}); try again "
                           "later.")
    return [d["identifier"] for d in data["response"].get("docs", []) if d.get("identifier")]


# ----------------------------------------------------------------- the lists in the output folder

def update_no_description(out):
    """Write NO DESCRIPTION YET.txt: every picture of your own videos in out that has no description yet (no .txt
    of the same name and not in captions.csv), saying where a draft is waiting. Removed when there are none.
    Returns how many are listed."""
    online = set()
    path = os.path.join(out, DESCRIBERS_LIST)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    online.add(json.loads(line)["file"])
                except (ValueError, KeyError, TypeError):
                    pass
    listed = set()
    path = os.path.join(out, CAPTIONS)
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            listed = {row.get("file", "") for row in csv.DictReader(f)}
    waiting = []
    for name in sorted(os.listdir(out)):
        stem, ending = os.path.splitext(name)
        if ending.lower() != ".jpg" or name in online or name in listed:
            continue
        if os.path.exists(os.path.join(out, stem + ".txt")):
            continue
        draft = os.path.exists(os.path.join(out, stem + ".draft.txt"))
        waiting.append(name + (f"  (a draft is in {stem}.draft.txt: check it, correct it, then rename it to "
                               f"{stem}.txt)" if draft else ""))
    target = os.path.join(out, NO_DESCRIPTION)
    if not waiting:
        if os.path.exists(target):
            os.remove(target)
        return 0
    write_text(target, "\n".join([
        "Pictures without a description yet",
        "",
        "Nothing was said near these pictures. They are not used for training until each has a description. To add",
        "one: make a text file with the same name as the picture, ending .txt instead of .jpg, in this folder, and",
        "write in it what the picture shows (for example: These are Granny Smith apples, a dollar twenty-nine a",
        "pound.). Or delete the picture if you do not need it. A draft (.draft.txt) was written by the computer: it",
        "may be wrong, so have it checked before you rename it to .txt.",
        "",
        *waiting]))
    return len(waiting)


def set_question(out, question):
    """Write question.txt in out (when it is not there yet): own_data.py asks this question for every picture in the
    folder that has a text file of the same name, instead of its usual "Describe this picture."."""
    path = os.path.join(out, QUESTION_FILE)
    if not os.path.exists(path):
        write_text(path, question)


def set_place(out, place):
    """Write place.txt in out (--place): where in the world the videos were filmed, such as "Accra, Ghana". own_data.py
    gives every picture in the folder this place, which teaches the model what places look like."""
    place = " ".join(str(place or "").split()).strip(" ,.")
    if place:
        os.makedirs(out, exist_ok=True)
        write_text(os.path.join(out, PLACE_FILE), place)


def add_captions(out, rows):
    """Add rows {"file", "question", "answer"} to captions.csv in out (own_data.py layout b), made when missing."""
    path = os.path.join(out, CAPTIONS)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "question", "answer"])
        if new:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


# ----------------------------------------------------------------- 1. your own videos

def own_video(path, out, every, max_frames, listener, faces, say, overlays=None, overlay_lines=None):
    """Make the pictures of one video of your own (see the module docstring). overlays: an Overlays for this video
    (date stamps and logos), or None; what it found and did is added to overlay_lines and OVERLAYS.txt. Returns
    {"kept", "described", "new": [pictures without a description]}."""
    name = os.path.basename(path)
    stem = safe_stem(os.path.splitext(name)[0])
    set_question(out, OWN_QUESTION)
    said = []
    if listener is not None:
        say("  Turning your speech into text.")
        said = phrases(listener.words(decode_sound(path)))
        append_text(os.path.join(out, TRANSCRIPT), transcript_text(name, said))
        say(f"  {plural(len(said), 'phrase')} heard.")
    say("  Choosing the pictures (sharp, not dark, not the same as the one before).")
    samples, length = scan(path, overlays.watch if overlays is not None else None)
    overlay_report(out, overlays, name, overlay_lines if overlay_lines is not None else [], say)
    kept, counts = choose(samples, every)
    align(kept, said)
    if max_frames and len(kept) > max_frames:
        with_words = [k for k in kept if k["said"]]
        without = [k for k in kept if not k["said"]]
        picked = spread(with_words, max_frames)
        picked += spread(without, max_frames - len(picked))
        kept = sorted(picked, key=lambda k: k["t"])
    pictures = grab(path, [k["pts"] for k in kept])
    described, new = 0, []
    for k in kept:
        img = pictures.get(k["pts"])
        if img is None:
            continue
        base = os.path.join(out, f"{stem}_{time_name(k['t'])}")
        save_picture(img, base + ".jpg", faces, overlays)
        text = tidy(" ".join(p["text"] for p in k["said"]))
        if text and not os.path.exists(base + ".txt"):
            write_text(base + ".txt", text)
            described += 1
        elif not text:
            new.append(base + ".jpg")
    left = []
    if counts["dark"]:
        left.append(f"{counts['dark']} dark")
    if counts["blurry"]:
        left.append(f"{counts['blurry']} blurry")
    if counts["same"]:
        left.append(f"{counts['same']} the same as another")
    say(f"  {plural(len(kept), 'picture')} kept from {clock(length)} of video, {described} with your words"
        + (f"; left out: {', '.join(left)}." if left else "."))
    return {"kept": len(kept), "described": described, "new": new}


# ----------------------------------------------------------------- 2. online videos

def video_length(url, say, tries=3):
    """The length in seconds of an online video (0 when not known). A website that says "too many requests" is
    asked again after a pause."""
    import time
    for attempt in range(tries):
        try:
            with open_media(url) as container:
                return float(container.duration / 1e6) if container.duration else 0.0
        except Exception as e:
            if "429" not in str(e) or attempt + 1 == tries:
                raise
            say("  The website asks to wait a moment; trying again in 20 seconds.")
            time.sleep(20)
    return 0.0


def online_pictures(video, out, every, max_frames, listener, faces, say, overlays=None, overlay_lines=None):
    """Make the stills of one online video (from online_video()): read only around evenly spaced times, write
    CREDITS.txt and stills-for-describers.jsonl, and with listener the narration to <name>.narration.txt.
    overlays, overlay_lines: see own_video() (here only the moments read are compared). Returns {"kept",
    "narrated"}."""
    key = video["id"].replace("File:", "")
    key = os.path.splitext(key)[0] if key.lower().endswith(VIDEO_ENDINGS) else key
    stem = safe_stem(f"{SITE_KEYS[video['site']]}-{key}")
    if done_before(out, stem):
        say("  Done before (its stills are in the folder): skipped.")
        return {"kept": 0, "narrated": 0}
    length = video_length(video["video"], say)
    if length <= 0:
        raise VideoProblem(f"The length of {video['title']} cannot be read, so it cannot be read in parts.")
    most = max_frames or ONLINE_MOST
    gap = max(every, length / most)
    points = [gap / 2 + i * gap for i in range(int(length / gap))][:most] or [length / 2]
    say(f"  Reading {plural(len(points), 'moment')} of {clock(length)} of video, straight from the web.")
    kept, counts, _ = spots(video["video"], points, gap, overlays.watch if overlays is not None else None)
    overlay_report(out, overlays, f"{video['title']} ({video['page']})", overlay_lines if overlay_lines is not None
                   else [], say)
    said = []
    if listener is not None:
        say("  Turning the narration into text (this reads the whole sound track).")
        said = phrases(listener.words(decode_sound(video["video"])))
        append_text(os.path.join(out, TRANSCRIPT), transcript_text(video["title"], said))
        align(kept, said)
    share_alike = video["kind"] == "by-sa"
    credit = video["title"] + (f", by {video['creator']}" if video["creator"] else "") + f" ({video['site']})"
    block = [f"{video['title']}", f"  By: {video['creator'] or 'not given'}",
             f"  Licence: {video['licence']}" + (f" ({video['licence_url']})" if video["licence_url"] else ""),
             f"  Source: {video['page']}"]
    if share_alike:
        block.append("  SHARE-ALIKE: these stills, their descriptions and anything trained on them must be shared "
                     "under the same licence.")
    block.append("  Stills:")
    rows, narrated = [], 0
    for k in kept:
        name = f"{stem}_{time_name(k['t'])}"
        save_picture(k["picture"], os.path.join(out, name + ".jpg"), faces, overlays)
        block.append(f"    {name}.jpg at {clock(k['t'])}")
        if k.get("said"):
            write_text(os.path.join(out, name + ".narration.txt"), tidy(" ".join(p["text"] for p in k["said"])))
            narrated += 1
        rows.append({"file": name + ".jpg", "licence": video["licence"],
                     "credit": f"{credit}, still at {clock(k['t'])}", "collection": f"video-{video['site']}",
                     "source": video["page"], "share_alike": share_alike})
    if rows:
        append_text(os.path.join(out, CREDITS), "\n".join(block))
    with open(os.path.join(out, DESCRIBERS_LIST), "a", encoding="utf-8") as f:
        f.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    left = ", ".join(f"{n} {why}" for why, n in counts.items() if n)
    say(f"  {plural(len(kept), 'still')} kept" + (f"; left out: {left}." if left else "."))
    return {"kept": len(kept), "narrated": narrated}


# ----------------------------------------------------------------- what the wizard calls

def make_pictures(video_paths, out_folder, every=2.0, max_frames=0, speech=True, language="en", blur_faces=False,
                  drafts=False, say=print, share_alike=False, online_speech=False, search="", collection="",
                  max_videos=5, speech_model=WHISPER_DEFAULT, overlays="keep", overlay_boxes=()):
    """Turn videos into training pictures in out_folder and return a summary in plain words.

    video_paths: one or more video files, folders of videos, or online addresses (archive.org, Wikimedia Commons,
    NASA Images). every: at most one picture per this many seconds. max_frames: at most this many pictures from
    each video (0: no limit for your own videos; ONLINE_MOST for online ones). speech: describe your own videos'
    pictures with what you said. blur_faces: blur faces. drafts: draft descriptions for the rest. share_alike:
    accept CC BY-SA online videos. online_speech: write online videos' narration to .narration.txt. search,
    collection, max_videos: also find up to max_videos archive.org videos for these words. overlays: what to do
    about burned-in date stamps, station logos and fixed tickers: "keep" them (as they are), "crop" them off (filled
    in when cropping would lose too much) or "fill" them in; overlay_boxes: boxes given by hand, (x0, y0, x1, y1) as
    shares of the picture (see overlay_box()), removed as well. What was found goes into OVERLAYS.txt."""
    check_overlays(overlays, overlay_boxes)
    if isinstance(video_paths, str):
        video_paths = [video_paths]
    os.makedirs(out_folder, exist_ok=True)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    local = video_files([p for p in video_paths if online_kind(p) is None])
    online = [p for p in video_paths if online_kind(p) is not None]
    refused = []
    if search:
        say(f"Searching archive.org for videos about {search}.")
        try:
            found = search_archive(search, collection, max_videos, share_alike)
        except VideoProblem as e:
            found = []
            refused.append(str(e))
        except Exception as e:  # noqa: BLE001 - a search that fails is said
            found = []
            refused.append(f"The archive.org search did not work ({str(e).splitlines()[0][:150]}).")
        say(f"  {plural(len(found), 'video')} found to check.")
        online += [f"archive:{i}" for i in found]
    faces = FaceBlur(say) if blur_faces else None
    listener = Listener(speech_model, language, say) if (speech and local) or (online_speech and online) else None
    totals = {"own": len(local), "videos": 0, "kept": 0, "described": 0, "online": 0, "narrated": 0, "skipped": 0}
    new, overlay_lines = [], []
    for number, path in enumerate(local, 1):
        name = os.path.basename(path)
        say(f"Video {number} of {len(local)}: {name}")
        if done_before(out_folder, safe_stem(os.path.splitext(name)[0])):
            say("  Done before (its pictures are in the folder; delete them to make them again): skipped.")
            totals["skipped"] += 1
            continue
        try:
            result = own_video(path, out_folder, every, max_frames, listener if speech else None, faces, say,
                               Overlays(overlays, overlay_boxes), overlay_lines)
        except VideoProblem as e:
            refused.append(str(e))
            say("  " + str(e))
            continue
        except Exception as e:  # noqa: BLE001 - one broken video does not stop the others
            refused.append(f"{name} could not be read ({str(e).splitlines()[0][:150]}).")
            say("  " + refused[-1])
            continue
        totals["videos"] += 1
        totals["kept"] += result["kept"]
        totals["described"] += result["described"]
        new += result["new"]
    accepted = 0
    for number, source in enumerate(online, 1):
        if search and source.startswith("archive:") and accepted >= max_videos:
            break
        say(f"Online video {number} of {len(online)}: {source}")
        try:
            video = online_video(source, share_alike)
            say(f"  {video['title']}; licence: {video['licence']}.")
            result = online_pictures(video, out_folder, every, max_frames, listener if online_speech else None,
                                     faces, say, Overlays(overlays, overlay_boxes), overlay_lines)
        except VideoProblem as e:
            refused.append(str(e))
            say("  " + str(e))
            continue
        except Exception as e:  # noqa: BLE001 - one video that cannot be read does not stop the others
            refused.append(f"{source} could not be read ({str(e).splitlines()[0][:150]}).")
            say("  " + refused[-1])
            continue
        accepted += 1
        totals["videos"] += 1
        totals["online"] += result["kept"]
        totals["narrated"] += result["narrated"]
    if listener is not None:
        listener.close()
    drafted = write_drafts(new, say) if drafts and new else 0
    waiting = update_no_description(out_folder)
    return summary(out_folder, totals, len(new), drafted, waiting, faces, refused, overlay_lines)


def summary(out, totals, without, drafted, waiting, faces, refused, overlay_lines=()):
    """The plain-words summary of make_pictures (overlay_lines: what was found and done about date stamps and
    logos, one line per video)."""
    lines = [f"Finished: {plural(totals['videos'], 'video')} made into pictures in {out}."]
    if totals["own"]:
        lines.append(f"Your own videos: {plural(totals['kept'], 'picture')} kept, {totals['described']} with a "
                     f"description from your speech, {without} without one.")
    if waiting:
        lines.append(f"{plural(waiting, 'picture')} still need a description: they are listed in {NO_DESCRIPTION}.")
    if drafted:
        lines.append(f"{plural(drafted, 'draft description')} written (.draft.txt): have them checked by a person "
                     "before renaming them to .txt.")
    if totals["online"]:
        lines.append(f"Online videos: {plural(totals['online'], 'still')} kept, credited in {CREDITS} and listed in "
                     f"{DESCRIBERS_LIST} for the describers' website."
                     + (f" {totals['narrated']} have the narration in a .narration.txt file." if totals["narrated"]
                        else ""))
    if faces is not None:
        lines.append(f"Faces blurred: {faces.faces} in {plural(faces.pictures, 'picture')}.")
    if overlay_lines:
        lines.append(f"Date stamps and logos (also written in {OVERLAYS_FILE}):")
        lines += ["  " + line for line in overlay_lines]
    if totals["skipped"]:
        lines.append(f"{plural(totals['skipped'], 'video')} done before {'was' if totals['skipped'] == 1 else 'were'} "
                     "skipped.")
    if refused:
        lines.append("Not used: " + " ".join(refused))
    return "\n".join(lines)


# ----------------------------------------------------------------- 3. audio-described videos

def choose_ad_track(tracks, ad_track=0):
    """(description track number, plain soundtrack number or None) of a video's sound tracks: the one given, or the
    one marked as audio description; VideoProblem when there is none."""
    if ad_track:
        if not any(t["number"] == ad_track for t in tracks):
            raise VideoProblem(f"This video has no sound track {ad_track}; it has {len(tracks)}.")
        chosen = ad_track
    else:
        marked = [t for t in tracks if t["described"]]
        if not marked:
            raise VideoProblem("No sound track of this video is marked as audio description. If you know which one "
                               "it is, choose it by its number (--ad-track); or give the description as a separate "
                               "sound file (--ad-audio) or text file (--ad-text).")
        chosen = marked[0]["number"]
    others = [t for t in tracks if t["number"] != chosen and not t["described"]]
    main = next((t["number"] for t in others if t["default"]), others[0]["number"] if others else None)
    return chosen, main


def make_described_pictures(video, out_folder, ad_track=0, ad_audio="", ad_text="", language="en", blur_faces=False,
                            say=print, speech_model=WHISPER_DEFAULT, overlays="keep", overlay_boxes=()):
    """Pictures with descriptions from an audio-described video you have, for PERSONAL training (see the module
    docstring); returns a summary in plain words, which lists the video's sound tracks and the personal-use
    note. overlays, overlay_boxes: date stamps and logos, as in make_pictures()."""
    check_overlays(overlays, overlay_boxes)
    os.makedirs(out_folder, exist_ok=True)
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    name = os.path.basename(video)
    stem = safe_stem(os.path.splitext(name)[0])
    tracks = audio_tracks(video)
    listing = tracks_text(tracks)
    say(f"{name}: its sound tracks:")
    say(listing)
    if done_before(out_folder, stem):
        return (f"{name} was done before (its pictures are in the folder; delete them to make them again).\n"
                f"Its sound tracks:\n{listing}")
    listener = None
    if ad_text:
        say(f"Reading the description text {os.path.basename(ad_text)}.")
        lines = read_description_text(ad_text)
        how = f"the description text {os.path.basename(ad_text)}"
    else:
        listener = Listener(speech_model, language, say)
        if ad_audio:
            say(f"Turning the description sound file {os.path.basename(ad_audio)} into text.")
            described = phrases(listener.words(decode_sound(ad_audio)))
            main = 1 if tracks else None
            how = f"the description sound file {os.path.basename(ad_audio)}"
        else:
            chosen, main = choose_ad_track(tracks, ad_track)
            say(f"Turning sound track {chosen} (the description) into text.")
            described = phrases(listener.words(decode_sound(video, chosen)))
            how = f"sound track {chosen}"
        if main:
            say(f"Turning sound track {main} (the plain soundtrack) into text, to tell the narrator from the "
                "dialogue.")
            main_words = listener.words(decode_sound(video, main))
            lines = separate(described, main_words)
        else:
            lines = described
        listener.close()
        append_text(os.path.join(out_folder, TRANSCRIPT), transcript_text(f"{name}: the narrator", lines))
    lines = narrator_lines(lines)
    say(f"{plural(len(lines), 'description line')} to use. Choosing the sharpest picture for each.")
    remover = Overlays(overlays, overlay_boxes)
    overlay_lines = []
    samples, _ = scan(video, remover.watch)
    overlay_report(out_folder, remover, name, overlay_lines, say)
    limit = blur_limit(samples)
    picks = {}
    for line in lines:
        start, end = line["start"] + AD_FROM, max(line["end"], line["start"] + AD_SHORT)
        inside = [s for s in samples if start <= s["t"] <= end and s["bright"] >= DARK]
        inside = inside or [s for s in samples if s["t"] >= line["start"] and s["bright"] >= DARK][:1]
        if not inside:
            continue
        best = max(inside, key=lambda s: s["sharp"])
        if best["sharp"] < limit and len(inside) > 1:
            continue
        pick = picks.setdefault(best["pts"], {"t": best["t"], "texts": []})
        pick["texts"].append(line["text"])
    faces = FaceBlur(say) if blur_faces else None
    pictures = grab(video, list(picks))
    rows = []
    for pts, pick in sorted(picks.items(), key=lambda item: item[1]["t"]):
        if pts not in pictures:
            continue
        file = f"{stem}_{time_name(pick['t'])}.jpg"
        save_picture(pictures[pts], os.path.join(out_folder, file), faces, remover)
        rows.append(file)
        base = os.path.splitext(os.path.join(out_folder, file))[0]
        if not os.path.exists(base + ".txt"):              # never overwrite a description someone corrected
            write_text(base + ".txt", " ".join(pick["texts"]))
    set_question(out_folder, AD_QUESTION)
    write_text(os.path.join(out_folder, PERSONAL_FILE), PERSONAL_USE)
    update_no_description(out_folder)
    text = [f"Finished: {plural(len(rows), 'picture')} from {name}, described by {how}, in {out_folder}.",
            "Each picture's description is in the text file of the same name (open it in Notepad to check and "
            "correct it).",
            "Its sound tracks:", listing]
    if faces is not None:
        text.append(f"Faces blurred: {faces.faces} in {plural(faces.pictures, 'picture')}.")
    if overlay_lines:
        text.append(f"Date stamps and logos (also written in {OVERLAYS_FILE}): " + " ".join(overlay_lines))
    text.append("PERSONAL USE: " + PERSONAL_USE)
    return "\n".join(text)


# ----------------------------------------------------------------- the command line

def main(argv=None):
    """Read the command line, do the work and say the summary."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sources", nargs="*", help="video files, folders of videos, or online video addresses")
    parser.add_argument("--out", required=True, help="the folder for the pictures")
    parser.add_argument("--every", type=float, default=2.0, help="at most one picture per this many seconds")
    parser.add_argument("--max", type=int, default=0, help="at most this many pictures from each video")
    parser.add_argument("--no-speech", action="store_true", help="do not use your speech as descriptions")
    parser.add_argument("--language", default="en", help="the language spoken (en, fr, de ...)")
    parser.add_argument("--blur-faces", action="store_true", help="blur faces")
    parser.add_argument("--draft-descriptions", action="store_true",
                        help="draft descriptions (.draft.txt) for pictures with nothing said near them")
    parser.add_argument("--speech-model", default=WHISPER_DEFAULT, choices=sorted(WHISPER_MODELS))
    parser.add_argument("--speech", action="store_true", help="online videos: write the narration to .narration.txt")
    parser.add_argument("--share-alike", action="store_true", help="online videos: also accept CC BY-SA")
    parser.add_argument("--from-search", default="", help="online videos: search archive.org for these words")
    parser.add_argument("--collection", default="", help="with --from-search: an archive.org collection")
    parser.add_argument("--max-videos", type=int, default=5, help="with --from-search: how many videos")
    parser.add_argument("--described", action="store_true", help="an audio-described video (personal use)")
    parser.add_argument("--ad-track", type=int, default=0, help="with --described: the description sound track")
    parser.add_argument("--ad-audio", default="", help="with --described: a description sound file")
    parser.add_argument("--ad-text", default="", help="with --described: a WebVTT or SRT description file")
    parser.add_argument("--overlays", default="keep", choices=OVERLAY_CHOICES,
                        help="burned-in date stamps, station logos and fixed tickers: keep them, crop them off (filled "
                             "in when cropping would lose too much), or fill them in")
    parser.add_argument("--place", default="", help="where the videos were filmed, ending with the country (for "
                                                    "example \"Accra, Ghana\"): written to place.txt in --out")
    parser.add_argument("--overlay-box", action="append", default=[], metavar="X,Y,W,H",
                        help="with --overlays crop or fill: also remove this box, in percent of the picture from its "
                             "top left corner (can be given more than once)")
    args = parser.parse_args(argv)
    try:
        boxes = [overlay_box(b) for b in args.overlay_box]
    except ValueError as e:
        parser.error(f"--overlay-box: {e}")

    def say(text=""):
        """Say one line on the screen."""
        print(text, flush=True)

    try:
        set_place(args.out, args.place)
        if args.described:
            if len(args.sources) != 1 or not os.path.isfile(args.sources[0]):
                raise VideoProblem("--described takes one video file that is on this computer.")
            text = make_described_pictures(args.sources[0], args.out, args.ad_track, args.ad_audio, args.ad_text,
                                           args.language, args.blur_faces, say, args.speech_model, args.overlays,
                                           boxes)
        else:
            if not args.sources and not args.from_search:
                raise VideoProblem("Give at least one video, folder or online address (or --from-search).")
            for source in args.sources:
                if online_kind(source) is None and not os.path.exists(source):
                    raise VideoProblem(f"{source} was not found.")
            text = make_pictures(args.sources, args.out, args.every, args.max, not args.no_speech, args.language,
                                 args.blur_faces, args.draft_descriptions, say, args.share_alike, args.speech,
                                 args.from_search, args.collection, args.max_videos, args.speech_model,
                                 args.overlays, boxes)
    except VideoProblem as e:
        say("STOPPED: " + str(e))
        return 1
    say("")
    say(text)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Stopped by you. Start it again: videos already done are skipped.")
        sys.exit(1)
