"""Build training-kit/kit/real_questions.jsonl: the test set of blind people's real questions (see the docstring of
training-kit/kit/real_questions.py for what it is and how it is scored). Run by a maintainer, not by the kit.

It reads, from a folder of downloads made beforehand (DOWNLOADS, the first argument):
  VQA_test.json            https://vizwiz.cs.colorado.edu/VizWiz_all_answers/VQA_test.json (VizWiz VQA test part
                           with its published answers, CC BY 4.0)
  vqa/train.json, vqa/val.json  from https://vizwiz.cs.colorado.edu/VizWiz_final/vqa_data/Annotations.zip (for the
                           photos VizWiz released with their private parts masked, VizWiz_train_00023431 to
                           00023958, and for the home health test questions of the train and val parts)
  priv/Annotations/*.json  from https://vizwiz.cs.colorado.edu/dataset_downloads/VizWiz-Priv-v1.0/Annotations.zip
                           (CC BY 4.0): a VizWiz VQA question that VizWiz-Priv asked about a private photo (a
                           particular question of four words or more, not a common one such as "What is this?") is
                           left out unless it is one of VizWiz's masked photos, so an unmasked private photo is never
                           used
  orbit_ann.zip            ORBIT's frame annotations, https://raw.githubusercontent.com/microsoft/ORBIT-Dataset/
                           master/data/orbit_extra_annotations.zip
  orbit_train_dir.tsv      the central directory of ORBIT's train zip (https://ndownloader.figshare.com/files/27189155):
                           name, offset, compressed size, method per line (read with byte ranges, never downloaded)

Run:  python3 tools/build_real_questions.py DOWNLOADS [--show 5]
--show N prints N questions of each topic for the hand check.
"""

import argparse
import json
import os
import random
import re
import sys
import zipfile

KIT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "training-kit", "kit")
sys.path.insert(0, KIT)
import real_questions as rq  # noqa: E402
import topics  # noqa: E402

TOTAL = 600
PER_TOPIC = 50
MASKED = (23431, 23958)          # VizWiz_train_000xxxxx: released with the private parts masked (vizwiz.org)

# ORBIT things (the folder names in ORBIT's zip, "my " dropped) used for "What is this?": (topic, accepted names).
ORBIT_THINGS = {
    "medication": ("medicines", ["medication", "medicine", "pills", "pill", "tablets", "pill bottle"]),
    "inhaler": ("medicines", ["inhaler"]),
    "tablets": ("medicines", ["tablets", "pills", "medication", "medicine"]),
    "eye drops": ("medicines", ["eye drops", "drops"]),
    "aspirin": ("medicines", ["aspirin", "pills", "tablets", "medicine", "painkillers"]),
    "pill dosette": ("medicines", ["pill organiser", "pill organizer", "pill box", "pillbox", "dosette",
                                   "pill dispenser", "pill case"]),
    "buckleys": ("medicines", ["buckley's", "buckleys", "cough syrup", "cough medicine", "medicine"]),
    "hand gel": ("medicines", ["hand gel", "hand sanitiser", "hand sanitizer", "sanitizer", "sanitiser"]),
    "hearing aid": ("medicines", ["hearing aid", "hearing aids"]),
    "baked bean tin": ("food", ["baked beans", "beans", "can", "tin"]),
    "banana": ("food", ["banana"]),
    "mustard": ("food", ["mustard"]),
    "mayonnaise jar": ("food", ["mayonnaise", "mayo"]),
    "rice": ("food", ["rice"]),
    "chicken instant noodles": ("food", ["noodles", "instant noodles", "ramen", "pot noodle"]),
    "pepper shaker": ("food", ["pepper", "pepper shaker", "pepper mill", "pepper grinder", "salt shaker"]),
    "fish food": ("food", ["fish food"]),
    "water bottle": ("drinks", ["water bottle", "bottle"]),
    "green water bottle": ("drinks", ["water bottle", "bottle"]),
    "mountain dew can": ("drinks", ["mountain dew", "can", "soda", "soft drink", "drink can"]),
    "pop bottle": ("drinks", ["bottle", "soda", "pop", "soft drink"]),
    "tea": ("drinks", ["tea", "tea bags", "teabags"]),
    "cranberry cream tea": ("drinks", ["tea"]),
    "vagabond ale bottle": ("alcohol", ["beer", "ale", "beer bottle", "bottle"]),
    "prosecco": ("alcohol", ["prosecco", "wine", "sparkling wine", "champagne", "bottle"]),
    "wine glass": ("alcohol", ["wine glass", "glass"]),
    "corkscrew": ("alcohol", ["corkscrew", "bottle opener", "wine opener"]),
    "pint glass": ("alcohol", ["pint glass", "glass", "beer glass"]),
    "apple tv remote": ("machines", ["remote", "remote control"]),
    "remote": ("machines", ["remote", "remote control"]),
    "tv remote": ("machines", ["remote", "remote control"]),
    "sky q remote": ("machines", ["remote", "remote control"]),
    "washing machine": ("machines", ["washing machine", "washer"]),
    "keyboard": ("machines", ["keyboard"]),
    "toaster": ("machines", ["toaster"]),
    "microwave": ("machines", ["microwave"]),
    "cooker": ("machines", ["cooker", "stove", "oven", "hob"]),
    "fridge": ("machines", ["fridge", "refrigerator"]),
    "mouse": ("machines", ["mouse", "computer mouse"]),
    "mobile phone": ("machines", ["phone", "iphone", "smartphone", "mobile", "cell phone"]),
    "laptop": ("machines", ["laptop", "computer"]),
    "victor reader stream": ("machines", ["victor reader", "book player", "media player", "player",
                                          "daisy player", "audio player"]),
    "dictaphone": ("machines", ["dictaphone", "recorder", "voice recorder"]),
    "battery drill": ("machines", ["drill"]),
    "bus stop sign": ("documents", ["bus stop", "sign"]),
    "ottawa bus stop": ("documents", ["bus stop", "sign"]),
    "post box": ("documents", ["post box", "postbox", "mailbox", "letter box", "pillar box"]),
    "local post box": ("documents", ["post box", "postbox", "mailbox", "letter box", "pillar box"]),
    "journal": ("documents", ["journal", "notebook", "book", "diary"]),
    "av tambourine": ("art", ["tambourine"]),
    "keys": ("everyday", ["keys", "key"]),
    "wallet": ("everyday", ["wallet", "purse"]),
    "purse": ("everyday", ["purse", "wallet", "handbag", "bag"]),
    "sunglasses": ("everyday", ["sunglasses", "glasses"]),
    "long cane": ("everyday", ["cane", "white cane", "long cane", "stick"]),
    "white cane": ("everyday", ["cane", "white cane", "long cane", "stick"]),
    "guide dog harness": ("everyday", ["harness", "dog harness", "guide dog harness"]),
    "mug": ("everyday", ["mug", "cup"]),
    "headphones": ("everyday", ["headphones", "headset"]),
    "slippers": ("everyday", ["slippers", "slipper"]),
    "scissors": ("everyday", ["scissors"]),
    "hairbrush": ("everyday", ["hairbrush", "brush", "hair brush"]),
}
ORBIT_PER_TOPIC = {"everyday": 20}
ORBIT_DEFAULT = 8
ISSUES = ("blur_issue", "underexposed_issue", "overexposed_issue", "framing_issue", "occlusion_issue",
          "viewpoint_issue", "object_not_present_issue")


def vizwiz_rows(downloads):
    """Every usable VizWiz question: the test part, the masked photos and the home health tests of the train and val
    parts; with topic and kind; private ones left out (and counted)."""
    def load(name):
        with open(os.path.join(downloads, name), encoding="utf-8") as f:
            return json.load(f)
    private_questions = set()
    for part in ("train", "val", "test"):
        for entry in load(f"priv/Annotations/{part}.json"):
            if entry.get("private") and entry.get("question"):
                private_questions.add(rq.question_key(entry["question"]))
    candidates = [("test", e) for e in load("VQA_test.json")]
    for part in ("train", "val"):
        for e in load(f"vqa/{part}.json"):
            number = int(e["image"][-12:-4])
            masked = part == "train" and MASKED[0] <= number <= MASKED[1]
            home = rq.classify_topic(e["question"], [a["answer"] for a in e["answers"]]) == rq.HOME_TESTS
            if masked or home:
                candidates.append((part + ("-masked" if masked else ""), e))
    common = {}                          # how often each question is asked: "what is this" is not a private match
    for _part, e in candidates:
        key = rq.question_key(e["question"])
        common[key] = common.get(key, 0) + 1
    rows, left = [], {}
    for part, e in candidates:
        people = [a["answer"] for a in e["answers"]]
        masked = part.endswith("masked")
        reason = rq.private_reason(e["question"], people)
        key = rq.question_key(e["question"])
        if not reason and not masked and key in private_questions and len(key.split()) >= 4 and \
                common.get(key, 0) <= 2:
            reason = "asked about a private photo (VizWiz-Priv)"
        if reason:
            left[reason.split(":")[0]] = left.get(reason.split(":")[0], 0) + 1
            continue
        topic = rq.classify_topic(e["question"], people)
        if topic in ("nudity", "sexual"):
            continue
        rows.append({"id": "vizwiz-" + e["image"][len("VizWiz_"):-4].replace("_", "-"), "source": "vizwiz",
                     "image": e["image"], "question": " ".join(e["question"].split()), "answers": people,
                     "answerable": int(e.get("answerable", 1)), "answer_type": e.get("answer_type", ""),
                     "topic": topic, "kind": rq.classify_kind(e["question"], topic, e.get("answer_type", "")),
                     "masked": masked, "licence": rq.LICENCE})
    return rows, left


def orbit_rows(downloads):
    """One clean frame (without problems) of one video for each collector and thing of ORBIT_THINGS, from ORBIT's
    train part, with where the frame is in the zip."""
    notes = zipfile.ZipFile(os.path.join(downloads, "orbit_ann.zip"))
    places = {}
    with open(os.path.join(downloads, "orbit_train_dir.tsv"), encoding="utf-8") as f:
        for line in f:
            name, offset, size, method = line.rstrip("\n").split("\t")
            if name.endswith(".jpg") and "/clean/" in name:
                places[name.rsplit("/", 1)[1]] = (name, int(offset), int(size), int(method))
    rng = random.Random(53)
    by_thing = {}
    for member in sorted(notes.namelist()):
        if not (member.startswith("train/") and member.endswith(".json") and "--clean--" in member):
            continue
        collector, thing = member[len("train/"):].split("--")[:2]
        thing = re.sub(r"^my ", "", thing.replace("-", " "))
        if thing not in ORBIT_THINGS:
            continue
        frames = json.load(notes.open(member))
        good = sorted(k for k, v in frames.items() if not any(v.get(i) for i in ISSUES) and k in places)
        if good:
            by_thing.setdefault((thing, collector), []).append(good[len(good) // 2])
    rows = []
    for (thing, collector), frames in sorted(by_thing.items()):
        topic, names = ORBIT_THINGS[thing]
        frame = rng.choice(frames)
        path, offset, size, method = places[frame]
        rows.append({"id": "orbit-" + os.path.splitext(frame)[0][-60:], "source": "orbit", "image": frame,
                     "question": "What is this?", "answers": names, "answerable": 1, "answer_type": "other",
                     "topic": topic, "kind": "what", "masked": False, "licence": rq.LICENCE, "zip": "train",
                     "offset": offset, "size": size, "method": method, "thing": thing})
    picked = []
    rng.shuffle(rows)
    for topic in {r["topic"] for r in rows}:
        mine = [r for r in rows if r["topic"] == topic]
        things, out = {}, []
        for r in mine:                              # different things first, then a second of each
            things.setdefault(r["thing"], []).append(r)
        while len(out) < ORBIT_PER_TOPIC.get(topic, ORBIT_DEFAULT) and any(things.values()):
            for t in sorted(things):
                if things[t] and len(out) < ORBIT_PER_TOPIC.get(topic, ORBIT_DEFAULT):
                    out.append(things[t].pop())
        picked += out
    return picked


def main(argv=None):
    """Build the list and print the counts (and the hand-check sample with --show)."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("downloads")
    parser.add_argument("--show", type=int, default=0)
    parser.add_argument("--out", default=rq.SET_FILE)
    args = parser.parse_args(argv)
    vizwiz, left = vizwiz_rows(args.downloads)
    orbit = orbit_rows(args.downloads)
    print(f"VizWiz questions usable: {len(vizwiz)}; left out: {left}")
    print("VizWiz by topic:", {t: sum(1 for r in vizwiz if r["topic"] == t) for t in
                               sorted({r["topic"] for r in vizwiz})})
    print("ORBIT frames:", {t: sum(1 for r in orbit if r["topic"] == t) for t in sorted({r["topic"] for r in orbit})})
    order = [t.id for t in topics.TOPICS] + [rq.HOME_TESTS]
    # Home health tests: every one there is (they are rare); the topics: PER_TOPIC each with ORBIT counted in.
    home = [r for r in vizwiz if r["topic"] == rq.HOME_TESTS]
    chosen = list(home) + list(orbit)
    for topic in [t for t in order if t != rq.HOME_TESTS]:
        have = sum(1 for r in chosen if r["topic"] == topic)
        chosen += rq.pick_mix([r for r in vizwiz if r["topic"] == topic], max(0, PER_TOPIC - have))
    chosen += rq.pick_mix([r for r in vizwiz if r["topic"] == rq.EVERYDAY], max(0, TOTAL - len(chosen)))
    rank = {t: i for i, t in enumerate(order + [rq.EVERYDAY])}
    chosen.sort(key=lambda r: (rank.get(r["topic"], 99), r["id"]))
    with open(args.out, "w", encoding="utf-8") as f:
        for r in chosen:
            r = {k: v for k, v in r.items() if k not in ("thing",) and not (k == "masked" and not v)}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Written {len(chosen)} questions to {args.out}")
    print("By topic:", rq.counts(chosen))
    print("Unanswerable:", sum(1 for r in chosen if not r["answerable"]), "masked photos:",
          sum(1 for r in chosen if r.get("masked")))
    print("Kinds:", {k: sum(1 for r in chosen if r["kind"] == k) for k in sorted({r["kind"] for r in chosen})})
    if args.show:
        for topic in order + [rq.EVERYDAY]:
            mine = [r for r in chosen if r["topic"] == topic]
            print(f"\n== {topic} ({len(mine)})")
            for r in random.Random(5).sample(mine, min(args.show, len(mine))):
                agreed = ", ".join(rq.agreed_answers(r["answers"])[:3]) or r["answers"][:3]
                print(f"  [{r['kind']}] {r['question'][:90]} | {agreed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
