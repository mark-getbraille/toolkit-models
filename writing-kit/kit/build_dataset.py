"""Build the Writing Kit's training files: instruction and answer pairs that teach Qwen to write emails, replies,
thank-you notes, requests, follow-ups, scheduling messages, announcements, text messages, memos, chat messages,
comments and letters, plus whole transcripts of real speech as colloquial English.

What it does, step by step:
  1. for each chosen source (writing_sources.py), downloads only its official files, pages or interface
     (readers.py, readers_more.py, readers_meetings.py, fetch.py: robots.txt obeyed, AI-training refusals obeyed,
     requests paced, API keys only from the computer's settings);
  2. applies the privacy setting (scrub.py, explained in SCRUBBING.txt): by default the owner's rule, which keeps
     everything and masks only Social Security, card, bank and account numbers and passwords; with --privacy strict
     the careful scrubbing (names and details replaced, sensitive messages dropped);
  3. writes an instruction for each piece by simple rules (instructions.py): emails (with the message being
     answered), chats ("write the next message"), texts, letters, public comments and notices;
  4. saves each email's attachments beside it and turns the text of document attachments into more examples
     (attachments.py), and saves whole speech transcripts as text files;
  5. leaves out repeats, spreads the examples over many mailboxes, lists and channels, and puts about one in twenty
     into the validation file (the same one every time, chosen from the text);
  6. writes, in the output folder (out by default):
       train.jsonl, validation.jsonl   one example per line (fields below);
       samples.txt                     the first examples of each source, to read and check;
       build-report.txt                what was read, kept and not used, and why, per source;
       ATTRIBUTION.txt                 the credits and licences of the sources used;
       sources-not-used.txt            the sources that were checked and cannot be used, with the reason;
       messages/<source>/<message>/    message.txt and its attachments;
       transcripts/<source>/           whole transcripts of real speech;
       audio_text/<source>/            audio files with their matching text (pairs.jsonl, README.txt), for speech
                                       and TTS work (sources_audio.py: LibriSpeech, LibriTTS, LibriVox);
       <style>/train.jsonl and validation.jsonl, STYLES.txt   the same examples split by style (styles.py);
       scanned-pages-left-out.txt      the scanned pages OCR could not read well enough, with the reason.

Scanned email releases (pictures of printed pages) are read with OCR on this computer (ocr.py, readers_scanned.py):
from the Internet Archive copies and GovInfo hearing records listed in writing_sources.py, and from a folder of
PDFs the owner downloaded himself (--scanned-folder).

Each line of train.jsonl and validation.jsonl has:
  id, instruction, response, messages (the same pair as a chat: user then assistant), kind, form, tone, audience,
  length, source, source_name, licence, licence_class, licence_url, credit.

Usage (from the writing-kit folder):
  python kit/build_dataset.py --out out                      (open and share-alike sources, 300 each)
  python kit/build_dataset.py --out out --personal           (also Enron and the W3C lists: personal use only)
  python kit/build_dataset.py --out out --sources dolly,oasst2 --per-source 200
  python kit/build_dataset.py --out out --personal --enron-file enron_mail_20150507.tar.gz   (a copy you have)
  python kit/build_dataset.py --out out --cache cache        (keeps downloads in "cache" for the next build)
  python kit/build_dataset.py --out out --scanned-folder "B:\\Original sources"   (only your own scanned PDFs)
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
import readers_more  # noqa: E402
import readers_meetings  # noqa: E402
import readers_business  # noqa: E402
import readers_litigation  # noqa: E402
import styles  # noqa: E402
import readers_creative  # noqa: E402
import attachments  # noqa: E402
import ocr  # noqa: E402
import readers_scanned  # noqa: E402
import sources_more  # noqa: E402
import sources_audio  # noqa: E402
import sources_newspapers  # noqa: E402
import sources_courts  # noqa: E402
import sources_patents  # noqa: E402

READER_MODULES = (readers, readers_more, readers_meetings, readers_business, readers_litigation, readers_creative,
                  readers_scanned, sources_more, sources_audio, sources_newspapers, sources_courts, sources_patents)
# left out unless named in --sources (the big corpora have their own commands)
OPT_IN = sources_audio.OPT_IN | sources_newspapers.OPT_IN | sources_courts.OPT_IN | sources_patents.OPT_IN
GROUPED = {"enron", "w3c", "usenet", "irc", "debian", "scotus", "hearings", "hansard", "idl", "scanned_federal",
           "scanned_state", "govinfo_exhibits"}   # sources read mailbox by mailbox or list by list
GROUPED |= sources_more.GROUPED

VALIDATION_SHARE = 20          # one example in twenty goes to validation.jsonl


OWNER, STRICT = "owner", "strict"        # the two privacy settings (see READ ME FIRST.txt and SCRUBBING.txt)


def protect(text, privacy, names=None, signature=True):
    """text as it goes into an example: under the owner's rule only the identity-theft identifiers are masked; under
    the strict setting personal details and names are replaced as well."""
    if privacy == OWNER:
        return scrub.mask_identifiers(text)
    names = names or scrub.NameScrubber()
    return names.scrub(scrub.scrub_details(text), signature=signature)


def example_from_email(record, source, privacy=OWNER, min_words=12, max_words=200):
    """(example, reason) for one email record. Owner's rule: the whole message is kept (names, signature, sensitive
    topics), identifiers masked; when it quotes the message it answers, that message goes into the instruction and
    the writer's own words are the answer. Strict setting: the cleaned own words only (scrub.clean_message)."""
    audience, is_reply = record.get("audience", "a colleague"), record.get("is_reply", False)
    if privacy == STRICT:
        cleaned, why = scrub.clean_message(record.get("subject", ""), record.get("body", ""),
                                           scrub.names_from_headers(*record.get("known_names", [])),
                                           scrub.names_from_headers(*record.get("writer_names", [])),
                                           min_words, max_words)
        if not cleaned:
            return None, why
        instruction, details = instructions.make_instruction(cleaned["subject"], cleaned["body"], audience, is_reply)
        return make_row(instruction, cleaned["body"], details, source), ""
    full, why = scrub.full_message(record.get("subject", ""), record.get("body", ""))
    if not full:
        return None, why
    own, quoted = full["own"], full["quoted"]
    subject = re.sub(r"^\s*((re|fw|fwd|aw)\s*:\s*)+", "", full["subject"], flags=re.I)
    instruction, details = instructions.make_instruction(subject, own, audience, is_reply or bool(quoted))
    if quoted:
        words = quoted.split()
        shown = " ".join(words[:600]) + (" [...]" if len(words) > 600 else "")
        shown = quoted if len(words) <= 600 else shown
        instruction += "\n\nThe message you are answering:\n" + shown
    return make_row(instruction, own, details, source), ""


def example_from_writing(record, source, privacy=OWNER, max_words=300):
    """(example, reason) for one writing record (a person's request and a person's answer); the request keeps its
    own words."""
    prompt, answer = record.get("instruction", ""), record.get("response", "")
    if privacy == STRICT:
        for part in (prompt, answer):
            why = scrub.sensitive_reason(part)
            if why:
                return None, "sensitive: " + why
    names = scrub.NameScrubber()
    answer_clean = protect(answer, privacy, names)
    prompt_clean = protect(prompt, privacy, names, signature=False)
    why = scrub.quality_reason(answer_clean, 12, max_words) if privacy == STRICT else \
        ("too short" if len(answer_clean.split()) < 5 else "")
    if why and why not in ("too many removed details",):
        return None, "quality: " + why
    kind = instructions.classify_kind("", prompt_clean)          # what was asked for, first
    if kind == "update":
        kind = instructions.classify_kind("", answer_clean)
    details = {"kind": kind, "form": instructions.guess_form(answer_clean, kind, ""),
               "tone": instructions.guess_tone(answer_clean, kind), "audience": "",
               "length": instructions.length_word(answer_clean)}
    return make_row(prompt_clean, answer_clean, details, source), ""


def examples_from_chat(record, source, privacy=OWNER, per_chat=3, context_size=6):
    """[(example, reason)] for a conversation: up to per_chat "write the next message" pairs, each with up to
    context_size earlier messages. Replies of fewer than three words, and the first message, are not used."""
    turns = [(who, protect(text, privacy, signature=False)) for who, text in record.get("turns", [])
             if text and text.strip()]
    candidates = [i for i in range(1, len(turns)) if (len(turns[i][1].split()) >= 3 and turns[i][0] != turns[i - 1][0]
                  or (record.get("style") == "talk" and i >= 1)) and len(turns[i][1].split()) <= 600]
    if record.get("style") == "irc":     # a reply that names the person it answers is the best pair in a busy channel
        named = [i for i in candidates if re.match(r"^\S+[:,]", turns[i][1])]
        candidates = named or candidates
    if not candidates:
        return [(None, "conversation too short")]
    step = max(1, len(candidates) // per_chat)
    out = []
    for i in candidates[::step][:per_chat]:
        context = turns[max(0, i - context_size):i]
        speaker, reply = turns[i]
        instruction, details = instructions.make_chat_instruction(record.get("setting", "a chat"), context, speaker,
                                                                  reply, record.get("style", ""))
        out.append((make_row(instruction, reply, details, source), ""))
    return out


def examples_from_record(record, source, privacy=OWNER):
    """[(example, reason)] for any record a reader yields (see readers_more.py for the kinds)."""
    kind = record.get("type", "email")
    if kind == "email":
        return [example_from_email(record, source, privacy)]
    if kind == "writing":
        return [example_from_writing(record, source, privacy)]
    if kind == "chat":
        return examples_from_chat(record, source, privacy)
    if kind == "text":
        text = record["response"] if record.get("unchanged") else protect(record["response"], privacy)
        details = {k: record.get(k, "") for k in ("kind", "form", "tone", "audience")}
        details["length"] = instructions.length_word(text)
        details.update(record.get("extra") or {})        # source-specific fields (for example a newspaper's date)
        return [(make_row(record["instruction"], text, details, source), "")]
    text = protect(record.get("text", ""), privacy)
    if privacy == STRICT and scrub.sensitive_reason(text):
        return [(None, "sensitive: " + scrub.sensitive_reason(text))]
    if kind == "sms":
        instruction, details = instructions.make_sms_instruction(text)
    elif kind == "letter":
        instruction, details = instructions.make_letter_instruction(text, record.get("title", ""))
    elif kind == "comment":
        instruction, details = instructions.make_comment_instruction(text, record.get("agency", ""),
                                                                     record.get("title", ""))
    else:
        return [(None, "unknown record")]
    return [(make_row(instruction, text, details, source), "")]


def attachment_examples(record, source, attach_dir, privacy=OWNER):
    """Save an email's attachments beside its text (attach_dir/<source>/<message>/) and return examples made from
    the text of the ones that are written documents (memos, letters, notes): "Write a document like the one
    attached to this message"."""
    files = record.get("attachments") or []
    if not files or not attach_dir:
        return []
    msg_key = hashlib.sha1((record.get("msg_id") or record.get("body", "")).encode("utf-8")).hexdigest()[:16]
    folder = os.path.join(attach_dir, source.key, msg_key)
    header = (record.get("header") or f"Subject: {record.get('subject', '')}\n") + "\n"
    attachments.save_message(folder, protect(header + record.get("body", ""), OWNER),
                             [(name, data) for name, data, _ in files])
    out = []
    wanted = record.get("text_from")             # scanned messages: only the attachment's own OCR text, not the pages
    for name, data, ctype in ([] if record.get("no_attachment_text") else files):
        if wanted is not None and name not in wanted:
            continue
        text = attachments.extract_text(name, data, ctype)
        if len(text.split()) < 20:
            continue
        text = protect(text, privacy)
        words = text.split()
        if len(words) > 3000:
            text = " ".join(words[:3000])
        about = re.sub(r"^\s*((re|fw|fwd)\s*:\s*)+", "", record.get("subject", ""), flags=re.I).strip()
        instruction = (f"Write the document \"{attachments.safe_name(name)}\" that was attached to an email"
                       + (f" about \"{about}\"" if about else "") + ". Write it in full, in the same plain, everyday "
                       "style as the original.")
        details = {"kind": "attachment", "form": "document", "tone": instructions.guess_tone(text, "update"),
                   "audience": record.get("audience", ""), "length": instructions.length_word(text)}
        out.append(make_row(instruction, text, details, source))
    return out


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


OPEN_PUBLIC_DOMAIN = {"licence": "Public domain: a work of the US federal government (17 U.S.C. 105)",
                      "licence_class": writing_sources.OPEN,
                      "licence_url": "https://creativecommons.org/publicdomain/mark/1.0/"}
PERSONAL_SCANNED = {"licence": "Personal use only: the writer keeps the copyright (not a US federal government work)",
                    "licence_class": writing_sources.PERSONAL, "licence_url": ""}


def apply_record_licence(row, record):
    """Scanned releases decide the licence message by message (readers_scanned.py): a record's "licence_open"
    True marks the row public domain, False marks it personal use only. Other records keep the source's licence."""
    if "licence_open" in record:
        row.update(OPEN_PUBLIC_DOMAIN if record["licence_open"] else PERSONAL_SCANNED)
    return row


def build_source(source, fetcher, per_source, say, seen, reader_options, privacy=OWNER, attach_dir=None,
                 wanted_styles=None, classes=None):
    """(rows, counts) for one source: up to per_source examples, no more than a tenth from one mailbox, list or
    channel when the source has several (at least 15). classes: the licence classes allowed in this build (rows of
    other classes, possible in scanned releases, are left out)."""
    module = next(m for m in READER_MODULES if hasattr(m, source.reader))
    reader = getattr(module, source.reader)
    counts = Counter()
    rows = []
    per_group = defaultdict(int)
    group_cap = max(15, per_source // 10)
    if source.key in ("w3c", "usenet", "irc", "debian", "scotus", "hearings", "hansard", "idl"):
        group_cap = max(group_cap, per_source // 6 + 1)
    if source.key in ("scanned_federal", "scanned_state", "govinfo_exhibits"):
        group_cap = max(group_cap, per_source // 3 + 1)
    if source.key in ("w3c", "usenet", "irc", "debian", "scotus", "hearings", "hansard"):
        group_cap = max(group_cap, per_source // 2 + 1)
    try:
        for record in reader(fetcher, say=say, **reader_options):
            counts["read"] += 1
            if record.get("type") == "audio_pair":       # audio with its text: its own folder, not an example
                if attach_dir:
                    sources_audio.save_pair(os.path.join(os.path.dirname(attach_dir), "audio_text"), source.key,
                                            record)
                    counts["audio and text pairs saved"] += 1
                continue
            group = record.get("group", "")
            if per_group[group] >= group_cap and len(per_group) > 0 and source.key in GROUPED:
                counts["skipped: enough from this mailbox, list or channel"] += 1
                continue
            made = examples_from_record(record, source, privacy)
            if record.get("raw") and attach_dir:              # keep the whole transcript as spoken-English text
                folder = os.path.join(os.path.dirname(attach_dir), "transcripts", source.key)
                os.makedirs(folder, exist_ok=True)
                with open(os.path.join(folder, attachments.safe_name(record.get("raw_name"), "transcript.txt")),
                          "w", encoding="utf-8") as f:
                    f.write(protect(record["raw"], OWNER))
                counts["transcripts saved"] += 1
            if record.get("type", "email") == "email":
                for row in attachment_examples(record, source, attach_dir, privacy):
                    made.append((row, ""))
                    counts["attachment texts"] += 1
                counts["attachments saved"] += len(record.get("attachments") or [])
            for row, why in made:
                if not row:
                    counts[why] += 1
                    continue
                apply_record_licence(row, record)
                if classes and row["licence_class"] not in classes:
                    counts["personal use only (writer outside the government); add --personal"] += 1
                    continue
                row["style"], row["register"] = styles.label(row, source.key, record)
                if wanted_styles and row["style"] not in wanted_styles:
                    counts["not one of the chosen styles"] += 1
                    continue
                key = normalise(row["response"]) + "|" + normalise(row["instruction"][:200])
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
    except ocr.OcrUnavailable as err:
        counts["skipped: " + str(err)] += 1
        say(f"{source.name}: skipped, because {err}.")
    except fetch.RobotsRefusal as err:
        counts["refused by robots.txt: " + str(err)] += 1
        say(f"{source.name}: not used, because {err}.")
    except (OSError, ValueError) as err:
        counts["stopped by an error: " + str(err)[:120]] += 1
        say(f"{source.name}: stopped early because of an error: {err}")
    counts["groups"] = len(per_group)
    return rows[:per_source], counts


SCANNED_READERS = ("read_ia_federal", "read_ia_state", "read_govinfo_exhibits", "read_scanned_folder")
CHANGES = {OWNER: "Social Security, card, bank and account numbers and passwords masked; nothing else changed",
           STRICT: "personal details and names replaced with placeholders, sensitive messages left out, messages "
                   "shortened to the writer's own words"}


def write_outputs(out, rows, counts_by_source, used, fetcher, started, privacy=OWNER, page_log=None):
    """Write every output file into out (see the module notes)."""
    os.makedirs(out, exist_ok=True)
    if page_log:
        with open(os.path.join(out, "scanned-pages-left-out.txt"), "w", encoding="utf-8") as f:
            f.write(f"Scanned pages left out by the OCR reader ({ocr.ENGINE_NAME}), with the reason. A page is kept "
                    f"when its confidence score is at least {ocr.MIN_PAGE_CONFIDENCE:.2f} and it has at least "
                    f"{ocr.MIN_PAGE_WORDS} words.\n\n")
            for name, page, why in page_log:
                f.write(f"{name}, page {page}: {why}\n" if page else f"{name}: {why}\n")
    train = [r for r in rows if not is_validation(r)]
    valid = [r for r in rows if is_validation(r)]
    if rows and not valid:
        valid, train = train[-1:], train[:-1]
    for name, part in (("train.jsonl", train), ("validation.jsonl", valid)):
        with open(os.path.join(out, name), "w", encoding="utf-8") as f:
            for r in part:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # one folder per style, so a single style can be trained on its own
    by_style = Counter(r["style"] for r in rows)
    for style in by_style:
        folder = os.path.join(out, style)
        os.makedirs(folder, exist_ok=True)
        for name, part in (("train.jsonl", train), ("validation.jsonl", valid)):
            with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                for r in part:
                    if r["style"] == style:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "STYLES.txt"), "w", encoding="utf-8") as f:
        f.write("The styles in this build, with how many examples each (folder name: what it is).\n\n")
        for style, description in styles.STYLES.items():
            if by_style[style]:
                f.write(f"{style}: {by_style[style]} examples. {description}.\n")

    with open(os.path.join(out, "samples.txt"), "w", encoding="utf-8") as f:
        f.write(f"Samples to read and check: the first ten examples of each source (privacy setting: {privacy}).\n"
                "Each one starts with a line 'Example', then the instruction, then the answer.\n\n")
        for source in used:
            mine = [r for r in rows if r["source"] == source.key][:10]
            f.write(f"===== {source.name} ({source.licence_class}): {len(mine)} shown =====\n\n")
            for n, r in enumerate(mine, 1):
                f.write(f"Example {n}. Style: {r['style']}. Register: {r['register']}. Kind: {r['kind']}.\n"
                        f"Instruction: {r['instruction']}\n"
                        f"Answer:\n{r['response']}\n\n")

    with open(os.path.join(out, "build-report.txt"), "w", encoding="utf-8") as f:
        f.write(f"Writing Kit build report, {time.strftime('%Y-%m-%d %H:%M')}. Privacy setting: {privacy} "
                f"({'whole messages; only SSN, card, bank and account numbers and passwords masked' if privacy == OWNER else 'names and personal details replaced, sensitive messages dropped'}).\n\n")
        f.write(f"Examples in all: {len(rows)} ({len(train)} for training, {len(valid)} for validation).\n\n")
        kinds = Counter(r["kind"] for r in rows)
        f.write("Styles: " + ", ".join(f"{k} {v}" for k, v in Counter(r["style"] for r in rows).most_common())
                + ".\n")
        f.write("Registers: " + ", ".join(f"{k} {v}" for k, v in Counter(r["register"] for r in rows).most_common())
                + ".\n")
        f.write("Kinds of message: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()) + ".\n\n")
        for source in used:
            c = counts_by_source.get(source.key, Counter())
            f.write(f"{source.name} ({source.licence_class}, {source.licence.split('. ')[0]}):\n")
            f.write(f"  read {c['read']} records, kept {c['kept']} examples, from {c['groups']} groups (mailboxes, "
                    f"lists, channels or files).\n")
            for label in ("attachments saved", "attachment texts", "transcripts saved", "audio and text pairs saved"):
                if c[label]:
                    f.write(f"  {label}: {c[label]}\n")
            for why, n in sorted(c.items(), key=lambda kv: -kv[1]):
                if why not in ("read", "kept", "groups", "attachments saved", "attachment texts", "transcripts saved",
                               "audio and text pairs saved"):
                    f.write(f"  not used, {why}: {n}\n")
            for w in source.warnings:
                f.write(f"  Warning: {w}\n")
            f.write("\n")
        if page_log is not None and any(s.reader in ("read_ia_federal", "read_ia_state", "read_govinfo_exhibits",
                                                         "read_scanned_folder") for s in used):
            f.write(f"Scanned pages were read with {ocr.ENGINE_NAME}. Pages left out for a low confidence score "
                    f"or almost no text: {len(page_log)} (listed in scanned-pages-left-out.txt).\n\n")
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
                    f"  Changes: {CHANGES[privacy] if source.key != 'sbcsae' else 'none (whole and unchanged)'}; "
                    + ("read from scanned pages with OCR; " if source.reader in SCANNED_READERS else "")
                    + "instructions written by rules.\n")
            if source.reader in SCANNED_READERS:
                kinds = Counter(r["licence_class"] for r in rows if r["source"] == source.key)
                f.write("  Licence by message: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()) + ".\n")
            f.write("\n")

    with open(os.path.join(out, "sources-not-used.txt"), "w", encoding="utf-8") as f:
        f.write("Sources that were checked and cannot be used, with the reason (checked November 2026).\n\n")
        for name, why in writing_sources.NOT_USED:
            f.write(f"{name}\n  {why}\n\n")
    return train, valid


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build the Writing Kit's training files.")
    parser.add_argument("--out", default="out", help="folder for the files (made if missing)")
    parser.add_argument("--styles", default="", help="build only these styles, separated by commas (see STYLES.txt "
                                                     "or READ ME FIRST.txt for the names)")
    parser.add_argument("--sources", default="", help="keys separated by commas (default: every allowed source)")
    parser.add_argument("--per-source", type=int, default=300, help="at most this many examples from each source")
    parser.add_argument("--personal", action="store_true", help="also use the personal-use-only sources")
    parser.add_argument("--enron-file", default="", help="a copy of enron_mail_20150507.tar.gz already on this "
                                                         "computer (then nothing is downloaded for Enron)")
    parser.add_argument("--oanc-file", default="", help="OANC-1.0.1-UTF8.zip downloaded in a browser from anc.org "
                                                        "(GitHub's robots.txt keeps programs from downloading it)")
    parser.add_argument("--local-file", action="append", default=[], metavar="KEY=PATH",
                        help="a file you downloaded in a browser for a source that programs may not download, for "
                             "example --local-file persuade=persuade.zip (persuade, bawe, yelp); may be repeated")
    parser.add_argument("--w3c-lists", default="", help="W3C list names separated by commas")
    parser.add_argument("--w3c-periods", type=int, default=3, help="how many archive periods (three months each) "
                                                                    "to read from each W3C list")
    parser.add_argument("--w3c-pages", type=int, default=30, help="at most this many messages per W3C period")
    parser.add_argument("--cache", default="", help="a folder to keep downloaded pages and files in, so a rebuild "
                                                    "does not download them again")
    parser.add_argument("--scanned-folder", default="", help="a folder of scanned PDF email releases you downloaded "
                                                             "yourself; they are read with OCR (personal use "
                                                             "unless a US federal government work). Alone, only "
                                                             "this folder is read; add --sources to read others too")
    parser.add_argument("--scanned-max-mb", type=int, default=80, help="the largest scanned PDF (in megabytes) "
                                                                       "the kit downloads from the Internet Archive "
                                                                       "or GovInfo")
    parser.add_argument("--scanned-max-pages", type=int, default=0, help="read at most this many pages of each "
                                                                         "PDF in the scanned folder (0: all)")
    parser.add_argument("--audio-pairs", type=int, default=200, help="at most this many audio and text pairs from "
                                                                      "each audio source (saved in audio_text)")
    parser.add_argument("--newspaper-folder", default="newspapers", help="where build_newspapers.py keeps the "
                                                                         "American Stories year files (a sample is "
                                                                         "read from them)")
    parser.add_argument("--newspaper-years", default="", help="years for the newspaper sample, for example "
                                                              "1850-1869,1900,1920s (default: every year)")
    parser.add_argument("--court-folder", default="court_opinions", help="where build_court_opinions.py keeps the "
                                                                         "CourtListener files (a sample is read)")
    parser.add_argument("--patent-folder", default="patents", help="where build_patents.py keeps the patent files "
                                                                   "(a sample is read)")
    parser.add_argument("--privacy", choices=[OWNER, STRICT], default=OWNER,
                        help="owner (the default): keep every message whole and mask only Social Security, card, "
                             "bank and account numbers and passwords; strict: also replace names and personal "
                             "details and drop sensitive messages")
    args = parser.parse_args(argv)
    wanted_styles = {x.strip() for x in args.styles.split(",") if x.strip()}
    bad = wanted_styles - set(styles.STYLES)
    if bad:
        parser.error("unknown style: " + ", ".join(sorted(bad)) + ". Known: " + ", ".join(styles.STYLES))

    started = time.time()
    say = lambda text: print(text, flush=True)
    classes = [writing_sources.OPEN, writing_sources.SHARE_ALIKE] + ([writing_sources.PERSONAL] if args.personal
                                                                     else [])
    known = writing_sources.by_key()
    keys = [k.strip() for k in args.sources.split(",") if k.strip()] or \
        ([] if args.scanned_folder else [s.key for s in writing_sources.SOURCES if s.key not in OPT_IN])
    unknown = [k for k in keys if k not in known]
    if unknown:
        parser.error("unknown source: " + ", ".join(unknown) + ". Known: " + ", ".join(known))
    used = []
    for k in keys:
        if known[k].licence_class in classes:
            used.append(known[k])
        else:
            say(f"{known[k].name} is {known[k].licence_class}; add --personal to use it.")
    if args.scanned_folder:
        if not os.path.isdir(args.scanned_folder):
            parser.error(f"the scanned folder was not found: {args.scanned_folder}")
        used.append(writing_sources.SCANNED_FOLDER)

    fetcher = fetch.Fetcher(say, cache_dir=args.cache or None)
    seen, rows, counts, page_log = set(), [], {}, []
    for source in used:
        say(f"Reading {source.name} ({source.licence_class}).")
        options = {"page_log": page_log, "scanned_max_mb": args.scanned_max_mb, "audio_pairs": args.audio_pairs,
                   "newspaper_folder": args.newspaper_folder, "newspaper_years": args.newspaper_years,
                   "court_folder": args.court_folder, "patent_folder": args.patent_folder}
        if source.key == "scanned_folder":
            options["folder"], options["max_pages"] = args.scanned_folder, args.scanned_max_pages
        if source.key == "enron" and args.enron_file:
            options["local_file"] = args.enron_file
        if source.key == "oanc" and args.oanc_file:
            options["local_file"] = args.oanc_file
        local = dict(x.split("=", 1) for x in args.local_file if "=" in x)
        if source.key in local:
            options["local_file"] = local[source.key]
        if source.key == "w3c":
            options["periods_per_list"], options["pages_per_period"] = args.w3c_periods, args.w3c_pages
            if args.w3c_lists:
                options["lists"] = [x.strip() for x in args.w3c_lists.split(",") if x.strip()]
        got, counts[source.key] = build_source(source, fetcher, args.per_source, say, seen, options, args.privacy,
                                               os.path.join(args.out, "messages"), wanted_styles,
                                               # the owner's own downloads may always be personal use
                                               classes + [writing_sources.PERSONAL] if source.key == "scanned_folder"
                                               else classes)
        say(f"{source.name}: {len(got)} examples kept.")
        rows += got
    train, valid = write_outputs(args.out, rows, counts, used, fetcher, started, args.privacy, page_log)
    say(f"Done: {len(train)} training and {len(valid)} validation examples in {os.path.abspath(args.out)}. "
        "Read samples.txt and build-report.txt there.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
