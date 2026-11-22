"""Self-test of the personal care, toys and world money books (personal_care.py, toys_books.py, world_money.py), with
MADE-UP data only: nothing is downloaded.

It checks that each module is registered once under its request word (at most 256 jobs) and reaches sources.py; that
every book has a licence the toolkit may repackage, a description, a licence page and line, a notice with its safety
or money note, and a page pattern that matches its own addresses; that the central banks' books are kept whole with
their credit in the notice; that every key an index lists is a book of the library; that pages are read in the order
listed; and that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_gaps_pictures.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import personal_care as P  # noqa: E402
import toys_books as T  # noqa: E402
import world_money as W  # noqa: E402

MODULES = ((P, "personal-care", "pcare", P.CARE_SAFETY), (T, "toys", "toys", T.TOY_SAFETY),
           (W, "world-money", "wmoney", W.MONEY_NOTE))


def test_registered():
    for module, word, prefix, _note in MODULES:
        assert module in more_refs.modules()
        keys = sources.expand_keys([word])
        assert keys == module.COLLECTION.expand_keys([word]) and len(keys) == len(set(keys)) <= 256
        assert set(keys) == set(module.COLLECTION.own_keys()) and f"{prefix}:index" in keys
        assert set(module.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get(W.ECB_LICENCE) == "open" and sources.ALLOWED.get(W.BOC_LICENCE) == "open"


def test_notes_say_what_the_owner_asked():
    for words in ("patch test", "eyebrows or eyelashes", "1-800-222-1222", "FDA"):
        assert words in P.CARE_SAFETY, words
    for words in ("under 3", "button or coin batteries", "magnets", "helmet", "SaferProducts.gov"):
        assert words in T.TOY_SAFETY, words
    assert "free currency reader" in W.MONEY_NOTE


def test_every_book():
    for module, _word, _prefix, note in MODULES:
        entries = list(module.COLLECTION.guides.values()) + list(module.COLLECTION.pdfs.values())
        assert entries, module.__name__
        for g in entries:
            assert g["group"] in sources.GROUPS, g["name"]
            whole = bool(g.get("unchanged"))
            short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
            assert B.licence_kind(short, whole), g["name"]
            assert g["notice"] and g["description"] and g["licence_page"] and g["licence_text"], g["name"]
            assert note in g["notice"], g["name"]
            if g["name"] in module.COLLECTION.guides:
                pattern = re.compile(g["pages"])
                for url in g.get("urls", []):
                    assert pattern.match(url), (g["name"], url)
                assert pattern.match(g["source"]), g["name"]
            else:
                assert g["archive"] and g["published"] and g["version"], g["name"]


def test_central_banks_kept_whole_with_credit():
    for g in W.GUIDES:
        assert g["unchanged"] and W.UNCHANGED_NOTE in g["notice"], g["name"]
        assert g["country"] != "United States", g["name"]
    rba = W.COLLECTION.guides["rba_banknote_accessibility"]
    assert rba["licence"] == "CC BY 4.0" and "creativecommons.org/licenses/by/4.0" in rba["notice"]
    assert B.licence_short(rba["licence"]) == "CC BY 4.0"
    ecb = W.COLLECTION.guides["ecb_visually_impaired"]
    assert "cited as the source" in ecb["notice"] and "free of charge" in ecb["notice"]
    boc = W.COLLECTION.guides["boc_blind_partially_sighted"]
    assert "attribution" in boc["notice"] and "not endorsed" in boc["notice"]
    for licence in (W.ECB_LICENCE, W.BOC_LICENCE):
        assert B.licence_short(licence) == licence                  # never read as a Creative Commons licence


def test_fda_books():
    for g in P.GUIDES:
        assert g["licence_page"] == P.FDA_POLICY and g["publisher"] == P.FDA_PUBLISHER, g["name"]
    products = P.COLLECTION.guides["fda_cosmetic_products"]
    assert any(u.endswith("/hair-dyes") for u in products["urls"])
    assert re.compile(P.PAGES).match("https://www.fda.gov/cosmetics/cosmetic-products/hair-dyes")
    assert not re.compile(P.PAGES).match("https://www.fda.gov/food/cosmetics")


def listed_names(folder, code):
    """The names a small program prints in another folder of the repository (the packs' and manuals' modules share
    names with this folder's, so they are read in their own process)."""
    import subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run([sys.executable, "-c", code], cwd=os.path.join(here, "..", folder), capture_output=True,
                         text=True, check=True, timeout=300).stdout
    return set(out.split())


def test_index_keys_exist():
    """Every key an index lists is a book of the library (else the index would leave it out), and every pack and
    manual collection it names exists."""
    packs = listed_names("packs", "import build_packs; print(' '.join(build_packs.PACKS))")
    manuals = listed_names("manuals", "import categories; print(' '.join(categories.CATEGORIES))")
    for module in (P, T, W):
        for _part, _intro, entries in module.SECTIONS:
            for kind, what, *rest in entries:
                if kind == "key":
                    assert X.key_exists(what), what
                elif kind == "pack":
                    assert what in packs, what
                elif kind == "manuals":
                    assert what in manuals, what
                elif kind == "word":
                    assert sources.expand_keys([what]) != [what], what
                else:
                    assert kind == "link" and rest[0].startswith("http"), what


def test_pages_read_in_order(monkeypatch):
    """A fixed-list guide is read in the order listed, its first page first, and nothing else is fetched."""
    monkeypatch.setattr(D, "readable", lambda url, cache=None: True)
    monkeypatch.setattr(B, "fetch", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch")))
    found = [u for u, _unit in D.crawl(P.COLLECTION.guides["fda_cosmetics_safety"], None)]
    assert found == P.SAFETY_PAGES
    found = [u for u, _unit in D.crawl(W.COLLECTION.guides["rba_banknote_accessibility"], None)]
    assert found == W.RBA_PAGES


def test_not_included():
    for module in (P, T, W):
        assert module.NOT_INCLUDED
        for row in module.NOT_INCLUDED:
            assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for m in (P, T, W) for r in m.NOT_INCLUDED)
    for words in ("Open Beauty Facts", "CPSC", "Strong", "V&A", "New Zealand", "Bank of England"):
        assert words in names, words
