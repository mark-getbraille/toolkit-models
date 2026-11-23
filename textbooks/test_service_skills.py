"""Self-test of the job-skill training manuals (textbooks/service_skills.py, skill:), with MADE-UP data only: nothing
is downloaded.

It checks that the module is registered once (its own prefix and group "Reference, job skills (US military training
manuals)") and reaches sources.py; that the overall request word service-skills and every trade's word stay at most
256 books, the trade words together covering every book once; that every book is a US military manual judged by the
release rule (distribution_a), read whole with only explosives parts cut, with a notice that names the service, the
publication number, the year and its basis, the copyright basis and the copy's source, and carries its trade's
safety note (the medical ones "follow current medical guidance"); that no Internet Archive item is used twice here or
anywhere else in the library; that the index lists only keys the library has; that a made-up restricted front page
sends a manual to left_out as personal use; and that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_service_skills.py
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import service_skills as S  # noqa: E402
import sources  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def test_registered_with_own_group_and_words():
    assert S in more_refs.modules()
    prefixes = [m.COLLECTION.prefix for m in more_refs.modules()]
    assert prefixes.count("skill") == 1
    assert sources.GROUPS["skills"] == "Reference, job skills (US military training manuals)"
    every = sources.expand_keys([S.ALL_WORD])
    assert every == S.COLLECTION.expand_keys([S.ALL_WORD])
    assert every[0] == "skill:index" and 0 < len(every) == len(set(every)) <= 256
    assert set(every) == set(S.COLLECTION.own_keys())
    seen = []
    for trade, (word, title, safety, covers) in S.TRADES.items():
        keys = sources.expand_keys([word])
        assert 0 < len(keys) == len(set(keys)) <= 256, word
        assert word.startswith("service-skills-") and title and safety and covers, trade
        seen += keys
    assert sorted(seen) == sorted(k for k in every if k != "skill:index")      # every book in exactly one trade
    assert set(S.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_every_book_is_a_whole_military_manual():
    names = [p["name"] for p in S.PDFS]
    assert len(names) == len(set(names))
    for p in S.PDFS:
        assert p["group"] == "skills" and p["archive"] and p["description"], p["name"]
        assert p["distribution_a"] is True and p["licence"] == sources.US_GOV, p["name"]
        assert p["work"].startswith("a work of the US"), p["name"]
        assert re.fullmatch(r"(19[4-9]\d|20[0-2]\d)", p["published"]), p["name"]
        n = p["notice"]
        assert n.startswith(S.NOTICE) and S.TRADES[p["trade"]][2] in n, p["name"]
        assert "17 U.S.C. 105" in n and "public domain" in n and p["archive"] in n, p["name"]
        assert p["published"] in n and S.SERVICES[p["service"]] in n, p["name"]
        assert "explosives" in n, p["name"]
        assert not B.NOT_FIELD_SAFE.search(p["title"]), p["name"]           # no explosives manual at all
    assert "follow current medical guidance" in S.MEDICAL_SAFETY
    for words in ("breaker", "electrician", "safety data sheet", "certified riggers", "911", "FAA", "allergens",
                  "veterinarian", "licence"):
        assert any(words in t[2] for t in S.TRADES.values()), words


def test_only_explosives_parts_are_cut():
    for title in ("Chapter 6: Demolitions", "Lesson 4: Land Mines", "Appendix B: Blasting In Quarries",
                  "Chapter 9: Booby Traps"):
        assert B.NOT_FIELD_SAFE.search(title), title
    for title in ("Lesson 2: Taking A Pulse", "Chapter 3: Pipe Fitting", "Lesson 1: Basic Electricity",
                  "Chapter 7: Structural Fire Fighting", "Chapter 4: Dive Planning"):
        assert not B.NOT_FIELD_SAFE.search(title), title


def test_nothing_used_twice_in_the_library():
    mine = [p["archive"] for p in S.PDFS]
    assert len(mine) == len(set(mine))
    other = set()
    for m in more_refs.modules():
        if m is S:
            continue
        other |= {g.get("archive") for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())}
    other |= {g.get("archive") for g in sources.PDF_DOCS}
    assert not set(mine) & other, set(mine) & other
    # any other file of the library (cookbooks, history and the rest keep their own lists): the item's name in quotes
    code = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.basename(path) not in ("service_skills.py", "test_service_skills.py"):
            code += open(path, encoding="utf-8").read()
    assert not [a for a in mine if f'"{a}"' in code]


def test_index_links_existing_books():
    keys = [e[1] for _part, _intro, items in S.SECTIONS for e in items if e[0] == "key"]
    assert keys and all(X.key_exists(k) for k in keys), [k for k in keys if not X.key_exists(k)]
    words = [e[1] for _part, _intro, items in S.SECTIONS for e in items if e[0] == "word"]
    for trade, (word, *_rest) in S.TRADES.items():
        assert word in words, word
    for word in words:
        assert sources.expand_keys([word]) != [word], word                   # a request word the library knows
    for _part, _intro, items in S.SECTIONS:
        for e in items:
            if e[0] == "link":
                assert e[2].startswith("https://") and e[3], e
    book, _sign = S.INDEX
    built = book("index", "work", None, [], None)
    assert len(built.pages) == len(S.SECTIONS) and built.licence == "CC0 1.0"


def test_restricted_copy_goes_to_left_out(monkeypatch, tmp_path):
    """A made-up restricted front page: the builder puts the manual in left_out as personal use, never a book."""
    entry = dict(S.PDFS[0], licence_page="", licence_text="")
    monkeypatch.setattr(B, "archive_pdf", lambda ident, cache=None: (
        "https://archive.org/download/made-up/made-up.pdf", "https://archive.org/details/made-up"))
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    (tmp_path / f"{entry['name']}.pdf").write_bytes(b"%PDF-1.4 made up")

    class Words:
        count = 4

        def __init__(self, path):
            pass

        def lines(self, n):
            return ["Made-up words about cooking for a hundred people, long enough to count as a text layer here."]

    monkeypatch.setattr(B, "PdfText", Words)
    monkeypatch.setattr(B, "front_text", lambda path, pages=12: "DISTRIBUTION RESTRICTION: Distribution authorized "
                        "to U.S. Government agencies only.")
    left_out = []
    assert B.pdfdoc_book(entry, str(tmp_path), None, left_out) is None
    assert left_out and left_out[0]["personal_use"] and left_out[0]["fetch_yourself"]


def test_not_included_rows():
    assert S.NOT_INCLUDED
    for row in S.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: https://" in row[1], row[0]
