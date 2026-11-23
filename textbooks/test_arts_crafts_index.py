"""Self-test of the arts and crafts guide (arts_crafts_index.py) and of the move of the craft books into the one
top-level group "Reference, arts and crafts" (the owner's request of 22 November 2026), with MADE-UP data only (the craft
trade pages of 23 November 2026 included):
nothing is downloaded.

It checks that the module is registered under its request word "arts-crafts" (at most 256 jobs) in the arts and crafts
group; that its key prefix "arts:" clashes with no other module; that the index lists every craft book (the textile
craft books of home_crafts.py, the sewing books of thin_topics.py, every book of crafts_books.py and craft_trades.py,
and homestead.py's two old beekeeping books) and the photography
collection, and no home repair book; that every key, pack and manual collection it names exists; that the craft books
keep their keys and request words; and that two modules sharing the "craft:" prefix each build their own keys.

Run it from the repository's folder:   python3 -m pytest textbooks/test_arts_crafts_index.py
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arts_crafts_index as A  # noqa: E402
import craft_trades as CT  # noqa: E402
import crafts_books as CB  # noqa: E402
import home_crafts as HC  # noqa: E402
import more_refs  # noqa: E402
import open_catalogues as OC  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import thin_topics as TT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def listed_names(folder, code):
    """The names a small program prints in another folder of the repository (the packs' and manuals' modules share
    names with this folder's, so they are read in their own process)."""
    out = subprocess.run([sys.executable, "-c", code], cwd=os.path.join(HERE, "..", folder), capture_output=True,
                         text=True, check=True, timeout=300).stdout
    return set(out.split())


def listed_keys():
    """Every book key the index lists."""
    return {what for _p, _i, entries in A.SECTIONS for kind, what, *_r in entries if kind == "key"}


def test_registered_in_the_arts_and_crafts_group():
    assert A in more_refs.modules() and more_refs.MODULES.count("arts_crafts_index") == 1
    assert sources.GROUPS[A.GROUP] == "Reference, arts and crafts" and A.GROUP == CB.GROUP
    keys = sources.expand_keys(["arts-crafts"])
    assert keys[0] == "arts:index" and len(keys) == len(set(keys)) <= 256
    assert more_refs.module_for("arts:index") is A and more_refs.module_for("arts-crafts") is A
    assert [m for m in more_refs.modules() if m.COLLECTION.prefix == "arts"] == [A]
    assert set(A.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_index_lists_every_craft_book_and_photography():
    keys = listed_keys()
    crafts = {f"craft:{g['name']}" for g in CB.GUIDES + CB.PDFS}
    textiles = {f"craft:{g['name']}" for g in HC.GUIDES + HC.PDFS if g["group"] == "crafts"}
    sewing = {f"pdf:{e['name']}" for e in TT.SEWING}
    trades = {f"ctrade:{e['name']}" for e in CT.GUIDES + CT.PDFS}
    bees = {what for _k, what, _t in A.HOMESTEAD_BEE_KEYS}
    service = {"skill:army_fm_10_16_general_fabric_repair_2000"}      # service_skills.py's, on the leather page
    service |= {what for _k, what, _t in A.PEACE_CORPS_BEE_KEYS + A.TANNING_KEYS}   # approtech's and hfill's
    assert crafts | textiles | sewing | trades | bees | service | {"make:index"} == keys
    assert "craft:webster_quilts_1915" in textiles and "craft:mickel_leather_work_1915" in textiles
    home_repair = {f"craft:{g['name']}" for g in HC.GUIDES + HC.PDFS if g["group"] == HC.GROUP}
    assert "craft:epa_safe_pest_control" in home_repair and not home_repair & keys
    words = [(kind, what) for _p, _i, entries in A.SECTIONS for kind, what, *_r in entries]
    assert ("word", "photography") in words
    titles = [t for t, _i, _e in A.SECTIONS]
    assert "Photography" in titles and "Textile crafts" == titles[0]
    assert not [t for t, _i, entries in A.SECTIONS if not entries], "a part with nothing in it"


def test_index_keys_packs_and_manuals_exist():
    packs = listed_names("packs", "import build_packs; print(' '.join(build_packs.PACKS))")
    manuals = listed_names("manuals", "import categories; print(' '.join(categories.CATEGORIES))")
    for _part, _intro, entries in A.SECTIONS:
        for kind, what, *_rest in entries:
            if kind == "key":
                assert X.key_exists(what), what
            elif kind == "pack":
                assert what in packs, what
            elif kind == "manuals":
                assert what in manuals, what


def test_index_book_lists_only_keys_the_library_has(monkeypatch, tmp_path):
    """The index book (made-up check of key_exists): a key the library lacks is left out and said."""
    real = X.key_exists
    monkeypatch.setattr(X, "key_exists", lambda key: key != "craft:webster_quilts_1915" and real(key))
    book_fn, sign_fn = A.INDEX
    left = []
    book = book_fn("index", str(tmp_path), None, left)
    assert len(book.pages) == len(A.SECTIONS) and any(r["title"] == "craft:webster_quilts_1915" for r in left)
    assert book.group == "crafts" and sign_fn("index") == sign_fn("index")


def test_craft_books_moved_with_their_keys_and_words():
    """The sewing books of thin_topics.py are in the arts and crafts group and still asked for by thin:sewing and
    group:reference (word_group); the Internet Archive's sewing, art and craft topics are in the group too."""
    for e in TT.SEWING:
        assert e["group"] == "crafts" and e["word_group"] == "reference", e["name"]
        assert f"pdf:{e['name']}" in sources.expand_keys(["thin:sewing"])
        assert f"pdf:{e['name']}" in sources.expand_keys(["group:reference"])
    for topic in ("sewing", "art", "crafts"):
        assert OC.IA_TOPICS[topic][1] == "crafts", topic
    assert OC.IA_TOPICS["home"][1] == "reference" and OC.IA_TOPICS["woodworking"][1] == "reference"


def test_shared_craft_prefix_goes_to_the_module_that_has_the_key():
    """home_crafts.py and crafts_books.py both use "craft:": each key is built by the module that has it."""
    assert more_refs.module_for("craft:binns_potters_craft_1910") is CB
    assert more_refs.module_for("craft:webster_quilts_1915") is HC
    assert more_refs.module_for("craft:no_such_book") in (HC, CB)
    assert more_refs.module_for("crafts") is CB and more_refs.module_for("home-crafts") is HC
