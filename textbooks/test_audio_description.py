"""Self-test of the picture and video description books (audio_description.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once under its request word "describer-guides" (at most 256 jobs) and
reaches sources.py with its group, licence lines and NOT_INCLUDED rows (each saying where to find the source); that
the CFR book is 47 CFR part 79 and goes through the library's CFR builder with this module's group and notice; and
that the index names only books, packs and links that exist (each picture pack is a real pack of the repository).

Run it from the repository's folder:   python3 -m pytest textbooks/test_audio_description.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio_description as A  # noqa: E402
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402


def test_registered():
    assert A in more_refs.modules()
    keys = sources.expand_keys(["describer-guides"])
    assert keys == A.COLLECTION.expand_keys(["describer-guides"]) and len(keys) == len(set(keys)) <= 256
    assert keys == ["describe:index", "describe:cfr_47_79_video_accessibility"]
    assert A.GROUP in sources.GROUPS
    assert set(A.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_cfr_book_uses_the_cfr_builder(monkeypatch):
    seen = {}

    def fake_lawdoc(entry, cache=None, left_out=None):
        """Record the entry instead of building."""
        seen.update(entry)
        return None

    monkeypatch.setattr(B, "lawdoc_book", fake_lawdoc)
    A.cfr_book("cfr_47_79_video_accessibility", None)
    assert seen["cfr"] == dict(title=47, volume=4, part=79, subpart="")
    assert seen["group"] == A.GROUP and seen["name"] == "describe_cfr_47_79_video_accessibility"
    assert seen["notice"] == A.NOTICE and "public domain" in A.NOTICE


def test_index_entries():
    sys.path.insert(0, os.path.join(HERE, "..", "packs"))
    import build_packs
    for _part, intro, entries in A.SECTIONS:
        assert intro
        for kind, what, words, *more in entries:
            assert kind in ("key", "pack", "link"), kind
            if kind == "pack":
                assert what in build_packs.PACKS, what
            if kind == "link":
                assert what.startswith(("http",)) is False and words.startswith("https://") and more[0]
            if kind == "key":
                assert ":" in what and words


def test_not_included():
    for row in A.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in A.NOT_INCLUDED)
    for words in ("DCMP Description Key", "American Council of the Blind", "FCC"):
        assert words in names, words
