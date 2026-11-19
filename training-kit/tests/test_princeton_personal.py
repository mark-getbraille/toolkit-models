"""Tests of the Princeton University Art Museum personal-use collection (kit/princeton_personal_sources.py), with
made-up search hits only: nothing is downloaded from the internet.

They check that the open packs' rules are used (a nude drawing as museum_art_nudes, a nude photograph as
nude_photo_studies, an erotic print as erotic_art with "content": "sexual", and a child, a photograph of a girl, a
work the museum keeps off the web, or a picture not on its image server left out); that every row says "personal use
only: no rights statement"; that without the packs folder the collection stops with a plain message; and that it is
wired as a personal-use (research) collection, never for picture-making.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KIT, "kit"))

import sources  # noqa: E402,F401 - first, as the kit does (it loads the Princeton module itself)
import princeton_personal_sources as pp  # noqa: E402

IIIF = "https://media.artmuseum.princeton.edu/iiif/3/collection/"


def hit(oid, title, classification="Drawings", medium="Red chalk", caption="", nowebuse=False, image=True):
    """A made-up search hit as the museum's data API gives it."""
    return {"objectid": oid, "displaytitle": title, "classification": classification, "medium": medium,
            "displaymaker": "A. Artist", "displaydate": "1850", "caption": caption, "nowebuse": nowebuse,
            "primaryimage": [IIIF + f"x{oid}"] if image else ["https://example.org/x.jpg"]}


HITS = [hit("1", "Académie d'homme: standing male nude"),
        hit("2", "A woman posing naked in the studio", "Photographs", "Gelatin silver print"),
        hit("3", "Lovers, from an erotic album (shunga)", "Prints", "Woodblock print"),
        hit("4", "Nude girl bathing", "Paintings", "Oil on canvas"),
        hit("5", "A naked girl", "Photographs", "Albumen print"),
        hit("6", "Standing female nude", nowebuse=True),
        hit("7", "Seated female nude", image=False),
        hit("8", "Landscape with a river", "Paintings", "Oil on canvas"),
        hit("9", "Nude", "", "unknown")]          # no kind given, and its record cannot say: left out


class FakeSession:
    """Search answers from HITS."""

    def get(self, url, params=None, **_):
        """Every query finds HITS; an object's own record is not found."""
        if "/objects/" in url:
            return type("R", (), {"status_code": 404, "json": lambda self: {}})()
        return type("R", (), {"status_code": 200, "json": lambda self: {"hits": {"hits": [{"_source": h}
                                                                                         for h in HITS]}}})()


@pytest.fixture
def tools():
    """The packs' rules (packs/adult_art_packs.py in this repository)."""
    a = pp.pack_tools()
    if a is None:
        pytest.skip("the packs folder is not beside the kit")
    return a


def test_the_open_packs_rules_and_the_label(tools):
    items = pp.princeton_items(20, s=FakeSession(), a=tools, pause=0)
    names = {n for n, _, _ in items}
    assert names == {"princeton-1.jpg", "princeton-2.jpg", "princeton-3.jpg"}
    rows = {n: [r for m, _, r in items if m == n] for n in names}
    assert all(r["licence"] == pp.LABEL and pp.LABEL in r["credit"] for _, _, r in items)
    assert rows["princeton-1.jpg"][1]["question"] == "Is there nudity in this picture?"
    assert rows["princeton-2.jpg"][0]["content"] == "nudity"
    assert all(r["content"] == "sexual" for r in rows["princeton-3.jpg"])
    assert all(u.endswith(f"/full/!{pp.SIDE},{pp.SIDE}/0/default.jpg") for _, u, _ in items)


def test_without_the_packs_folder(monkeypatch):
    monkeypatch.setattr(pp, "pack_tools", lambda: None)
    with pytest.raises(RuntimeError, match="packs folder"):
        pp.princeton_items(5, s=FakeSession(), pause=0)


def test_wired_as_personal_use_never_picture_making():
    import sources
    source = next(s for s in sources.SOURCES if s.key == pp.KEY)
    assert source.group == "research" and sources.is_personal(source) and source.content == "nudity"
    assert pp.KEY in sources.NOT_FOR_PICTURE_MAKING
    assert pp.KEY not in {s.key for s in sources.chosen(with_nudity=True, with_sexual=True)}
    assert pp.KEY in {s.key for s in sources.chosen(with_nudity=True, with_research=True)}
    with open(os.path.join(os.path.dirname(KIT), ".github", "workflows", "training-kit.yml"), encoding="utf-8") as f:
        assert f.read().count("--hidden-import princeton_personal_sources") == 2


def test_general_rows(tools):
    """Any subject with a label text of eight words or more; nudes, erotica and title-only records left out."""
    base = {"objectid": "20", "displaytitle": "View of a Harbor", "classification": "Paintings", "medium": "Oil",
            "displaymaker": "B. Painter", "displaydate": "1870", "primaryimage": [IIIF + "x20"],
            "texts": [{"textpurpose": "Gallery Label",
                       "textentryhtml": "<p>Fishing boats rest in a calm harbor at dawn, nets drying on the quay.</p>"},
                      {"textpurpose": "Provenance", "textentryhtml": "Given to the museum by a long-standing donor."}]}
    name, url, rows = pp.general_rows(tools, base)
    assert rows[0]["question"] == pp.MUSEUM_QUESTION and "Fishing boats rest in a calm harbor" in rows[0]["answer"]
    assert rows[0]["licence"] == pp.LABEL
    assert "donor" not in rows[0]["answer"]                       # provenance is never a description
    assert pp.general_rows(tools, dict(base, texts=[{"textpurpose": "Gallery Label", "textentryhtml": "A harbor."}])) \
        is None
    assert pp.general_rows(tools, dict(base, texts=[{"textpurpose": "Provenance",
                                                     "textentryhtml": "Bought in Paris in 1925 from a dealer."}])) is None
    assert pp.general_rows(tools, dict(base, displaytitle="Reclining Nude")) is None
    assert pp.general_rows(tools, dict(base, displaytitle="Erotic scene")) is None
    assert pp.general_rows(tools, dict(base, displaytitle="Madonna and Child"))[2][0]["child"] is True
