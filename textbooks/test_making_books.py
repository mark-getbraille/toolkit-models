"""Self-test of the home manufacturing and making books (making_books.py), with MADE-UP data only: nothing is
downloaded.

It checks that the module is registered once under its request word "making" (at most 256 jobs) in its own group
"Reference, home manufacturing and making" and reaches sources.py; that every book has a licence the toolkit may
repackage (the GPL and GFDL documentation as share-alike), a notice with the safety words (laser beam, eye
protection, PVC and vinyl, resin, spinning machines), a description, a licence page and line, and a page pattern that
matches its own addresses; that the military manuals follow the release rule and the old books the 1931 rule; that the
index's keys are the library's and its sections cover what the owner asked (OpenSCAD for blind makers first among the
design parts, tactile models linked to the vision books, the makers as links); that the sites that refuse AI readers
(RepRap, Marlin) are never read; and that every row of NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_making_books.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import practical_index as X  # noqa: E402
import sources  # noqa: E402
import making_books as M  # noqa: E402


def test_registered_in_its_own_group():
    assert M in more_refs.modules() and "making_books" in more_refs.MODULES
    keys = sources.expand_keys(["making"])
    assert keys == M.COLLECTION.expand_keys(["making"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {"make:index"} | {f"make:{n}" for n in list(M.COLLECTION.guides) + list(M.COLLECTION.pdfs)}
    assert sources.GROUPS[M.GROUP] == "Reference, home manufacturing and making"
    assert set(M.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert sources.ALLOWED.get("GPL-3.0") == "share-alike" and sources.ALLOWED.get("GFDL") == "share-alike"
    assert more_refs.module_for("make:klipper_docs") is M and more_refs.module_for("making") is M


def test_safety_notice_says_what_the_owner_asked():
    for words in ("never look into a laser beam", "eye protection rated for the laser's wavelength", "PVC or vinyl",
                  "chlorine gas", "nitrile gloves", "no gloves, loose sleeves, jewellery", "fire extinguisher",
                  "Molten metal"):
        assert words in M.MAKING_SAFETY, words


def test_every_book():
    for g in list(M.COLLECTION.guides.values()) + list(M.COLLECTION.pdfs.values()):
        assert g["group"] == M.GROUP, g["name"]
        short = B.licence_short(g["licence"])
        assert B.licence_kind(short), g["name"]
        assert g["notice"] and g["description"], g["name"]
        assert M.MAKING_SAFETY in g["notice"], g["name"]
        if g["name"] in M.COLLECTION.guides:
            assert g["licence_page"] and g["licence_text"], g["name"]
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
            assert pattern.match(g["source"]) or g["source"].endswith("/index.html") or \
                "wikibooks" in g["source"], g["name"]
        elif g.get("old_public_domain"):
            assert g["archive"] and int(g["published"]) < 1931 and "out of date" in g["description"], g["name"]
        elif g.get("archive"):
            assert g.get("distribution_a") or g.get("military"), g["name"]
            assert g["work"].startswith("a work of the US "), g["name"]
        else:
            assert g["pdf"].startswith("https://nvlpubs.nist.gov/") and g["licence"] == sources.US_GOV, g["name"]
    # the share-alike documentation says so in its notice
    for name in ("klipper_docs", "linuxcnc_docs"):
        g = M.COLLECTION.guides[name]
        assert B.licence_kind(B.licence_short(g["licence"])) == "share-alike" and "share-alike" in g["notice"], name
    assert B.licence_kind(B.licence_short(M.COLLECTION.guides["freecad_manual"]["licence"])) == "open"


def test_page_patterns():
    klipper = re.compile(M.COLLECTION.guides["klipper_docs"]["pages"])
    assert klipper.match("https://www.klipper3d.org/Bed_Level.html")
    assert not klipper.match("https://www.klipper3d.org/img/printer.png")
    freecad = re.compile(M.COLLECTION.guides["freecad_manual"]["pages"])
    assert freecad.match("https://wiki.freecad.org/Manual:Preparing_models_for_3D_printing")
    assert not freecad.match("https://wiki.freecad.org/Manual:Introduction/fr")
    linuxcnc = re.compile(M.COLLECTION.guides["linuxcnc_docs"]["pages"])
    assert linuxcnc.match("https://linuxcnc.org/docs/stable/html/gcode/g-code.html")
    assert not linuxcnc.match("https://linuxcnc.org/docs/stable/html/man/man1/halcmd.1.html")
    fda = re.compile(M.COLLECTION.guides["fda_laser_safety"]["pages"])
    assert all(fda.match(u) for u in M.FDA_PAGES)


def test_sites_that_refuse_ai_readers_are_not_read():
    addresses = " ".join(str(g.get("source", "")) + str(g.get("pdf", "")) + " ".join(g.get("urls", []))
                         for g in list(M.COLLECTION.guides.values()) + list(M.COLLECTION.pdfs.values()))
    for site in ("reprap.org", "marlinfw.org", "help.prusa3d.com", "osha.gov", "github.com/gnea", "cricut.com",
                 "lightburnsoftware.com"):
        assert site not in addresses, site


def test_index():
    sections = dict((title, entries) for title, _intro, entries in M.SECTIONS)
    titles = list(sections)
    assert titles.index("Accessible 3D design for blind makers") < titles.index("Cutting machines and heat presses")
    blind = sections["Accessible 3D design for blind makers"]
    assert {e[1] for e in blind} >= {"make:wikibooks_openscad_tutorial", "make:wikibooks_openscad_user_manual"}
    assert "screen reader" in next(intro for t, intro, _e in M.SECTIONS if t == "Accessible 3D design for blind "
                                                                                    "makers")
    tactile = sections["Tactile graphics and 3D-printed tactile models"]
    assert ("word", "vision-living") in [(e[0], e[1]) for e in tactile]
    for entries in sections.values():
        for kind, what, *_rest in entries:
            if kind == "key" and what.startswith("make:"):
                assert what in M.COLLECTION.own_keys(), what
            if kind == "link":
                assert _rest[0].startswith("https://") and _rest[1], what
    links = " ".join(e[1] for entries in sections.values() for e in entries if e[0] == "link")
    for maker in ("Prusa", "Cricut", "Silhouette", "LightBurn", "Tinkercad", "Marlin", "RepRap", "GRBL",
                  "Glowforge", "Bambu", "Creality", "Elegoo", "Sherline", "Shapeoko"):
        assert maker in links, maker


def test_index_book_lists_only_keys_the_library_has(monkeypatch, tmp_path):
    """The index book (made-up check of key_exists): a key the library lacks is left out and said."""
    real = X.key_exists
    monkeypatch.setattr(X, "key_exists", lambda key: key != "make:klipper_docs" and real(key))
    book_fn, sign_fn = M.INDEX
    left = []
    book = book_fn("index", str(tmp_path), None, left)
    assert book.pages and any(r["title"] == "make:klipper_docs" for r in left)
    assert sign_fn("index") == sign_fn("index")


def test_not_included():
    for row in M.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in M.NOT_INCLUDED)
    for words in ("RepRap", "Marlin", "Prusa", "GRBL", "Inkscape", "LaserGRBL", "OSHA", "Cricut", "LightBurn"):
        assert words in names, words
