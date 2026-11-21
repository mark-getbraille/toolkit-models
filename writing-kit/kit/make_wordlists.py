"""Make wordlists.json, the two word lists scrub.py uses to spot people's names that are not in names.py:

  common   ordinary words: every word written in small letters at least 3 times in the reference text;
  public   well-known proper names (places, countries, companies, products, months): words written with a capital
           letter in the middle of a sentence at least 20 times in the reference text, minus every first name and
           surname in names.py.

A capitalised word that is in neither list (and is not a known public word) is treated as a person's name and
replaced with a placeholder. That replaces some place and company names too; it is on purpose: the kit would rather
lose a pipeline's name than keep a private person's surname.

The reference text is the English part of OpenAssistant OASST2 (Apache License 2.0, by OpenAssistant / LAION and
its contributors), read from its official file on Hugging Face. Only word counts are kept, never any sentence.
The file is made once and kept in the repository; run this again only to remake it:
    python kit/make_wordlists.py
"""

import collections
import gzip
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fetch  # noqa: E402
import names  # noqa: E402
import readers  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "wordlists.json")


def texts(data):
    """Every English message text in the OASST2 trees file (bytes, gzip)."""
    def walk(node):
        if node.get("lang") == "en":
            yield node.get("text", "")
        for child in node.get("replies", []):
            yield from walk(child)
    for line in gzip.decompress(data).decode("utf-8").splitlines():
        yield from walk(json.loads(line)["prompt"])


def count(all_texts):
    """(common, public) word lists from an iterable of texts."""
    lower, capital = collections.Counter(), collections.Counter()
    for text in all_texts:
        text = re.sub(r"```.*?```", " ", text, flags=re.S)          # leave out program code
        for m in re.finditer(r"\b[a-z][a-z']{1,30}\b", text):
            lower[m.group(0)] += 1
        for m in re.finditer(r"(?<=[a-z,;] )[A-Z][a-z]{2,30}\b", text):
            capital[m.group(0)] += 1
    common = sorted(w for w, n in lower.items() if n >= 3)
    people = names.FIRST_NAMES | names.SURNAMES | names.AMBIGUOUS
    public = sorted(w for w, n in capital.items() if n >= 20 and w.lower() not in people)
    return common, public


def main():
    fetcher = fetch.Fetcher()
    print("Downloading OASST2 (54 MB) to count words...")
    common, public = count(texts(fetcher.get(readers.OASST2_URL)))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"about": "Word counts from the English part of OpenAssistant OASST2 (Apache License 2.0, "
                            "OpenAssistant / LAION and contributors). Made by make_wordlists.py.",
                   "common": common, "public": public}, f, separators=(",", ":"))
    print(f"Wrote {OUT}: {len(common)} common words, {len(public)} public names.")


if __name__ == "__main__":
    main()
