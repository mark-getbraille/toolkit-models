"""A self-test of the Commons disasters pack's reading plan (packs/graphic_packs.py), with a made-up Commons answer
only: nothing is downloaded. It checks that the pack no longer walks the whole of "Images from FEMA" or "Floods",
reads FEMA's own disaster categories one by one, stops each listing at DISASTER_MOST_LISTED files, and passes its
cap and pause to build_commons.

Run it from the repository's folder:   python3 -m pytest packs/test_graphic_disasters.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import graphic_packs as g  # noqa: E402


def test_small_categories_only():
    cats = g.COMMONS_DISASTERS
    assert "Images from FEMA" not in cats and cats["Floods"] is False
    fema = [c for c in cats if c.startswith("Images from FEMA, category ")]
    assert len(fema) >= 10 and all(not cats[c] for c in fema if not c.endswith("Earthquake"))
    assert not any(word in c for c in cats for word in ("Ceremony", "Officials", "Congress", "Press"))


def test_capped_listing(monkeypatch):
    import food_packs
    asked = []

    def fake_get(s, params):
        """A made-up category of 2,000 files, 500 to an answer."""
        asked.append(dict(params))
        start = int(params.get("cmcontinue", 0))
        got = [{"title": f"File:{n}.jpg"} for n in range(start, min(start + params["cmlimit"], 2000))]
        out = {"query": {"categorymembers": got}}
        if start + params["cmlimit"] < 2000:
            out["continue"] = {"cmcontinue": str(start + params["cmlimit"])}
        return out
    monkeypatch.setattr(food_packs, "commons_get", fake_get)
    titles = g.capped_members(None, "Images from FEMA, category Flooding", "file", 600)
    assert len(titles) == 600 and len(asked) == 2 and titles[0] == "File:0.jpg"


def test_disasters_use_the_cap_and_pause(monkeypatch):
    seen = {}
    monkeypatch.setattr(g, "build_commons", lambda key, cats, limit, **kw: seen.update(kw, key=key) or [])
    g.build_commons_disasters(10)
    assert seen == {"key": "commons_disasters", "most": g.DISASTER_MOST_LISTED, "pause": g.DISASTER_PAUSE}
