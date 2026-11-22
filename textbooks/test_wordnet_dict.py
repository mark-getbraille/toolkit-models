"""Self-test of the Open English WordNet dictionary added on 2026-11-22 (wordnet_dict.py), with MADE-UP words only:
nothing is downloaded.

It checks that:
  - the book is registered in the group "dictionaries" with a licence the toolkit may repackage, asked for by
    wordnet, dictionary, thesaurus and dict:oewn; the builder and the weekly check send dict: keys here;
  - the small YAML reader reads what OEWN writes (quoted keys with doubled quotes, plain scalars over two lines,
    lists of mappings, examples with a source);
  - a word's entry has its parts of speech, pronunciation, definitions, examples, synonyms, broader and narrower
    terms (the narrower ones worked out from the broader), opposites and related forms, linked to the words' pages;
  - words are grouped alphabetically into pages that never cross a letter, each word a search title (a redirect);
  - the licence files are checked (the WordNet licence's numbered lines included) before anything is cloned.

Run it from the repository's folder:   python3 -m pytest textbooks/test_wordnet_dict.py
"""

import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import refs_common as R  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402
import wordnet_dict as W  # noqa: E402

ENTRIES = """'''hood':
  n:
    sense:
    - id: '''hood%1:14:01::'
      synset: 00000003-n
dog:
  n:
    pronunciation:
    - value: dɒɡ
      variety: GB
    sense:
    - id: dog%1:05:00::
      synset: 00000001-n
  v:
    form:
    - dogged
    sense:
    - synset: 00000010-v
cat:
  n:
    sense:
    - id: cat%1:05:00::
      synset: 00000002-n
      derivation:
      - catty%3:00:00::
catty:
  a:
    sense:
    - id: catty%3:00:00::
      synset: 00000020-a
      antonym:
      - kind%3:00:00::
kind:
  a:
    sense:
    - id: kind%3:00:00::
      synset: 00000021-a
domestic dog:
  n:
    sense:
    - synset: 00000001-n
"""
SYNSETS = """00000001-n:
  definition:
  - a member of the genus Canis that has been domesticated by man since
    prehistoric times
  example:
  - the dog barked all night
  - source: Made-up Author
    text: 'it''s a good dog'
  hypernym:
  - 00000004-n
  members:
  - dog
  - domestic dog
  partOfSpeech: n
00000002-n:
  definition:
  - a small domesticated feline
  hypernym:
  - 00000004-n
  members:
  - cat
  partOfSpeech: n
00000003-n:
  definition:
  - a neighbourhood
  members:
  - '''hood'
  partOfSpeech: n
00000004-n:
  definition:
  - a domesticated animal
  members:
  - pet
  partOfSpeech: n
"""


def make_wordnet():
    """A tiny Wordnet from the made-up YAML."""
    wn = W.Wordnet()
    wn.add_entries(W.yaml_load(ENTRIES))
    wn.add_synsets(W.yaml_load(SYNSETS))
    wn.add_synsets({"00000010-v": {"definition": ["go after"], "members": ["dog"]},
                    "00000020-a": {"definition": ["spiteful"], "members": ["catty"]},
                    "00000021-a": {"definition": ["gentle"], "members": ["kind"]}})
    wn.finish()
    return wn


def test_registered_in_the_dictionaries_group():
    assert sources.GROUPS["dictionaries"] == "Reference, dictionaries and thesauri"
    for word in ("wordnet", "dictionary", "thesaurus", "group:dictionaries", "dict:oewn"):
        assert sources.expand_keys([word]) == ["dict:oewn"], word
    assert R.module_for("dict:oewn") is W
    assert B.licence_kind(B.licence_short(W.CC_BY), False) == "open"
    assert set(W.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in W.NOT_INCLUDED)
    assert "Princeton University" in W.NOTICE and "AS IS" in W.NOTICE


def test_builder_and_weekly_check_send_dict_keys_here(monkeypatch, tmp_path):
    monkeypatch.setattr(W, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("dict:oewn") == "signed dict:oewn"
    called = []
    monkeypatch.setattr(W, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["dict:oewn"], str(tmp_path))
    assert called == [["dict:oewn"]]


def test_yaml_reader():
    entries = W.yaml_load(ENTRIES)
    assert list(entries)[:2] == ["'hood", "dog"]
    assert entries["'hood"]["n"]["sense"][0] == {"id": "'hood%1:14:01::", "synset": "00000003-n"}
    assert entries["dog"]["n"]["pronunciation"] == [{"value": "dɒɡ", "variety": "GB"}]
    syn = W.yaml_load(SYNSETS)["00000001-n"]
    assert syn["definition"] == ["a member of the genus Canis that has been domesticated by man since prehistoric "
                                 "times"]
    assert syn["example"] == ["the dog barked all night", {"source": "Made-up Author", "text": "it's a good dog"}]
    assert W.yaml_load('a: "two \\"quoted\\"\n  words"\n') == {"a": 'two "quoted" words'}


def test_entry():
    wn = make_wordnet()
    where = {w: ("words-x", W.anchor(w)) for w in wn.entries}
    dog = W.entry_html(wn, "dog", where)
    assert dog.index("<h3>dog, noun</h3>") < dog.index("<h3>dog, verb</h3>")
    for words in ("Pronunciation: /dɒɡ/ (GB)", "since prehistoric times", "Other forms: dogged",
                  "Examples: “the dog barked all night”; “it&#x27;s a good dog” (Made-up Author)",
                  'Synonyms: <a href="words-x#w-domestic-dog">domestic dog</a>', "Broader terms: pet"):
        assert words in dog, words
    pet = W.entry_html(wn, "cat", where)
    assert 'Related forms: <a href="words-x#w-catty">catty</a>' in pet
    assert "Opposite: " in W.entry_html(wn, "catty", where)
    assert wn.synsets["00000004-n"]["hyponym"] == ["00000001-n", "00000002-n"]    # narrower terms, worked out
    assert W.anchor("A-line") != W.anchor("A line") and W.anchor("dog") == "w-dog"


def test_pages_by_letter(monkeypatch):
    monkeypatch.setattr(W, "WORDS_PER_PAGE", 2)
    pages = W.plan_pages(["cat", "'hood", "dog", "domestic dog", "doge", "3D", "catty"])
    assert [(u, words) for u, _p, words in pages] == [("Numbers and symbols", ["3D"]), ("C", ["cat", "catty"]),
                                                     ("D", ["dog", "doge"]), ("D", ["domestic dog"]),
                                                     ("H", ["'hood"])]
    assert len({p for _u, p, _w in pages}) == len(pages)


def test_book(monkeypatch, tmp_path):
    folder = tmp_path / "yaml"
    folder.mkdir()
    (folder / "entries-a.yaml").write_text(ENTRIES, encoding="utf-8")
    (folder / "noun.animal.yaml").write_text(SYNSETS, encoding="utf-8")
    book = W.wordnet_book(str(folder), "2025", "abcdef1234567890", "2025-11-01")
    assert book.licence == "CC BY 4.0" and book.published == "2025-11-01" and "2025" in book.version
    assert ("word/dog", "dog", "words-dog") in book.redirects and ("word/'hood", "'hood", "words-hood") in book.redirects
    assert [p.title for p in book.pages] == ["cat to catty", "dog to domestic dog", "'hood", "kind"]
    assert [p.unit for p in book.pages] == ["C", "D", "H", "K"]
    assert any(o["url"].endswith("WNDB_License.txt") for o in book.originals)


def test_licence_checked_before_cloning(monkeypatch):
    monkeypatch.setattr(W, "newest_edition", lambda: ("2025", "2025-edition"))
    monkeypatch.setattr(R, "shallow_clone", lambda *a, **k: (_ for _ in ()).throw(AssertionError("cloned")))

    def fetch(url, cache=None, binary=False, tries=4):
        if url.endswith("LICENSE.md"):
            return "further developed under the Creative Commons Attribution 4.0\nInternational License."
        if url.endswith("WNDB_License.txt"):
            return "  7 Permission to use, copy, modify and distribute this software and  \n  8 changed words"
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(D, "_ai", {})
    left_out = []
    assert W.books_for("dict:oewn", "work", None, left_out) == []
    assert "WNDB_License.txt" in left_out[0]["reason"]
    assert __import__("re").search(W.WNDB_TEXT, "Permission to use, copy, modify and distribute this software and  \n  8 database")
