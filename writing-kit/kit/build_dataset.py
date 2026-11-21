"""Build the Writing Kit's training files: instruction and answer pairs that teach Qwen to write emails, replies,
thank-you notes, requests, follow-ups, scheduling messages, short announcements, text messages and memos.

What it does, step by step:
  1. for each chosen source (writing_sources.py), downloads only its official file or pages (readers.py, fetch.py:
     robots.txt obeyed, AI-training refusals obeyed, requests paced);
  2. passes every message through the privacy scrubbing (scrub.py, explained in SCRUBBING.txt): the writer's own
     words only, sensitive messages dropped, personal details and names replaced with placeholders, only short
     workaday messages kept;
  3. writes an instruction for each real email by simple rules (instructions.py); OASST2 and Dolly keep the
     request their writer wrote, scrubbed the same way;
  4. leaves out repeats, spreads the examples over many mailboxes or lists, and puts about one in twenty into the
     validation file (the same one every time, chosen from the text);
  5. writes, in the output folder:
       train.jsonl, validation.jsonl   one example per line (fields below);
       samples.txt                     the first examples of each source, to read and check;
       build-report.txt                what was kept and dropped, and why, per source;
       ATTRIBUTION.txt                 the credits and licences of the sources used;
       sources-not-used.txt            the sources that were checked and cannot be used, with the reason.

Each line of train.jsonl and validation.jsonl has:
  id, instruction, response, messages (the same pair as a chat: user then assistant), kind, form, tone, audience,
  length, source, source_name, licence, licence_class, licence_url, credit.

Usage (from the writing-kit folder):
  python kit/build_dataset.py --out output                      (open and share-alike sources, 300 each)
  python kit/build_dataset.py --out output --personal           (also Enron and the W3C lists: personal use only)
  python kit/build_dataset.py --out output --sources dolly,oasst2 --per-source 200
  python kit/build_dataset.py --out output --personal --enron-file enron_mail_20150507.tar.gz   (a copy you have)
  python kit/build_dataset.py --out output --cache cache        (keeps downloads in "cache" for the next build)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch  # noqa: E402
import instructions  # noqa: E402
import readers  # noqa: E402
import scrub  # noqa: E402
import writing_sources  # noqa: E402

VALIDATION_SHARE = 20          # one example in twenty goes to validation.jsonl


def example_from_email(record, source, min_words=12, max_words=200):
    """(example, reason) for one email record: the cleaned message as the response and a rule-made instruction,
    or (None, why it was dropped)."""
    cleaned, why = scrub.clean_message(record.get("subject", ""), record.get("body", ""),
                                       scrub.names_from_headers(*record.get("known_names", [])),
                                       scrub.names_from_headers(*record.get("writer_names", [])),
                                       min_words, max_words)
    if not cleaned:
        return None, why
    instruction, details = instructions.make_instruction(cleaned["subject"], cleaned["body"],
                                                         record.get("audience", "a colleague"),
                                                         record.get("is_reply", False))
    return make_row(instruction, cleaned["body"], details, source), ""


def example_from_writing(record, source, max_words=300):
    """(example, reason) for one writing record (a person's request and a person's answer), scrubbed the same way
    as emails; the request keeps its own words."""
    prompt, answer = record.get("instruction", ""), record.get("response", "")
    for part, label in ((prompt, "request"), (answer, "answer")):
        why = scrub.sensitive_reason(part)
        if why:
            return None, "sensitive: " + why
    names = scrub.NameScrubber()
    answer_clean = names.scrub(scrub.scrub_details(answer))
    prompt_clean = names.scrub(scrub.scrub_details(prompt), signature=False)
    why = scrub.quality_reason(answer_clean, 12, max_words)
    if why and why not in ("too many removed details",):
        return None, "quality: " + why
    if len(re.findall(r"\[[^\]]+\]", answer_clean)) > 12:
        return None, "quality: too many removed details"
    kind = instructions.classify_kind("", prompt_clean)          # what was asked for, first
    if kind == "update":
        kind = instructions.classify_kind("", answer_clean)
    details = {"kind": kind, "form": instructions.guess_form(answer_clean, kind, ""),
               "tone": instructions.guess_tone(answer_clean, kind), "audience": "",
               "length": instructions.length_word(answer_clean)}
    return make_row(prompt_clean, answer_clean, details, source), ""


def make_row(instruction, response, details, source):
    """One output line (a dict)."""
    rid = hashlib.sha1((source.key + "\n" + response).encode("utf-8")).hexdigest()[:16]
    return {
        "id": f"{source.key}-{rid}",
        "instruction": instruction,
        "response": response,
        "messages": [{"role": "user", "content": instruction}, {"role": "assistant", "content": response}],
        **details,
        "source": source.key,
        "source_name": source.name,
        "licence": source.licence,
        "licence_class": source.licence_class,
        "licence_url": source.licence_url,
        "credit": source.credit,
    }


def normalise(text):
    """The text in a form for spotting repeats (small letters, no spaces or punctuation)."""
    return re.sub(r"[^a-z]+", "", text.lower())


def is_validation(row):
    """True for about one example in VALIDATION_SHARE, always the same ones."""
    return int(hashlib.sha1(row["response"].encode("utf-8")).hexdigest(), 16) % VALIDATION_SHARE == 0


def build_source(source, fetcher, per_source, say, seen, reader_options):
    """(rows, counts) for one source: up to per_source examples, no more than a tenth from one mailbox or list
    when the source has groups (at least 15)."""
    reader = getattr(readers, source.reader)
    counts = Counter()
    rows = []
    per_group = defaultdict(int)
    group_cap = max(15, per_source // 10)
    is_email = source.key in ("enron", "w3c")
    if source.key == "w3c":
        group_cap = max(group_cap, per_source // max(1, len(reader_options.get("lists") or readers.W3C_LISTS)) + 1)
    try:
        for record in reader(fetcher, say=say, **reader_options):
            counts["read"] += 1
            group = record.get("group", "")
            if is_email and per_group[group] >= group_cap:
                counts["skipped: enough from this mailbox or list"] += 1
                continue
            if is_email:
                row, why = example_from_email(record, source)
            else:
                row, why = example_from_writing(record, source)
            if not row:
                counts[why] += 1
                continue
            key = normalise(row["response"])
            if key in seen:
                counts["repeat"] += 1
                continue
            seen.add(key)
            rows.append(row)
            per_group[group] += 1
            counts["kept"] += 1
            if counts["read"] % 200 == 0:
                say(f"  {source.key}: {counts['read']} read, {counts['kept']} kept")
            if len(rows) >= per_source:
                break
    except fetch.RobotsRefusal as err:
        counts["refused by robots.txt: " + str(err)] += 1
        say(f"{source.name}: not used, because {err}.")
    counts["groups"] = len(per_group)
    return rows, counts


def write_outputs(out, rows, counts_by_source, used, fetcher, started):
    """Write every output file into out (see the module notes)."""
    os.makedirs(out, exist_ok=True)
    train = [r for r in rows if not is_validation(r)]
    valid = [r for r in rows if is_validation(r)]
    if rows and not valid:
        valid, train = train[-1:], train[:-1]
    for name, part in (("train.jsonl", train), ("validation.jsonl", valid)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(os.path.join(out, "samples.txt"), "w", encoding="utf-8") as f:
        f.write("Samples to read and check: the first ten examples of each source, after scrubbing.\n"
                "Each one starts with a line 'Example', then the instruction, then the answer.\n\n")
        for source in used:
            mine = [r for r in rows if r["source"] == source.key][:10]
            f.write(f"===== {source.name} ({source.licence_class}): {len(mine)} shown =====\n\n")
            for n, r in enumerate(mine, 1):
                f.write(f"Example {n}. Kind: {r['kind']}. Tone: {r['tone']}.\nInstruction: {r['instruction']}\n"
                        f"Answer:\n{r['response']}\n\n")

    with open(os.path.join(out, "build-report.txt"), "w", encoding="utf-8") as f:
        f.write(f"Writing Kit build report, {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"Examples in all: {len(rows)} ({len(train)} for training, {len(valid)} for validation).\n\n")
        kinds = Counter(r["kind"] for r in rows)
        f.write("Kinds of message: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()) + ".\n\n")
        for source in used:
            c = counts_by_source.get(source.key, Counter())
            f.write(f"{source.name} ({source.licence_class}, {source.licence.split('. ')[0]}):\n")
            f.write(f"  read {c['read']}, kept {c['kept']}, from {c['groups']} mailboxes or lists.\n")
            for why, n in sorted(c.items(), key=lambda kv: -kv[1]):
                if why not in ("read", "kept", "groups"):
                    f.write(f"  dropped, {why}: {n}\n")
            for w in source.warnings:
                f.write(f"  Warning: {w}\n")
            f.write("\n")
        if fetcher.warnings:
            f.write("Notes from robots.txt files:\n" + "".join(f"  {w}\n" for w in fetcher.warnings) + "\n")
        f.write(f"Time taken: {int(time.time() - started)} seconds.\n")

    with open(os.path.join(out, "ATTRIBUTION.txt"), "w", encoding="utf-8") as f:
        f.write("Credits and licences of the text in train.jsonl and validation.jsonl.\n\n")
        classes = sorted({r["licence_class"] for r in rows})
        if writing_sources.PERSONAL in classes:
            f.write("This build includes PERSONAL USE ONLY text: use it only to train your own model on your own "
                    "computer, and do not share the files or the trained add-on.\n\n")
        elif writing_sources.SHARE_ALIKE in classes:
            f.write("This build includes SHARE-ALIKE text (CC BY-SA): anything made from it that you share must "
                    "carry the same licence and these credits.\n\n")
        for source in used:
            n = sum(1 for r in rows if r["source"] == source.key)
            f.write(f"{source.name}: {n} examples\n  Credit: {source.credit}\n  Licence: {source.licence} "
                    f"({source.licence_class}) {source.licence_url}\n  Where: {source.home}\n"
                    f"  Changes: messages scrubbed of personal details and names, shortened to the writer's own "
                    f"words; instructions written by rules.\n\n")

    with open(os.path.join(out, "sources-not-used.txt"), "w", encoding="utf-8") as f:
        f.write("Sources that were checked and cannot be used, with the reason (checked November 2026).\n\n")
        for name, why in writing_sources.NOT_USED:
            f.write(f"{name}\n  {why}\n\n")
    return train, valid


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the Writing Kit's training files.")
    parser.add_argument("--out", default="output", help="folder for the files (made if missing)")
    parser.add_argument("--sources", default="", help="keys separated by commas (default: every allowed source)")
    parser.add_argument("--per-source", type=int, default=300, help="at most this many examples from each source")
    parser.add_argument("--personal", action="store_true", help="also use the personal-use-only sources")
    parser.add_argument("--enron-file", default="", help="a copy of enron_mail_20150507.tar.gz already on this "
                                                         "computer (then nothing is downloaded for Enron)")
    parser.add_argument("--w3c-lists", default="", help="W3C list names separated by commas")
    parser.add_argument("--cache", default="", help="a folder to keep downloaded pages and files in, so a rebuild "
                                                    "does not download them again")
    args = parser.parse_args(argv)

    started = time.time()
    say = lambda text: print(text, flush=True)
    classes = [writing_sources.OPEN, writing_sources.SHARE_ALIKE] + ([writing_sources.PERSONAL] if args.personal
                                                                     else [])
    known = writing_sources.by_key()
    keys = [k.strip() for k in args.sources.split(",") if k.strip()] or [s.key for s in writing_sources.SOURCES]
    unknown = [k for k in keys if k not in known]
    if unknown:
        parser.error("unknown source: " + ", ".join(unknown) + ". Known: " + ", ".join(known))
    used = []
    for k in keys:
        if known[k].licence_class in classes:
            used.append(known[k])
        else:
            say(f"{known[k].name} is {known[k].licence_class}; add --personal to use it.")

    fetcher = fetch.Fetcher(say, cache_dir=args.cache or None)
    seen, rows, counts = set(), [], {}
    for source in used:
        say(f"Reading {source.name} ({source.licence_class}).")
        options = {}
        if source.key == "enron" and args.enron_file:
            options["local_file"] = args.enron_file
        if source.key == "w3c" and args.w3c_lists:
            options["lists"] = [x.strip() for x in args.w3c_lists.split(",") if x.strip()]
        got, counts[source.key] = build_source(source, fetcher, args.per_source, say, seen, options)
        say(f"{source.name}: {len(got)} examples kept.")
        rows += got
    train, valid = write_outputs(args.out, rows, counts, used, fetcher, started)
    say(f"Done: {len(train)} training and {len(valid)} validation examples in {os.path.abspath(args.out)}. "
        "Read samples.txt and build-report.txt there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
