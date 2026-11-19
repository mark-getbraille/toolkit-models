"""Tests of the state digital library personal-use collection (kit/state_collections_personal_sources.py), with
made-up records only: nothing is downloaded from the internet.

They check that the open packs' readers and rules are used (an OAI record with research-only rights is taken with
the "research and private study" label; an open one, a closed one, a portrait and an Indigenous record are not; a
record whose words do not describe the picture is not), that every row and credit carries its personal-use label,
that without the packs folder the collection stops with a plain message, that it is wired as a personal-use
(research) collection, never for picture-making, and that the left-out list names the museums with their reasons.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KIT, "kit"))

import sources  # noqa: E402,F401 - first, as the kit does (it loads the module itself)
import state_collections_personal_sources as sp  # noqa: E402

RESEARCH = "This item has been made available for use in research, teaching, and private study."
NOC = "http://rightsstatements.org/vocab/NoC-US/1.0/"


def record(n, title, description, rights, subject="Streets--North Carolina"):
    """A made-up OAI-PMH record as the packs' reader gives it."""
    return {"id": f"oai:x/{n}", "deleted": False, "title": [title], "description": [description],
            "identifier": [f"https://lib.example.edu/{n}"], "relation": [f"https://lib.example.edu/{n}.jpg"],
            "type": ["StillImage"], "format": ["postcards"], "rights": [rights] if rights else [],
            "subject": [subject], "coverage": ["Greenville (N.C.)"], "date": ["1910"], "publisher": [],
            "contributor": [], "creator": [], "source": []}


RECORDS = [record(1, "Main Street, Greenville", "Postcard of a street scene with storefronts, wagons and people on "
                  "the sidewalk.", RESEARCH),
           record(2, "Depot", "Postcard of the railroad depot with a train at the platform and a baggage cart.", NOC),
           record(3, "Courthouse", "Postcard of the courthouse with its dome and the lawn in front of it.",
                  "Copyright 1925 Example Company, all rights reserved"),
           record(4, "Portrait of John Smith", "Postcard portrait of John Smith in his Sunday clothes and hat.",
                  RESEARCH),
           record(5, "Cherokee village", "Postcard of houses in a village in the mountains with smoke rising.",
                  RESEARCH),
           record(6, "Bridge", "Bridge.", RESEARCH),
           record(7, "Mill", "Postcard of the cotton mill by the river, with its tall chimney and the dam.", "")]


def tools():
    """The pack tools, or a skip when the packs folder is not beside the kit."""
    p = sp.pack_tools()
    if p is None:
        pytest.skip("the packs folder is not beside the kit")
    return p


def test_oai_items_use_the_open_packs_rules(monkeypatch):
    """Research-only and no-statement records are taken with their labels; the others are not."""
    p = tools()
    monkeypatch.setattr(p, "oai_records", lambda s, base, set_spec="", most=0, robots=None, **k: RECORDS)
    monkeypatch.setattr(p.RobotsGuard, "allowed", lambda self, url: ("", 0))
    items = sp.oai_items(p, 20, s=object())
    names = [n for n, _, _ in items]
    assert names == ["ecu-oai_x_1.jpg", "ecu-oai_x_7.jpg"]
    rows = items[0][2]
    assert rows[0]["licence"] == sp.LABELS["research"] and sp.LABELS["research"] in rows[0]["credit"]
    assert rows[0]["answer"].startswith("Main Street, Greenville. Postcard of a street scene")
    assert items[1][2][0]["licence"] == sp.LABELS["none"]


def test_without_the_packs_folder(monkeypatch):
    """Without the packs, the collection stops with a plain message."""
    monkeypatch.setattr(sp, "pack_tools", lambda: None)
    with pytest.raises(RuntimeError, match="packs folder"):
        sp.state_items(5)


def test_wiring_and_left_out_list():
    """A personal-use research collection, never for picture-making; the museums left out with reasons."""
    keys = {s.key: s for s in sources.SOURCES}
    source = keys[sp.KEY]
    assert source.group == "research" and sources.is_personal(source)
    assert sp.KEY in sources.NOT_FOR_PICTURE_MAKING
    assert not sp.STATE_COLLECTIONS_PICTURE_MAKING_OK
    for museum in ("Indianapolis Museum of Art at Newfields", "Denver Art Museum", "Dallas Museum of Art",
                   "Saint Louis Art Museum", "Hammer Museum (UCLA)"):
        assert sp.STATE_COLLECTIONS_NOT_INCLUDED[museum]
