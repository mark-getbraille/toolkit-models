"""Picture packs for READING HANDWRITING: handwritten manuscript pages with what people typed out from them, and
Wikimedia Commons pictures of handwritten letters, notes, signs, lists and signatures. Used by build_packs.py in the
same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)]; a
picture with more than one question comes once with its JPEG and then as (None, None, row) rows naming the same
picture. The limit counts pictures.

The owner's request of 2026-11-21 (picture packs for a picture describer used by blind people). An answer gives a
transcription ONLY where the dataset gives one, word for word as people typed it; otherwise it says what kind of
handwriting it is, from the Commons category, and (as a second question) the file's own caption.

The packs:
  bentham_pages        The Bentham Papers (University College London): manuscript pages by the philosopher Jeremy
                       Bentham (1748 to 1832) and his secretaries, from the dataset of the ICDAR 2015 competition on
                       handwritten text recognition (tranScriptorium project; Sanchez, Toselli, Romero and Vidal,
                       2015), CC BY 4.0, Zenodo record 248733 (zenodo.org's robots.txt allows /api/records/*/files;
                       read piece by piece from its 6.8 GB zip). 748 pages typed out by the Transcribe Bentham
                       volunteers and checked by the project. "Read this handwritten page." -> the transcription,
                       with the editors' marks made plain: a gap the transcribers could not read is "[...]" and a
                       word split across lines ("im=" / ":posed") is joined.
  commons_handwriting  Wikimedia Commons (CC0, public domain or CC BY files only): handwriting, handwritten
                       letters, handwritten signs, shopping lists, autographs and signatures. "What is this?" ->
                       "This is a handwritten letter." from the category; for a signature whose file name says whose
                       it is ("Abraham Lincoln signature.svg"), "Whose signature is this?" -> "It is the signature of
                       Abraham Lincoln."; and the file's own caption, when it is a real one.

Already in the kit, not repeated: loc_letters (text_packs.py, Library of Congress By the People, CC0 transcriptions
of handwritten letters and diaries), and the envelopes and window envelopes of commons_mail_parcels
(everyday_extras_packs.py). The handwriting sets that could not be packs (GNHK, IAM, RIMES, CVL, HKR, the
ImageCLEF 2016 Bentham set) are in the kit's handwriting_sources.py, with the reason for each.

    python packs/handwriting_packs.py bentham_pages --limit 4      (prints a few rows: a quick check)
"""

import json
import random
import re
import sys
import zipfile

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say, smaller, clean
from food_packs import with_twins
from described_commons import build_described, file_words

READ_PAGE = "Read this handwritten page."
ASK_WHAT = "What is this?"
ASK_SIGNATURE = "Whose signature is this?"

# ----------------------------------------------------------------- Bentham Papers (ICDAR 2015 HTRtS)

BENTHAM_RECORD = "https://zenodo.org/records/248733"
BENTHAM_ZIP = "https://zenodo.org/api/records/248733/files/ICDAR-HTR-Competition-2015.zip/content"
BENTHAM_INNER = "ICDAR-HTR-Competition-2015/TRAIN/contestHTRtS.zip"
BENTHAM_BASE = "contestHTRtS/BenthamData/"
BENTHAM_ABOUT = ("This is a handwritten manuscript page from the Bentham Papers at University College London: "
                 "papers of the philosopher Jeremy Bentham (1748 to 1832), written by him and his secretaries.")
SOFT_HYPHEN = "­"


def bentham_text(text):
    """A Bentham transcription made plain: a word the transcriber split across two lines ("Hus=" then ":band",
    with soft hyphens) is joined; <gap/> (words the volunteers could not read) becomes "[...]"; other editorial
    tags are taken away and their words kept; spaces are tidied. "" when nothing is left."""
    text = text.replace("\r", "")
    text = re.sub(rf"[=\-]?{SOFT_HYPHEN}?[ \t]*\n[ \t]*{SOFT_HYPHEN}?:", "", text)
    text = text.replace(SOFT_HYPHEN, "")
    text = re.sub(r"(?<=[a-z])=?:(?=[a-z])", "", text)     # "for:mer": a line break the page had inside a word
    text = re.sub(r"<gap\s*/>", "[...]", text, flags=re.I)
    text = re.sub(r"<[^>]{1,40}>", "", text)
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def page_lines(xml_text):
    """The typed-out lines of a PAGE XML file (the 1st batch keeps its text there), in the order of the file."""
    return [clean(m) for m in re.findall(r"<TextLine\b.*?<Unicode>(.*?)</Unicode>", xml_text, re.S) if clean(m)]


def bentham_credit(page_id):
    """The credit line of one page: "071_045_003" is box 71, folio 45, page 3 of the Bentham Papers."""
    box, folio, page = (page_id.split("_") + ["", "", ""])[:3]
    return (f"Bentham Papers, University College London (box {box.lstrip('0')}, folio {folio.lstrip('0')}, "
            f"image {page.lstrip('0')}), transcribed by Transcribe Bentham volunteers; from the ICDAR 2015 HTRtS "
            f"dataset (Sanchez, Toselli, Romero and Vidal, 2015, tranScriptorium), CC BY 4.0, {BENTHAM_RECORD}")


def bentham_rows(page_id, text):
    """The rows of one page, or [] when its transcription is too short or too long to be a good answer."""
    text = bentham_text(text)
    words = len(text.split())
    if not 5 <= words <= 450 or text.count("[...]") > words / 8:
        return []
    credit = bentham_credit(page_id)
    return [{"question": READ_PAGE, "answer": text, "credit": credit},
            {"question": ASK_WHAT, "answer": BENTHAM_ABOUT, "credit": credit}]


def build_bentham_pages(limit):
    """The bentham_pages pack: the 2nd batch's page transcriptions and the 1st batch's PAGE files, pages in a fixed
    random order, read from inside the stored inner zip piece by piece (nothing else of the 6.8 GB is fetched)."""
    from world_life_packs import remote_zip
    outer = remote_zip(BENTHAM_ZIP)
    inner = zipfile.ZipFile(outer.open(BENTHAM_INNER))
    names = set(inner.namelist())
    pages = []
    for name in sorted(names):
        m = re.match(re.escape(BENTHAM_BASE) + r"(1stBatch/PAGE|2ndBatch/Transcriptions)/(\w+)\.(xml|txt)$", name)
        if not m:
            continue
        batch = m.group(1).split("/")[0]
        picture = f"{BENTHAM_BASE}{batch}/Images/Pages/{m.group(2)}.jpg"
        if picture in names:
            pages.append((m.group(2), name, picture))
    random.Random(2015).shuffle(pages)
    say(f"Bentham: {len(pages)} pages with a transcription")
    fetched = []
    for page_id, text_name, picture in pages:
        if len(fetched) >= limit:
            break
        raw = inner.read(text_name).decode("utf-8", "replace")
        text = "\n".join(page_lines(raw)) if text_name.endswith(".xml") else raw
        rows = bentham_rows(page_id, text)
        if not rows:
            continue
        data = smaller(inner.read(picture))
        if data:
            build_packs.note_source(f"bentham-{page_id}.jpg", f"{BENTHAM_ZIP}#{picture}")
            fetched.append((f"bentham-{page_id}.jpg", data, rows))
    return with_twins(fetched)


# ----------------------------------------------------------------- Commons: handwriting and signatures

def kind(words):
    """A rows_for function for a kind of handwriting: "What is this?" -> "This is <words>." for every file."""
    return lambda title, text: [(ASK_WHAT, f"This is {words}.")]


# "Abraham Lincoln signature", "Signature of Marie Curie", "Autograph of John Keats", "Mozart Unterschrift"
SIGNED_BY = (re.compile(r"^(?:the\s+)?(?:signature|autograph)\s+(?:of|by)\s+(.+)$", re.I),
             re.compile(r"^(.+?)[\s,_-]+(?:signature|autograph|unterschrift|firma|signatur)\b.*$", re.I))
NOT_A_NAME = re.compile(r"\b(signatures?|autographs?|unknown|unidentified|sample|example|stamp|seal|letter|"
                        r"document|page|book|copy|svg|png|jpg|\d{3,})\b", re.I)


def signer(title):
    """Whose signature a file is, from its title, or "" when the title does not plainly name one person (two to
    five words, starting with a capital letter, no numbers)."""
    words = file_words(title)
    for pattern in SIGNED_BY:
        m = pattern.match(words)
        if m:
            name = re.sub(r"\s*\((?:[^()]*)\)\s*$", "", m.group(1)).strip(" ,.-")
            name = re.sub(r"\s+(?:\d{4}|v\d+|transparent|black|white|cropped|vector)$", "", name, flags=re.I)
            if 2 <= len(name.split()) <= 5 and name[:1].isupper() and not NOT_A_NAME.search(name) \
                    and not re.search(r"\d", name):
                return name
    return ""


def signature_rows(title, text):
    """The rows of a signature: whose it is when the file name says, and that it is a handwritten signature."""
    name = signer(title)
    rows = [(ASK_WHAT, "This is a handwritten signature.")]
    if name:
        rows.append((ASK_SIGNATURE, f"It is the signature of {name}."))
    return rows


HANDWRITING = [
    ("Handwriting", True, kind("handwriting")),
    ("Handwritten letters", True, kind("a handwritten letter")),
    ("Handwritten signs", True, kind("a handwritten sign")),
    ("Shopping lists", False, kind("a shopping list")),
    ("Autographs", True, signature_rows),
    ("Signatures", True, signature_rows),
]


def caption_row(title, text, category):
    """The file's own caption or description, as "Write a short description ..." (when it has a real one)."""
    if text and len(text.split()) >= 5:
        return {"question": build_packs.ALT_TEXT, "answer": text}
    return None


def build_commons_handwriting(limit):
    """The commons_handwriting pack (see the module docstring); no files whose words name a child."""
    return build_described(HANDWRITING, limit, "hand", adults_only=True, extra_row=caption_row)


# ----------------------------------------------------------------- the packs

HANDWRITING_PACKS = {
    "bentham_pages": (build_bentham_pages, "Bentham Papers pages and transcriptions from the ICDAR 2015 Competition "
                                           "HTRtS dataset (Sanchez, Toselli, Romero and Vidal, 2015; tranScriptorium; "
                                           "Transcribe Bentham, University College London), CC BY 4.0, "
                                           f"{BENTHAM_RECORD}. Each page is credited below."),
    "commons_handwriting": (build_commons_handwriting, "Wikimedia Commons (https://commons.wikimedia.org): files CC0, "
                                                       "public domain or CC BY (credited below); captions CC0."),
}
HANDWRITING_LIMITS = {"bentham_pages": 700, "commons_handwriting": 1500}
HANDWRITING_COMMONS_KEYS = ("commons_handwriting",)


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one handwriting pack builder.")
    parser.add_argument("key", choices=sorted(HANDWRITING_PACKS))
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args(argv)
    entries = HANDWRITING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
