"""Self-test of the Peace Corps manuals and guides (peace_corps.py), with MADE-UP data only: nothing is downloaded.

It checks that the module is registered once and reaches sources.py; that every request word stands for at most 256
keys and the theme words together cover every book; that no Internet Archive item is built twice (here, in another
collection, or by the approtech helper); that every book has a licence the toolkit may repackage and a notice that
states its basis truthfully (an office's work, no notice before 1989, or the Peace Corps' reproduction words); that
every health book says to follow current medical guidance (and the HIV books more); that the index is made offline,
lists every book by theme, and finds a made-up Peace Corps book in another collection; and that every row of
NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_peace_corps.py
"""

import os
import re
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import refs_kit as K  # noqa: E402
import sources  # noqa: E402
import peace_corps as P  # noqa: E402


def test_registered():
    assert more_refs.MODULES.count("peace_corps") == 1 and P in more_refs.modules()
    assert sources.GROUPS[P.GROUP] == "Reference, Peace Corps manuals and guides"
    assert set(P.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    for licence in (P.PC_NO_NOTICE, P.PC_PERMISSION):
        assert sources.ALLOWED.get(licence) == "open"


def test_words_and_sizes():
    themed = []
    for theme, (word, _heading) in P.THEMES.items():
        keys = sources.expand_keys([word])
        assert keys == P.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256, word
        assert keys[0] == "pc:index" and len(keys) > 1, word
        themed += keys[1:]
    everything = sources.expand_keys(["peace-corps"])
    assert len(everything) == len(set(everything)) <= 256
    assert set(everything) == set(P.COLLECTION.own_keys()) == {"pc:index"} | set(themed)
    assert len(themed) == len(set(themed)) == len(P.BOOKS)      # each book in exactly one theme
    for key in everything:
        assert more_refs.module_for(key) is P, key


def test_no_duplicates():
    names = [r[1] for r in P.BOOKS]
    items = [r[2] for r in P.BOOKS]
    assert len(names) == len(set(names)) and len(items) == len(set(items))
    assert not set(items) & P.APPROTECH_ITEMS
    elsewhere = set()
    for m in more_refs.modules():
        if m is P:
            continue
        for e in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values()):
            elsewhere.add(e.get("archive"))
    for e in sources.PDF_DOCS:
        elsewhere.add(e.get("archive"))
    assert not set(items) & elsewhere
    # the ERIC number is never built twice under its two Internet Archive names
    numbers = [re.sub(r"^ERIC_", "", i) for i in items if i.startswith("ERIC_")]
    assert len(numbers) == len(set(numbers))


def test_every_book():
    for row, e in zip(P.BOOKS, P.PDFS):
        theme, name, item, year, title, _ice, lang, kind, desc = row
        assert theme in P.THEMES and re.fullmatch(r"[a-z0-9_]+", name), name
        assert re.fullmatch(r"(ERIC_ED\d{6}|micro_IA\d{8}_\d{4})", item), name
        assert 1960 < int(year) <= 2026 and lang in ("eng", "spa", "fra"), name
        assert set(kind) <= set("opgchvr") and len([k for k in kind if k in "opgc"]) <= 1, name
        assert desc and title and e["archive"] == item and e["group"] == P.GROUP, name
        assert B.licence_kind(e["licence"]) == "open", name
        assert e["published"] == year and item in e["version"] and e["notice"] and e["description"], name
        letter = P.kind_letters(kind)
        if letter in "opg" and letter:
            assert e["licence"] == K.US_GOV and e["licence_page"] == K.GOVINFO_POLICY, name
            assert "17 U.S.C. 105" in e["notice"], name
        elif letter == "c":
            assert P.REPRODUCE in e["notice"] and P.CREDIT in e["notice"], name
            assert e["licence"] == (P.PC_PERMISSION if int(year) >= 1989 else P.PC_NO_NOTICE), name
        else:
            assert int(year) < 1989 and e["licence"] == P.PC_NO_NOTICE, name
            assert "no copyright notice" in e["notice"], name
        if "r" in kind:
            assert P.REPRINTS[name] in e["notice"] and "remain their owners' copyright" in e["notice"], name
        assert ("scan of ERIC's microfiche" in e["notice"]) == item.startswith("micro_IA"), name
        assert e["language"] == ("" if lang == "eng" else lang), name
    assert set(P.REPRINTS) == {r[1] for r in P.BOOKS if "r" in r[7]}


def test_health_notes():
    health = [(r, e) for r, e in zip(P.BOOKS, P.PDFS) if r[0] == "health"]
    assert len(health) >= 10
    for r, e in health:
        assert "h" in r[7], r[1]
    for r, e in zip(P.BOOKS, P.PDFS):
        if "h" in r[7]:
            assert "Follow current medical guidance" in e["notice"] and f"from {r[3]}" in e["notice"], r[1]
        if re.search(r"\b(HIV|AIDS)\b", r[4]):
            assert "v" in r[7] and "HIV testing, treatment and prevention have changed" in e["notice"], r[1]


def test_index_offline(monkeypatch):
    """The index is made without reading the web; every book is listed under its theme, and a made-up Peace Corps
    book of another collection appears on the last page with its request word."""
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    fake = types.SimpleNamespace(COLLECTION=K.Collection(
        "madeup", "madeup", pdfs=[dict(name="pc_wells", title="Made-up Wells Manual", publisher="Peace Corps ICE",
                                       archive="made-up-item")],
        words={"madeup-water": lambda: ["madeup:pc_wells"]}))
    real = more_refs.modules
    monkeypatch.setattr(more_refs, "modules", lambda: real() + [fake])
    left_out = []
    book_fn, sign_fn = P.COLLECTION.makers["index"]
    book = book_fn("index", "work", None, left_out)
    assert book.licence == "CC0 1.0" and not left_out, left_out
    text = " ".join(p.body for p in book.pages)
    for r in P.BOOKS:
        assert f"(key pc:{r[1]})" in text, r[1]
    for word, _heading in P.THEMES.values():
        assert f"request word {word}" in text, word
    assert "Made-up Wells Manual (key madeup:pc_wells; request word madeup-water)" in text
    assert "relate:peace_corps_culture_matters" in text and '<a href="https://' in text
    assert sign_fn("index")


def test_not_included():
    for row in P.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in P.NOT_INCLUDED)
    for words in ("Boston University", "American Public Health Association", "Hesperian", "UNESCO", "Water in Africa",
                  "approtech", "peacecorps.gov"):
        assert words in names + " ".join(r[1] for r in P.NOT_INCLUDED), words
