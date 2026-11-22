"""An offline English dictionary and thesaurus for the reference library: Open English WordNet, in the group
"dictionaries" ("Reference, dictionaries and thesauri"), the owner's request of 2026-11-22. Keys: wordnet (the book
here), dict:oewn (the same book).

What this module builds, in plain words: the newest yearly edition of Open English WordNet (OEWN), the continuation
of Princeton University's WordNet that the Global WordNet Association's Open English WordNet team keeps up to date,
IN FULL: every word and phrase (about 160,000) with every meaning, grouped by part of speech, each with its
definition and examples, its synonyms (the other words of the same meaning), and its links: broader and narrower
terms, opposites, parts and wholes, related forms, "similar to", "see also", topics and what it entails or causes.
The book is arranged alphabetically; each page holds a few dozen neighbouring words, each a heading, and every word
is also a title of its own in the book's search, so looking up a word goes straight to its page.

Licence: OEWN is under the Creative Commons Attribution 4.0 licence (CC BY 4.0, "attribution is given to both
Princeton WordNet and the Open English Wordnet team"), and its Princeton WordNet part under the WordNet licence
(permission to use, copy, modify and distribute for any purpose, with Princeton's copyright notice and disclaimer on
every copy): both texts are checked in the repository's own LICENSE.md and WNDB_License.txt at every build, and the
notice is on the book's welcome page.

Where it is read: the edition's tag of the team's git repository (github.com/globalwordnet/english-wordnet; one
shallow clone of its src/yaml folder, the source the release files are made from). GitHub's robots.txt disallows
programs from its release download addresses, so the ready-made release files are not fetched; a git clone is what
the owner's rules allow. The YAML files are read by this module's own small reader (YAML_READER), so no new library is
needed.

The book has its licence and notice, "published" (the edition's date), "version" (the edition and commit), the key
and fingerprint for the weekly update check (sign(): the newest edition tag), and "originals" (the repository and its
licence files).

refs_common.REGISTRY sends the dict: keys here. Run from the repository's folder:
  python3 textbooks/wordnet_dict.py dict:oewn --out build/textbooks --limit 500     (a small test: 500 words)
"""

import argparse
import hashlib
import html
import os
import re
import subprocess
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_common as R  # noqa: E402

GROUP = "dictionaries"
GROUPS = {GROUP: "Reference, dictionaries and thesauri"}
WORDS = ("wordnet", f"group:{GROUP}", "dictionary", "thesaurus")

OEWN_REPO = "https://github.com/globalwordnet/english-wordnet"
OEWN_RAW = "https://raw.githubusercontent.com/globalwordnet/english-wordnet"
OEWN_SITE = "https://en-word.net/"
CC_BY = "CC BY 4.0"
CC_BY_URL = "https://creativecommons.org/licenses/by/4.0/"
LICENCE_TEXT = r"Creative Commons Attribution 4.0\s+International License"
WNDB_TEXT = r"Permission to use, copy, modify and distribute this software and[\s\d]+database"   # (the file numbers its lines)
WORDS_PER_PAGE = 40

POS_NAMES = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective", "r": "adverb"}
POS_ORDER = "nvasr"
# Synset relations: (key in the YAML, the words shown) in the order shown; the inverse ones are worked out here.
SYNSET_LINKS = [("hypernym", "Broader terms"), ("hyponym", "Narrower terms"), ("instance_hypernym", "Instance of"),
                ("instance_hyponym", "Instances"), ("mero_part", "Parts"), ("holo_part", "Part of"),
                ("mero_member", "Members"), ("holo_member", "Member of"), ("mero_substance", "Made of"),
                ("holo_substance", "Substance of"), ("entails", "Entails"), ("causes", "Causes"),
                ("similar", "Similar to"), ("also", "See also"), ("attribute", "Attribute"),
                ("domain_topic", "Topic"), ("has_domain_topic", "Words of this topic"),
                ("domain_region", "Region"), ("has_domain_region", "Words of this region"),
                ("exemplifies", "Usage example of"), ("is_exemplified_by", "Usage examples")]
INVERSE = {"hypernym": "hyponym", "instance_hypernym": "instance_hyponym", "mero_part": "holo_part",
           "mero_member": "holo_member", "mero_substance": "holo_substance", "domain_topic": "has_domain_topic",
           "domain_region": "has_domain_region", "exemplifies": "is_exemplified_by"}
SENSE_LINKS = [("antonym", "Opposite"), ("pertainym", "Pertains to"), ("participle", "Participle of"),
               ("derivation", "Related forms"), ("also", "See also"), ("similar", "Similar to"),
               ("exemplifies", "Usage example of")]


# ====================================================================== YAML_READER

def _scalar(text):
    """A YAML plain or quoted scalar's value ("'a''man'" -> "a'man")."""
    t = text.strip()
    if len(t) >= 2 and t[0] == "'" and t[-1] == "'":
        return t[1:-1].replace("''", "'")
    if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
        inner = t[1:-1]
        return re.sub(r'\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)', lambda m: (
            chr(int(m.group(1)[1:], 16)) if m.group(1)[0] in "ux" and len(m.group(1)) > 1 else
            {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/", " ": " "}.get(m.group(1), m.group(1))), inner)
    return t


def _key_split(text):
    """(key, rest after "key:") of a mapping line, or None. The key may be quoted ("'''hood':")."""
    if text[:1] in ("'", '"'):
        q = text[0]
        i = 1
        while i < len(text):
            if text[i] == q:
                if q == "'" and text[i + 1:i + 2] == "'":
                    i += 2
                    continue
                if q == '"' and text[i - 1] == "\\":
                    i += 1
                    continue
                break
            i += 1
        if text[i + 1:i + 2] == ":" and (len(text) == i + 2 or text[i + 2] == " "):
            return _scalar(text[:i + 1]), text[i + 2:].strip()
        return None
    m = re.match(r"^([^\s'\"#][^:]*?):(?: (.*))?$", text)
    if not m:
        return None
    return m.group(1), (m.group(2) or "").strip()


def _unclosed(text):
    """True when a scalar starts with a quote that is not closed on its line."""
    t = text.strip()
    if not t or t[0] not in "'\"":
        return False
    if t[0] == "'":
        body = t[1:].replace("''", "")
        return "'" not in body
    body = re.sub(r'\\.', "", t[1:])
    return '"' not in body


def yaml_load(text):
    """The value of a YAML document of the kind OEWN writes (block mappings and sequences, plain scalars that go on
    over more-indented lines, single- and double-quoted scalars, no anchors, flow collections or block scalars)."""
    lines = [(len(l) - len(l.lstrip(" ")), l.strip()) for l in text.replace("\r", "").split("\n")
             if l.strip() and not l.lstrip().startswith("#") and l.strip() != "---"]
    pos = [0]

    def value_with_more(first, indent):
        """A scalar starting with first, with its continuation lines (indented more than indent)."""
        parts = [first]
        while pos[0] < len(lines):
            ind, content = lines[pos[0]]
            if _unclosed(" ".join(parts)):
                parts.append(content)
                pos[0] += 1
                continue
            if ind > indent and not first.startswith(("'", '"')):
                parts.append(content)
                pos[0] += 1
                continue
            break
        joined = " ".join(parts)
        return _scalar(joined)

    def block(indent):
        """The mapping or sequence whose lines start at indent."""
        if pos[0] >= len(lines):
            return None
        ind, content = lines[pos[0]]
        if content == "-" or content.startswith("- "):
            out = []
            while pos[0] < len(lines):
                ind, content = lines[pos[0]]
                if ind != indent or not (content == "-" or content.startswith("- ")):
                    break
                rest = content[2:].strip() if content != "-" else ""
                pos[0] += 1
                if not rest:
                    out.append(block(lines[pos[0]][0]) if pos[0] < len(lines) and lines[pos[0]][0] > indent else None)
                elif _key_split(rest) is not None:
                    # "- key: value" starts a mapping whose other keys are indented to the key's column
                    lines[pos[0] - 1] = (indent + 2, rest)
                    pos[0] -= 1
                    out.append(block(indent + 2))
                else:
                    out.append(value_with_more(rest, indent))
            return out
        out = {}
        while pos[0] < len(lines):
            ind, content = lines[pos[0]]
            if ind != indent:
                break
            kv = _key_split(content)
            if kv is None:
                break
            key, rest = kv
            pos[0] += 1
            if rest:
                out[key] = value_with_more(rest, indent)
            elif pos[0] < len(lines) and (lines[pos[0]][0] > indent or (lines[pos[0]][0] == indent and
                                                                       lines[pos[0]][1].startswith("- "))):
                out[key] = block(lines[pos[0]][0])
            else:
                out[key] = None
        return out
    return block(lines[0][0]) if lines else None


# ====================================================================== reading OEWN

class Wordnet:
    """The words and meanings of OEWN: lemmas -> {part of speech: {"senses": [...], "pronunciation": [...]}},
    synsets -> {definition, example, members, relations}, sense ids -> (lemma, synset)."""

    def __init__(self):
        """Empty."""
        self.entries = {}
        self.synsets = {}
        self.sense_ids = {}

    def add_entries(self, data):
        """One entries-*.yaml file's mapping."""
        for lemma, by_pos in (data or {}).items():
            lemma = str(lemma)
            for pos, entry in (by_pos or {}).items():
                self.entries.setdefault(lemma, {})[str(pos)] = entry or {}
                for sense in (entry or {}).get("sense") or []:
                    if isinstance(sense, dict) and sense.get("id"):
                        self.sense_ids[str(sense["id"])] = (lemma, str(sense.get("synset")))

    def add_synsets(self, data):
        """One <pos>.<lexfile>.yaml file's mapping."""
        for sid, syn in (data or {}).items():
            if isinstance(syn, dict):
                self.synsets[str(sid)] = syn

    def finish(self):
        """Work out the inverse relations (narrower terms, part of, words of a topic...)."""
        for sid, syn in list(self.synsets.items()):
            for rel, inv in INVERSE.items():
                for target in syn.get(rel) or []:
                    other = self.synsets.get(str(target))
                    if other is not None:
                        other.setdefault(inv, [])
                        if sid not in other[inv]:
                            other[inv].append(sid)


def read_wordnet(folder, limit=None):
    """A Wordnet from a folder of OEWN YAML files. limit: only the first so many lemmas (a test), with only their
    synsets' text kept."""
    wn = Wordnet()
    names = sorted(os.listdir(folder))
    for name in names:
        if name.startswith("entries-") and name.endswith(".yaml"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                wn.add_entries(yaml_load(f.read()))
    if limit:
        keep = sorted(wn.entries, key=sort_key)[:limit]
        wn.entries = {k: wn.entries[k] for k in keep}
    for name in names:
        if re.match(r"^(noun|verb|adj|adv)\.[A-Za-z]+\.yaml$", name):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                wn.add_synsets(yaml_load(f.read()))
    wn.finish()
    return wn


# ====================================================================== the book

def sort_key(lemma):
    """Alphabetical order, ignoring case and the marks before a word ("'hood" with the h's)."""
    return (re.sub(r"^[^0-9A-Za-z]+", "", lemma).lower() or lemma.lower(), lemma)


def unit_of(lemma):
    """The book's part of a word: its first letter (A to Z), or "Numbers and symbols"."""
    first = sort_key(lemma)[0][:1].upper()
    return first if "A" <= first <= "Z" else "Numbers and symbols"


def anchor(lemma):
    """The id of a word's heading on its page."""
    if not re.search(r"[^A-Za-z0-9 ]", lemma):
        return "w-" + lemma.replace(" ", "-")
    return "w-" + re.sub(r"[^A-Za-z0-9]+", "-", lemma).strip("-")[:60] + "-" + \
        hashlib.sha256(lemma.encode("utf-8")).hexdigest()[:6]


def plan_pages(lemmas):
    """[(unit, page path, [lemmas])]: neighbouring words in pages of WORDS_PER_PAGE, a page never across two
    letters."""
    out, current, unit = [], [], None
    for lemma in sorted(lemmas, key=sort_key):
        u = unit_of(lemma)
        if current and (u != unit or len(current) >= WORDS_PER_PAGE):
            out.append((unit, current))
            current = []
        unit = u
        current.append(lemma)
    if current:
        out.append((unit, current))
    used, pages = set(), []
    for unit, words in out:
        base = "words-" + (re.sub(r"[^a-z0-9]+", "-", sort_key(words[0])[0]).strip("-")[:40] or "symbols")
        path = base
        n = 2
        while path in used:
            path = f"{base}-{n}"
            n += 1
        used.add(path)
        pages.append((unit, path, words))
    return pages


def entry_html(wn, lemma, where):
    """The dictionary entry of one word: its parts of speech, each meaning with definition, examples, synonyms and
    links. where: {lemma: (page path, anchor)}."""
    esc = html.escape

    def link(word):
        target = where.get(word)
        return f'<a href="{target[0]}#{target[1]}">{esc(word)}</a>' if target else esc(word)

    def members(sid, skip=None):
        syn = wn.synsets.get(str(sid)) or {}
        return [str(m) for m in syn.get("members") or [] if str(m) != skip]

    parts = [f'<h2 id="{anchor(lemma)}">{esc(lemma)}</h2>']
    by_pos = wn.entries.get(lemma, {})
    for pos in sorted(by_pos, key=lambda p: POS_ORDER.find(p) if p in POS_ORDER else 9):
        entry = by_pos[pos]
        parts.append(f"<h3>{esc(lemma)}, {POS_NAMES.get(pos, pos)}</h3>")
        sounds = []
        for p in entry.get("pronunciation") or []:
            if isinstance(p, dict) and p.get("value"):
                sounds.append(f"/{p['value']}/" + (f" ({p['variety']})" if p.get("variety") else ""))
        if sounds:
            parts.append(f"<p>Pronunciation: {esc(', '.join(sounds))}</p>")
        forms = [str(f) for f in entry.get("form") or []]
        if forms:
            parts.append(f"<p>Other forms: {esc(', '.join(forms))}</p>")
        items = []
        for sense in entry.get("sense") or []:
            if not isinstance(sense, dict):
                continue
            syn = wn.synsets.get(str(sense.get("synset"))) or {}
            definition = "; ".join(str(d) for d in syn.get("definition") or [])
            bits = [f"<p>{esc(definition) or '(no definition)'}</p>"]
            examples = []
            for ex in syn.get("example") or []:
                if isinstance(ex, dict):
                    examples.append(f"“{ex.get('text', '')}” ({ex.get('source', '')})")
                else:
                    examples.append(f"“{ex}”")
            if examples:
                bits.append("<p>Examples: " + esc("; ".join(examples)) + "</p>")
            same = members(sense.get("synset"), lemma)
            if same:
                bits.append("<p>Synonyms: " + ", ".join(link(m) for m in same) + "</p>")
            for rel, words in SENSE_LINKS:
                targets = [wn.sense_ids[str(t)][0] for t in sense.get(rel) or [] if str(t) in wn.sense_ids]
                if rel == "derivation":            # the morphosemantic links (event, agent, result...) are forms too
                    for other in ("agent", "body_part", "by_means_of", "destination", "event", "instrument",
                                  "location", "material", "property", "result", "state", "undergoer", "uses",
                                  "vehicle"):
                        targets += [wn.sense_ids[str(t)][0] for t in sense.get(other) or [] if str(t) in wn.sense_ids]
                targets = list(dict.fromkeys(t for t in targets if t != lemma))
                if targets:
                    bits.append(f"<p>{words}: " + ", ".join(link(t) for t in targets) + "</p>")
            for rel, words in SYNSET_LINKS:
                groups = []
                for target in syn.get(rel) or []:
                    names = members(target)
                    if names:
                        groups.append(", ".join(link(n) for n in names))
                if groups:
                    bits.append(f"<p>{words}: " + "; ".join(groups) + "</p>")
            items.append("<li>" + "".join(bits) + "</li>")
        if items:
            parts.append("<ol>" + "".join(items) + "</ol>")
    return "\n".join(parts)


def wordnet_book(folder, edition, commit, published, limit=None):
    """The Book of OEWN from a folder of its YAML files."""
    import build_textbooks as B
    wn = read_wordnet(folder, limit)
    pages = plan_pages(wn.entries)
    where = {}
    for _unit, path, words in pages:
        for w in words:
            where[w] = (path, anchor(w))
    book = B.Book(name="open_english_wordnet", title=f"Open English WordNet {edition}: dictionary and thesaurus",
                  subject="English dictionary and thesaurus", level="reference", group=GROUP,
                  publisher="Open English WordNet team (Global WordNet Association), from Princeton WordNet",
                  country="International", licence=CC_BY, licence_url=CC_BY_URL, source=OEWN_SITE,
                  description=f"Open English WordNet {edition}, the open continuation of Princeton WordNet, in full: "
                              f"{len(wn.entries):,} English words and phrases with {len(wn.synsets):,} meanings, "
                              "each with its definition, examples and synonyms, and its broader and narrower terms, "
                              "opposites, parts, related forms and other links. Look a word up with the book's "
                              "search, or browse the pages alphabetically.", notice=NOTICE,
                  authors="John P. McCrae and the Open English WordNet team; Princeton University (WordNet)")
    book.changes = "the YAML source of the edition written out as dictionary entries, alphabetically"
    for n, (unit, path, words) in enumerate(pages, 1):
        title = words[0] if len(words) == 1 else f"{words[0]} to {words[-1]}"
        body = "\n".join(entry_html(wn, w, where) for w in words)
        book.pages.append(B.Page(path, title, body, 0, unit))
        for w in words:
            book.redirects.append((f"word/{w}", w, path))
    book.published = published
    book.version = f"OEWN {edition} (git tag {edition}-edition, commit {commit[:12]})"
    book.originals = [{"url": f"{OEWN_REPO}/tree/{edition}-edition", "kind": "html"},
                      {"url": f"{OEWN_RAW}/{edition}-edition/LICENSE.md", "kind": "txt"},
                      {"url": f"{OEWN_RAW}/{edition}-edition/WNDB_License.txt", "kind": "txt"}]
    return book


NOTICE = ("Open English WordNet: Copyright (c) 2019-present, The Open English WordNet Team, licensed under the "
          "Creative Commons Attribution 4.0 International License (https://creativecommons.org/licenses/by/4.0/). "
          "This work is based on or incorporates elements of the Princeton University WordNet database; attribution "
          "is given to both Princeton WordNet and the Open English Wordnet team. WordNet 3.1 Copyright 2011 by "
          "Princeton University. All rights reserved. THIS SOFTWARE AND DATABASE IS PROVIDED \"AS IS\" AND "
          "PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES, EXPRESS OR IMPLIED. BY WAY OF EXAMPLE, BUT "
          "NOT LIMITATION, PRINCETON UNIVERSITY MAKES NO REPRESENTATIONS OR WARRANTIES OF MERCHANTABILITY OR FITNESS "
          "FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF THE LICENSED SOFTWARE, DATABASE OR DOCUMENTATION WILL NOT "
          "INFRINGE ANY THIRD PARTY PATENTS, COPYRIGHTS, TRADEMARKS OR OTHER RIGHTS. The name of Princeton "
          "University or Princeton may not be used in advertising or publicity pertaining to distribution of the "
          "software and/or database. Title to copyright in this software, database and any associated documentation "
          "shall at all times remain with Princeton University. Changed: written out as a dictionary for reading "
          "offline.")


def newest_edition():
    """(edition "2025", tag "2025-edition") of the newest yearly edition tag of the repository (git ls-remote)."""
    out = subprocess.run(["git", "ls-remote", "--tags", OEWN_REPO], capture_output=True, text=True,
                         timeout=120).stdout
    years = sorted({int(m) for m in re.findall(r"refs/tags/(\d{4})-edition$", out, re.M)})
    if not years:
        raise ValueError("no edition tag")
    return str(years[-1]), f"{years[-1]}-edition"


def books_for(key, work, cache=None, left_out=None, limit=None):
    """The Books of one key (dict:oewn), or [] (the reason in left_out)."""
    import build_textbooks as B
    left_out = left_out if left_out is not None else []
    if key != "dict:oewn":
        left_out.append({"title": key, "reason": "Unknown key."})
        return []
    edition, tag = newest_edition()
    for name, pattern in (("LICENSE.md", LICENCE_TEXT), ("WNDB_License.txt", WNDB_TEXT)):
        url = f"{OEWN_RAW}/{tag}/{name}"
        try:
            ok = R.readable(url, cache) and re.search(pattern, B.fetch(url, cache))
        except (urllib.error.URLError, OSError):
            ok = False
        if not ok:
            left_out.append({"title": "Open English WordNet", "reason": f"Its {name} could not be read or no longer "
                             "states the licence that was checked."})
            return []
    dest = R.shallow_clone(OEWN_REPO, work, ["/src/yaml/", "/LICENSE.md", "/WNDB_License.txt"], ref=tag)
    commit, date = R.git_facts(dest)
    return [wordnet_book(os.path.join(dest, "src", "yaml"), edition, commit, date, limit)]


def all_keys():
    """Every build key of this module."""
    return ["dict:oewn"]


def knows(word):
    """True when word is one of this module's request words or keys."""
    return word in WORDS or word.startswith("dict:")


def expand_keys(words):
    """The keys the words stand for: "wordnet", "dictionary", "thesaurus" or "group:dictionaries" (the book), or one
    key (kept as it is)."""
    keys = []
    for w in words:
        keys += all_keys() if w in WORDS else [w]
    return list(dict.fromkeys(keys))


def sign(key):
    """The weekly check's sign of change: the newest edition tag (a new yearly edition is a new version)."""
    try:
        return newest_edition()[1] if key == "dict:oewn" else ""
    except (OSError, ValueError, subprocess.SubprocessError):
        return ""


def build(keys, out_dir, cache=None, date=None, limit=None):
    """Build the book into out_dir with one manifest per key (refs_common.build_keys)."""
    return R.build_keys(R._module("wordnet_dict"), keys, out_dir, cache, date, limit)  # (also when run as a script)


LICENCE_LINES = {
    "open_english_wordnet": "github.com/globalwordnet/english-wordnet LICENSE.md (read 2026-11-22, checked again at "
                            "every build): \"This resource is derived from Princeton WordNet under the WordNet "
                            "License and further developed under the Creative Commons Attribution 4.0 International "
                            "License. You may share and adapt this resource providing attribution is given to both "
                            "Princeton WordNet and the Open English Wordnet team.\" WNDB_License.txt: the WordNet "
                            "licence (\"Permission to use, copy, modify and distribute this software and database "
                            "and its documentation for any purpose and without fee or royalty is hereby granted\", "
                            "with Princeton's copyright notice and disclaimer on all copies: in the book's notice). "
                            "Read by git clone (GitHub's robots.txt disallows release downloads, so they are not "
                            "fetched); raw.githubusercontent.com has no robots rules.",
}

NOT_INCLUDED = [
    ("Princeton WordNet 3.0 and 3.1 (wordnet.princeton.edu)", "Not built separately: its licence is permissive "
     "(the WordNet licence, checked 2026-11-22), but Open English WordNet, which is built in full (dict:oewn), is its "
     "continuation: it holds all of Princeton WordNet 3.1 with thousands of corrections and new words since 2019. "
     "Princeton's own last release was 3.1 (2011). Index: https://wordnet.princeton.edu/download"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("keys", nargs="*", default=["wordnet"])
    p.add_argument("--out", default="build/textbooks")
    p.add_argument("--cache", default=None)
    p.add_argument("--limit", type=int, default=None, help="a small test build: only so many words")
    p.add_argument("--list", action="store_true", help="only print the keys the words stand for")
    a = p.parse_args(argv)
    if a.list:
        print("\n".join(expand_keys(a.keys)))
        return 0
    build(a.keys, a.out, a.cache, limit=a.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
