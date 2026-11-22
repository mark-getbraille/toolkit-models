"""A self-test of the arts and crafts packs (packs/crafts_packs.py) and the kit's crafts collections
(training-kit/kit/crafts_sources.py), with made-up records and labels only: nothing is downloaded.

It checks that the kiln, clay, lye, wax, glass, torch, resin and blade notes follow their answers in the packs and
the kit; that the museum craft packs keep only CC0, described, English-titled objects under their own file names,
never a nude; that Open Images rows say only what the labels say; that pottery and jewellery are collections of
their own; and that every pack is wired (build_packs, COMMONS_KEYS only for Commons packs, the workflows, the kit's
sources, the crafts and art topics, picture-making only for things, the hidden imports). The shared checks of Open Images labels
and Commons categories are in packs/test_electronics.py.

Run it from the repository's folder:   python3 -m pytest packs/test_crafts.py
"""

import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import crafts_packs as c  # noqa: E402
from test_electronics import workflows  # noqa: E402


def answers(specs):
    """{category: first answer} of Commons specs."""
    return {spec[0]: spec[2][0][1] for spec in specs}


def test_notes_follow_their_answers():
    a = answers(c.CRAFTS_SPECS)
    for category in ("Kilns", "Pottery kilns", "Raku", "Fused glass", "Anagama kiln"):
        assert a[category].endswith(c.KILN_NOTE), category
    for category in ("Pottery wheels", "Potters"):
        assert a[category].endswith(c.CLAY_NOTE), category
    assert not a["Aleppo soap"].endswith(c.LYE_NOTE)                         # finished soap, no lye handled
    assert a["Candle wicks"].endswith(c.WAX_NOTE) and a["Making a stained-glass window"].endswith(c.GLASS_NOTE)
    for category in ("Glassblowing", "Lampworking", "Goldsmiths", "Jewellers"):
        assert a[category].endswith(c.TORCH_NOTE), category
    for category in ("Whittling", "Woodcarvers"):
        assert a[category].endswith(c.BLADE_NOTE), category
    assert "lye to water, never water to lye" in c.LYE_NOTE and "double boiler" in c.WAX_NOTE
    assert "silica" in c.CLAY_NOTE and "lead" in c.GLASS_NOTE
    import sources  # noqa: F401 - loaded first
    import crafts_sources as k
    assert (k.KILN_NOTE, k.CLAY_NOTE, k.LYE_NOTE, k.TORCH_NOTE, k.GLASS_NOTE, k.BLADE_NOTE) == (
        c.KILN_NOTE, c.CLAY_NOTE, c.LYE_NOTE, c.TORCH_NOTE, c.GLASS_NOTE, c.BLADE_NOTE)
    sa = {cat: ans for cat, _q, ans, _d in k.POTTERY_SA + k.JEWELLERY_SA + k.CRAFTS_SA}
    assert sa["Kilns"].endswith(k.KILN_NOTE) and not sa["Aleppo soap"].endswith(k.LYE_NOTE)


def test_museum_records(monkeypatch):
    import gaps_collection_packs as gc
    record = {"id": 12345, "title": "Storage Jar", "share_license_status": "CC0", "type": "Ceramic",
              "images": {"web": {"url": "https://x/jar.jpg"}}, "creation_date": "1700s",
              "technique": "stoneware with ash glaze",
              "digital_description": "A tall stoneware jar with a brown ash glaze running down its shoulder.",
              "creators": [{"description": "Made-up Potter (Japanese)"}], "culture": ["Japan, Edo period"],
              "url": "https://www.clevelandart.org/art/12345"}
    calls = []

    def fake_get_json(s, url, params=None):
        calls.append(params)
        if params.get("limit") == 1:
            return {"info": {"total": 3}}
        return {"data": [record, dict(record, id=2, share_license_status="Copyrighted"),
                         dict(record, id=3, title="Nude bather vase", digital_description="A nude figure.")]}
    import museum_general_packs
    monkeypatch.setattr(museum_general_packs, "get_json", fake_get_json)
    monkeypatch.setattr(c.time, "sleep", lambda s: None)
    items = c.cma_craft_items(("Ceramic",), "museumpottery", 5)
    assert [i[0] for i in items] == ["museumpottery-12345.jpg"]
    rows = items[0][2]
    assert "Storage Jar" in rows[0]["answer"] and "ash glaze" in rows[0]["answer"]
    assert "Cleveland Museum of Art, CC0" in rows[0]["credit"]
    assert all(p.get("type") == "Ceramic" for p in calls)
    assert c.renamed(("aicg-77.jpg", "u", [], True), "museumjewel")[0] == "museumjewel-77.jpg"
    assert gc.nude_or_erotic("Nude bather vase")


def test_open_images_rows():
    rows = g.oi_gap_rows({"Bead": 1, "Earring": 1, "Origami": 0}, c.CRAFTS_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What jewellery or stones are in this picture?"] == "I can see beads and an earring."
    assert said["Is there any origami in this picture?"] == "No, I can't see any origami in this picture."
    rows = g.oi_gap_rows({"Watercolor paint": 1}, c.CRAFTS_OI, random.Random(1))
    assert rows[0]["answer"] == "I can see watercolour paint. " + c.PIGMENT_NOTE
    rows = g.oi_gap_rows({"Fountain pen": 1}, c.CRAFTS_OI, random.Random(1))
    assert rows[0]["answer"] == "I can see a fountain pen."                   # no paint note on a pen


def test_wiring():
    packs_yml, build_yml, kit_yml = workflows()
    keys = set(c.CRAFTS_PACKS)
    assert keys == set(c.CRAFTS_LIMITS) and keys <= set(build_packs.PACKS)
    assert set(c.CRAFTS_COMMONS_KEYS) <= build_packs.COMMONS_KEYS
    assert not (keys - set(c.CRAFTS_COMMONS_KEYS)) & build_packs.COMMONS_KEYS
    for key, limit in c.CRAFTS_LIMITS.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import crafts_sources") == 2
    import sources
    import topics
    import crafts_sources as k
    listed = {s.key: s for s in sources.SOURCES}
    assert set(k.CRAFTS_PACK_KEYS) == keys
    for key in keys:
        assert listed[key].group == "permissive" and listed[key].prepare is sources.prepare_pack, key
    for key in ("pottery_commons_sa", "jewellery_commons_sa", "crafts_commons_sa"):
        assert listed[key].group == "share-alike", key
    assert set(c.POTTERY_KEYS) <= set(k.POTTERY_KIT_KEYS) and set(c.JEWELLERY_KEYS) <= set(k.JEWELLERY_KIT_KEYS)
    # the topics: exactly as the kit module says; every collection in "crafts" (Arts and crafts), the museum ones in
    # "art" too, and no Commons or Open Images craft collection left in "art" or "home"
    for topic_id, topic_keys in k.CRAFTS_TOPICS.items():
        assert set(topic_keys) <= set(topics.find(topic_id).keys), topic_id
    crafts = set(topics.find("crafts").keys)
    for topic in topics.TOPICS:
        held = {s.key for s in k.CRAFTS_SOURCES} & set(topic.keys)
        assert held <= set(k.CRAFTS_TOPICS.get(topic.id, ())), topic.id
    assert not {s.key for s in k.CRAFTS_SOURCES} & set(topics.find("home").keys)
    no_making = set(sources.NOT_FOR_PICTURE_MAKING)
    for s in k.CRAFTS_SOURCES:
        assert s.key in crafts, s.key
        assert (s.key in no_making) == (s.key not in k.CRAFTS_PICTURE_MAKING_OK), s.key
    assert "commons_pottery_ceramics" in no_making and "museum_ceramics" not in no_making
