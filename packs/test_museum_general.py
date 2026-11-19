"""A self-test of the general museum packs (packs/museum_general_packs.py), with made-up Met records only: nothing is
downloaded. It checks which objects are left for other packs (highlights, musical instruments, nudes and erotica,
not public domain), the answer from the record and its subject tags, that a record without tags is not "described",
and the wiring.

Run it from the repository's folder:   python3 -m pytest packs/test_museum_general.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import museum_general_packs as g  # noqa: E402

REPO = os.path.dirname(HERE)


def obj(**kw):
    """A made-up Met object record."""
    base = {"objectID": 1, "isPublicDomain": True, "primaryImage": "https://images.metmuseum.org/x.jpg",
            "title": "Basket of Fruit", "objectName": "Painting", "artistDisplayName": "Bartolomeo Cavarozzi",
            "objectDate": "ca. 1620", "medium": "Oil on canvas", "culture": "", "department": "European Paintings",
            "tags": [{"term": "Fruit"}, {"term": "Still Life"}], "objectURL": "https://www.metmuseum.org/art/1",
            "isHighlight": False, "geographyType": "", "city": "", "country": ""}
    base.update(kw)
    return base


def test_excluded():
    assert g.met_excluded(obj()) == ""
    assert g.met_excluded(obj(isHighlight=True)).startswith("a highlight")
    assert g.met_excluded(obj(department="Musical Instruments")).startswith("a musical instrument")
    assert g.met_excluded(obj(title="Reclining Nude")).startswith("a nude")
    assert g.met_excluded(obj(tags=[{"term": "Female Nudes"}])).startswith("a nude")
    assert g.met_excluded(obj(title="Lovers, shunga")).startswith("a nude")
    assert g.met_excluded(obj(isPublicDomain=False)).startswith("not public domain")


def test_rows():
    rows, described = g.met_rows(obj())
    assert described and rows[0]["question"] == g.MUSEUM_QUESTION
    assert rows[0]["answer"] == ("Basket of Fruit: a painting by Bartolomeo Cavarozzi, ca. 1620, in oil on canvas. "
                                 "The museum lists these subjects: fruit, still life.")
    _, described = g.met_rows(obj(tags=[{"term": "Men"}]))
    assert not described                                   # an empty tag says nothing about what it shows


def test_wiring():
    assert set(g.MUSEUM_GENERAL_PACKS) <= set(build_packs.PACKS)
    with open(os.path.join(REPO, ".github", "workflows", "packs.yml"), encoding="utf-8") as f:
        packs_yml = f.read()
    with open(os.path.join(REPO, ".github", "workflows", "pack-build.yml"), encoding="utf-8") as f:
        build_yml = f.read()
    for key, limit in g.MUSEUM_GENERAL_LIMITS.items():
        assert f'"{key}"' in packs_yml and re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M)
    import sources
    assert "met_collection" in {s.key for s in sources.SOURCES}
