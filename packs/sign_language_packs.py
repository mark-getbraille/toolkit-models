"""A picture pack for SIGN LANGUAGE: the American (and British) manual alphabets, fingerspelled letters and numbers,
signs and sign language interpreters, from Wikimedia Commons. Used by build_packs.py in the same way as its own
PACKS: build_<key>(limit) returns [(file name, JPEG bytes or None, row)]; a picture with more than one question comes
once with its JPEG and then as (None, None, row) rows naming the same picture. The limit counts pictures.

The owner's request of 2026-11-21. These are pictures of people's hands and of people signing, so the pack is NEVER
used for picture-making (the kit's NOT_FOR_PICTURE_MAKING). A letter, number or sign is named ONLY where the file
says which it is (its title ends in the letter, "ASL letter B.svg", or says "sign for <word>"); otherwise the answer
says only what the Commons category says (a fingerspelling chart, American Sign Language, an interpreter at work),
with the file's own caption as a second answer when it has a real one. Files whose words name a child are left out.

The pack:
  commons_sign_language  Wikimedia Commons (CC0, public domain or CC BY files only; the public-domain ASL
                         fingerspelling drawings among them): the categories "ASL letters", "American manual
                         alphabet", "Fingerspelling", "American Sign Language", "British Sign Language" and "Sign
                         language interpreters".

Already in the kit, not repeated: commons_expressions (expression_packs.py: thumbs up, OK, V sign, waving; it leaves
sign alphabets out on purpose), bice_gestures, hagrid (share-alike) and how2sign (personal use). ASL Citizen, WLASL,
MS-ASL and the Kaggle alphabet sets are in the kit's picture_reading_sources.py with the reason each is not built.

    python packs/sign_language_packs.py commons_sign_language --limit 6      (prints a few rows: a quick check)
"""

import json
import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say
from described_commons import build_described, file_words, own_caption_row

ASK_LETTER = "Which letter is this hand showing in fingerspelling?"
ASK_NUMBER = "Which number is this hand showing in sign language?"
ASK_SIGN = "What sign is this?"
ASK_WHAT = "What is this?"
ASK_DOING = "What is the person doing?"

# A title that ends in the letter or number shown: "ASL letter B", "Sign language A", "Asl alphabet gallaudet C",
# "ASL number 5". The words before it must be about sign language or fingerspelling.
SIGN_WORDS = r"(?:asl|american sign language|sign[\s_-]*language|fingerspell\w*|manual alphabet|signlanguage|bsl|" \
             r"british sign language|gallaudet|hand ?sign|handshape)"
LETTER = re.compile(rf"\b{SIGN_WORDS}\b.*?(?:\bletter\s+)?\b([A-Z])$", re.I)
NUMBER = re.compile(rf"\b{SIGN_WORDS}\b.*?(?:\bnumber\s+)?\b(\d{{1,2}})$", re.I)
SIGN_FOR = re.compile(r"\bsign(?:ing)?\s+for\s+(?:the\s+word\s+)?[\"'“]?([A-Za-z][A-Za-z' -]{1,30}?)[\"'”]?"
                      r"(?:\s+in\s+(?:ASL|American Sign Language|BSL|British Sign Language))?\s*$", re.I)


def language_of(category, title):
    """"British Sign Language" for the BSL category or a title naming it, else "American Sign Language"."""
    return "British Sign Language" if re.search(r"\b(bsl|british)\b", f"{category} {title}", re.I) \
        else "American Sign Language"


def alphabet_rows(category):
    """A rows_for function for the alphabet and fingerspelling categories."""
    def rows_for(title, text):
        words = file_words(title)
        language = language_of(category, words)
        letter, number = LETTER.search(words), NUMBER.search(words)
        if letter:
            return [(ASK_LETTER, f"The letter {letter.group(1).upper()}, in the {language} manual alphabet."),
                    (ASK_WHAT, f"This is a hand making a letter of the {language} manual alphabet "
                               f"(fingerspelling).")]
        if number:
            return [(ASK_NUMBER, f"The number {int(number.group(1))}, in {language}.")]
        if re.search(r"\balphabets?\b|\bchart\b", words, re.I):
            return [(ASK_WHAT, f"This is a chart of the {language} manual alphabet: the handshapes for the "
                               f"letters, used to fingerspell words.")]
        return []
    return rows_for


def signing_rows(category):
    """A rows_for function for the sign language categories: the sign where the file names it, else that it
    shows the language, only for files with a real caption (the caption is added as a second answer)."""
    def rows_for(title, text):
        words = file_words(title)
        language = language_of(category, words)
        for source in (words, text or ""):
            m = SIGN_FOR.search(source.rstrip(". "))
            if m:
                return [(ASK_SIGN, f"It is the {language} sign for \"{m.group(1).strip().lower()}\".")]
        letter_rows = alphabet_rows(category)(title, text)
        if letter_rows:
            return letter_rows
        if text and len(text.split()) >= 5:
            return [(ASK_WHAT, f"This shows {language}.")]
        return []
    return rows_for


def interpreter_rows(title, text):
    """An interpreter at work: what the category says."""
    return [(ASK_DOING, "The person is a sign language interpreter, turning what is said into sign language.")]


SIGN_SPECS = [
    ("ASL letters", False, alphabet_rows("ASL letters")),
    ("American manual alphabet", True, alphabet_rows("American manual alphabet")),
    ("Fingerspelling", True, alphabet_rows("Fingerspelling")),
    ("American Sign Language", True, signing_rows("American Sign Language")),
    ("British Sign Language", True, signing_rows("British Sign Language")),
    ("Sign language interpreters", True, interpreter_rows),
]


def caption_row(title, text, category):
    """The file's own caption, when it is a real one in English (described_commons.own_caption_row)."""
    return own_caption_row(title, text, category)


def build_commons_sign_language(limit):
    """The commons_sign_language pack (see the module docstring); no files whose words name a child."""
    return build_described(SIGN_SPECS, limit, "sign", adults_only=True, extra_row=caption_row)


SIGN_LANGUAGE_PACKS = {
    "commons_sign_language": (build_commons_sign_language, "Wikimedia Commons (https://commons.wikimedia.org): files "
                                                           "CC0, public domain or CC BY (credited below); captions "
                                                           "CC0."),
}
SIGN_LANGUAGE_LIMITS = {"commons_sign_language": 500}
SIGN_LANGUAGE_COMMONS_KEYS = ("commons_sign_language",)


def main(argv=None):
    """Run the builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try the sign language pack builder.")
    parser.add_argument("key", choices=sorted(SIGN_LANGUAGE_PACKS))
    parser.add_argument("--limit", type=int, default=6)
    args = parser.parse_args(argv)
    entries = SIGN_LANGUAGE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
