"""Self-test of the wilderness and remote first aid books (wilderness_first_aid.py), with MADE-UP data only: nothing
is downloaded.

It checks that the module is registered once under its request word and its own group (at most 256 jobs); that
every web guide and PDF has a licence the toolkit may repackage, a notice ending with the wilderness note (911, the
SOS of a satellite messenger or PLB, not training, take a course), a description, a licence page and line and a page
pattern that matches its own addresses; that CDC's books are kept whole with CDC's conditions; that the Army medical
bulletins go through the release rule (military) and claim no release line themselves; that no page is one another
module already reads (the outdoor cooking Forest Service and Park Service pages, the first aid books); and that every
NOT_INCLUDED row says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_wilderness_first_aid.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import wilderness_first_aid as W  # noqa: E402
import mental_health as M  # noqa: E402


def books():
    """Every web guide and PDF entry of the module."""
    return list(W.COLLECTION.guides.values()) + list(W.COLLECTION.pdfs.values())


def test_registered():
    assert W in more_refs.modules() and more_refs.MODULES.count("wilderness_first_aid") == 1
    keys = sources.expand_keys(["wilderness-first-aid"])
    assert keys == W.COLLECTION.expand_keys(["wilderness-first-aid"]) and len(keys) == len(set(keys)) <= 256
    assert set(keys) == {f"wild:{n}" for n in list(W.COLLECTION.guides) + list(W.COLLECTION.pdfs)}
    assert sources.GROUPS["wildfirstaid"] == "Reference, wilderness first aid"
    assert set(W.LICENCE_LINES) <= set(sources.LICENCE_LINES)


def test_note_says_what_the_owner_asked():
    for words in ("call 911", "SOS", "personal locator beacon", "not training", "wilderness first aid course"):
        assert words in W.NOTE, words


def test_every_book():
    for g in books():
        short = g["licence"] if g["licence"] in sources.NO_CHANGES else B.licence_short(g["licence"])
        assert B.licence_kind(short, bool(g.get("unchanged"))) == "open", g["name"]
        assert g["notice"].endswith(W.NOTE) and g["description"] and g["group"] == W.GROUP, g["name"]
        assert g["licence_page"] and g["licence_text"], g["name"]
        if g["name"] in W.COLLECTION.guides:
            pattern = re.compile(g["pages"])
            for url in g.get("urls", []):
                assert pattern.match(url), (g["name"], url)
        else:
            assert g["military"] and g["archive"] and g["published"] and g["version"], g["name"]
            assert "approved for public release" not in g["notice"].lower(), g["name"]
            assert not g.get("distribution_a"), g["name"]           # a bulletin, not a field manual


def test_cdc_books_whole_with_conditions():
    cdc = [g for g in books() if g["publisher"] == M.CDC_PUBLISHER]
    assert {g["name"] for g in cdc} == {"cdc_niosh_outdoor_hazards", "cdc_lightning"}
    for g in cdc:
        assert g["unchanged"] and g["licence_page"] == M.CDC_TERMS and "Source: CDC" in g["notice"], g["name"]
    niosh = re.compile(W.COLLECTION.guides["cdc_niosh_outdoor_hazards"]["pages"])
    assert niosh.match("https://www.cdc.gov/niosh/outdoor-workers/about/venomous-snakes.html")
    assert not niosh.match("https://www.cdc.gov/niosh/outdoor-workers/site.html")


def test_no_repeats_of_other_modules():
    """No page here is one another module's fixed list reads, and no site book repeats another's sites."""
    others = [g for m in more_refs.modules() if m is not W
              for g in list(m.COLLECTION.guides.values()) + list(m.COLLECTION.pdfs.values())]
    their_urls = {u if isinstance(u, str) else u[0] for g in others for u in g.get("urls", [])}
    their_starts = {s for g in others for s, _d in g.get("crawl") or []}
    their_archives = {g.get("archive") for g in others} - {None}
    for g in books():
        assert not set(g.get("urls", [])) & their_urls, g["name"]
        assert not {s for s, _d in g.get("crawl") or []} & their_starts, g["name"]
        assert g.get("archive") not in their_archives, g["name"]
    fs = re.compile(W.COLLECTION.guides["usfs_backcountry_safety"]["pages"])
    for topic in ("camping", "food", "bears", "water-safety"):                  # the outdoor cooking book's pages
        assert not fs.match(f"https://www.fs.usda.gov/visit/know-before-you-go/{topic}")


def test_not_included():
    for row in W.NOT_INCLUDED:
        assert row in sources.NOT_INCLUDED and "Index: http" in row[1], row[0]
    names = " ".join(r[0] for r in W.NOT_INCLUDED)
    for words in ("Wilderness Medical Society", "NOLS", "Coast Guard", "Wikibooks"):
        assert words in names, words
