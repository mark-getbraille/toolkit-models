"""Self-test of the further blind and low-vision living books (blind_living_more.py), with MADE-UP data only:
nothing is downloaded.

It checks that the module is registered once, in the group of vision_living.py, and reaches sources.py; that every
request word is at most 256 jobs, that the theme words share no key and together make the word blind-living; that no
book of this module repeats an Internet Archive item, address or key the library already has; that every entry has a
licence the toolkit may repackage, with the share-alike BRLTTY books apart from the public-domain ones; that the old
books carry the before-1931 check, the Library of Congress books their front-page check, and the government books
their licence pages; that the BRLTTY page patterns match their own addresses (and not the contents pages); that a
made-up BRLTTY page is cut to its content; that the index (vision:index) lists the new books; and that every row of
NOT_INCLUDED says where to find the source.

Run it from the repository's folder:   python3 -m pytest textbooks/test_blind_living_more.py
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blind_living_more as M  # noqa: E402
import build_textbooks as B  # noqa: E402
import more_refs  # noqa: E402
import sources  # noqa: E402
import vision_living as V  # noqa: E402


def test_registered():
    assert M in more_refs.modules() and more_refs.MODULES.count("blind_living_more") == 1
    assert M.GROUP == V.GROUP == "vision" and sources.GROUPS["vision"] == "Reference, blind and low-vision living"
    assert set(M.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in M.NOT_INCLUDED)
    for licence in M.ALLOWED:
        assert sources.ALLOWED.get(licence) == "open", licence


def test_words():
    every = []
    for word in M.THEMES:
        keys = sources.expand_keys([word])
        assert keys == M.COLLECTION.expand_keys([word]) and 0 < len(keys) == len(set(keys)) <= 256, word
        every += keys
    assert len(every) == len(set(every)), "a key is in two theme words"
    whole = sources.expand_keys(["blind-living"])
    assert whole == every and len(whole) <= 256 and set(whole) == set(M.COLLECTION.own_keys())
    assert not set(whole) & set(sources.expand_keys(["vision-living"]))


def _other_entries():
    """Every PDF and web guide entry of the library outside this module (sources.py's tables and the other
    more_refs modules), to look for repeats."""
    out = list(sources.PDF_DOCS) + list(sources.GOV_GUIDES) + list(sources.NONPROFIT)
    for m in more_refs.modules():
        if m is not M:
            out += list(m.COLLECTION.pdfs.values()) + list(m.COLLECTION.guides.values())
    return out


def test_no_repeats():
    others = _other_entries()
    items = {e.get("archive") for e in others if e.get("archive")}
    addresses = {e.get(f) for e in others for f in ("pdf", "source") if e.get(f)}
    names = {e["name"] for e in others if e.get("group") == M.GROUP}
    mine = list(M.COLLECTION.pdfs.values()) + list(M.COLLECTION.guides.values())
    assert len({e["name"] for e in mine}) == len(mine)
    archives = [e["archive"] for e in mine if e.get("archive")]
    assert len(archives) == len(set(archives))
    for e in mine:
        assert e.get("archive") not in items, e["name"]
        assert e.get("pdf", "-") not in addresses and e.get("source", "-") not in addresses, e["name"]
        assert e["name"] not in names, e["name"]
    for word in ("keller_story_of_my_life", "best_the_blind", "braille_music_notation", "moon_light"):
        assert not any(word in e["name"] for e in mine), word       # those are already in the library


def test_licences_separated():
    for e in list(M.COLLECTION.pdfs.values()) + list(M.COLLECTION.guides.values()):
        kind = B.licence_kind(B.licence_short(e["licence"]))
        assert kind, e["name"]
        assert e["group"] == M.GROUP and e["description"] and e["notice"], e["name"]
        if e in M.SCREEN_READERS:
            assert kind == "share-alike" and e["licence"] == M.LGPL and "same licence" in e["notice"], e["name"]
        else:
            assert kind == "open", e["name"]
        if e.get("old_public_domain"):
            assert int(e["published"]) < 1931 and e.get("archive"), e["name"]
            assert "words" in e["description"] or "code" in e["description"] or "today" in e["description"], \
                e["name"]                         # every old book says what is out of date
        elif e in M.NLS_BOOKS:
            assert e["pdf_licence_text"] == M.LOC_FRONT and e["archive"], e["name"]
        else:
            assert e["licence_page"] and e["licence_text"], e["name"]
    assert sum(1 for e in M.PDFS if e.get("old_public_domain")) >= 30


def test_loc_front_check():
    """The front-page rule accepts a made-up Library of Congress title page and refuses one with a copyright line."""
    good = "INSTRUCTION MANUAL Made-up Edition Division For The Blind LIBRARY OF CONGRESS WASHINGTON 1961"
    assert re.search(M.LOC_FRONT, good)
    assert not re.search(M.LOC_FRONT, "Copyright 1984 by A Made-up Press. Library of Congress Cataloging")
    assert not re.search(M.LOC_FRONT, "A made-up book with no agency named")


def test_brltty_patterns():
    manual, guides = M.COLLECTION.guides["brltty_manual"], M.COLLECTION.guides["brltty_guides"]
    for url in (M.BRLTTY_MANUAL + "BRLTTY-3.html", M.BRLAPI_MANUAL + "BrlAPI-1.html"):
        assert re.match(manual["pages"], url), url
    assert not re.match(manual["pages"], M.BRLTTY_MANUAL + "BRLTTY.html")       # the contents page
    for url in guides["urls"] + [M.BRLTTY_DOC + "KeyBindings/brl-xx-made-up.html"]:
        assert re.match(guides["pages"], url), url
    assert not re.match(guides["pages"], M.BRLTTY_DOC + "KeyBindings/")
    assert re.search(M.BRLTTY_LICENCE_TEXT, "under the terms of The GNU Lesser General Public License as published")


def test_brltty_page_cut():
    """A made-up LinuxDoc page loses its navigation links and keeps its section."""
    page = ('<HTML><HEAD><TITLE>BRLTTY Reference Manual: Made-up Section</TITLE></HEAD><BODY>'
            '<A HREF="BRLTTY-4.html">Next</A><HR><H2>3. Made-up Section</H2><P>The made-up words.</P>'
            '<HR><A HREF="BRLTTY-4.html">Next</A></BODY></HTML>')
    entry = M.COLLECTION.guides["brltty_manual"]
    body = B.article_content(page, entry)
    assert "made-up words" in body and "Next" not in body
    assert re.search(entry["title_from"], page).group(1) == "Made-up Section"


def test_index_lists_new_books():
    listed = {what for _t, _i, entries in V.SECTIONS for kind, what, *_ in entries if kind in ("key", "word")}
    for key in ("blind:nls_braille_transcribing_manual_2000", "blind:brltty_manual", "blind:eustis_seeing_eye_1927",
                "blind:keller_midstream_1929", "blind:va_vha_directive_1174", "blind-living"):
        assert key in listed, key
    assert all(V.key_exists(k) for k in listed if ":" in k)


def test_not_included():
    for name, why in M.NOT_INCLUDED:
        assert name and "Index: http" in why, name
