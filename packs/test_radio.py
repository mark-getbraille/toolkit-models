"""A self-test of the radio communications packs (packs/radio_packs.py) and the kit's collections for them
(training-kit/kit/radio_sources.py), with made-up labels and records only: nothing is downloaded.

It checks that:
  - every radio, antenna, tower and station answer ends with the radio safety note (power lines, towers, lightning and
    grounding, RF exposure, transmit only where licensed, no encryption on amateur frequencies), the amateur things
    say a licence is needed to transmit, the mesh devices say which bands are licence-free, and the safety words are
    the same in the packs, the kit and the books;
  - the brand filters keep radios and leave out the makers' other products (Motorola phones, Uniden cordless phones);
  - Open Images rows say only what the labels say, and no label of these packs is asked by another pack;
  - no Commons category of these packs is named by another pack file (the electronics packs' coaxial cables and
    connectors included), nor twice here;
  - every pack is wired (as packs/test_preparedness.py checks), and the radio collections are in the radio topic,
    the radios also in machines and the cards also in documents.

Run it from the repository's folder:   python3 -m pytest packs/test_radio.py
"""

import glob
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(REPO, "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import gaps_oi_packs as g  # noqa: E402
import radio_packs as r  # noqa: E402
from test_preparedness import asked_elsewhere, check_wiring  # noqa: E402


def answer_of(category):
    """The first answer of a category's Commons spec."""
    return next(spec[2][0][1] for spec in r.RADIO_SPECS if spec[0] == category)


def test_safety_and_licence_notes():
    for words in ("power lines", "tower", "lightning", "Ground", "RF exposure", "licensed", "encryption", "911"):
        assert words in r.RADIO_SAFETY, words
    for spec in r.RADIOS + r.ANTENNAS_STATION + r.MESH_DATA:
        assert spec[2][0][1].endswith(r.RADIO_SAFETY), spec[0]
    for category in ("Amateur radio transceivers", "Telegraph keys", "Amateur radio repeaters",
                     "Automatic Packet Reporting System", "Digital amateur radio"):
        assert r.HAM_ONLY in answer_of(category), category
    for category in ("Meshtastic", "LoRa", "Heltec"):
        assert r.MESH_NOTE in answer_of(category), category
    assert "902 to 928 MHz" in r.MESH_NOTE and "encryption is not allowed" in r.MESH_NOTE
    assert "GMRS needs an FCC licence" in r.LICENCE_FREE
    assert "CTCSS or DCS" in answer_of("Amateur radio repeaters")
    assert "SAME code" in answer_of("NOAA Weather Radio")
    for spec in r.CARDS_CHARTS:
        assert r.RADIO_SAFETY not in spec[2][0][1]


def test_notes_match_books_and_kit():
    import sources  # noqa: F401 - loaded first: it loads radio_sources at its end
    import radio_sources as k
    sys.path.insert(2, os.path.join(REPO, "textbooks"))
    import radio_books as books
    assert r.RADIO_SAFETY == books.RADIO_SAFETY == k.RADIO_SAFETY
    assert (k.HAM_ONLY, k.MESH_NOTE) == (r.HAM_ONLY, r.MESH_NOTE)
    pack_categories = {spec[0] for spec in r.RADIO_SPECS}
    for category, _q, answer, _d in k.RADIO_SA:
        assert category in pack_categories and answer.endswith(k.RADIO_SAFETY), category


def test_brand_filters():
    must = next(spec[3] for spec in r.RADIOS if spec[0] == "Motorola radios")
    assert must.search("Motorola XTS 5000 two-way radio") and must.search("Motorola Talkabout walkie talkie")
    assert not must.search("Motorola Razr V3 mobile phone")
    uniden = next(spec[3] for spec in r.RADIOS if spec[0] == "Uniden")
    assert uniden.search("Uniden BC125AT scanner") and not uniden.search("Uniden cordless telephone base")
    morse = next(spec[3] for spec in r.CARDS_CHARTS if spec[0] == "Morse code")
    assert morse.search("International Morse code chart")


def test_open_images_rows():
    rows = g.oi_gap_rows({"Two-way radio": 1, "Mast": 0}, r.RADIO_OI, random.Random(1))
    said = {row["question"]: row["answer"] for row in rows}
    assert said["What radio equipment is in this picture?"] == f"I can see a two-way radio. {r.RADIO_SAFETY}"
    elsewhere = asked_elsewhere({"radio_packs"})
    assert not g.gap_labels(r.RADIO_OI) & elsewhere, g.gap_labels(r.RADIO_OI) & elsewhere


def test_no_commons_category_is_used_by_another_pack():
    others = ""
    for path in glob.glob(os.path.join(HERE, "*.py")):
        if os.path.basename(path) != "radio_packs.py" and not os.path.basename(path).startswith("test_"):
            with open(path, encoding="utf-8") as f:
                others += f.read()
    seen = set()
    for spec in r.RADIO_SPECS:
        assert spec[0] not in seen, spec[0]
        seen.add(spec[0])
        assert f'"{spec[0]}"' not in others, f"{spec[0]} is used by another pack"
    assert '"Coaxial connectors"' in others and "Coaxial connectors" not in seen


def test_wiring():
    import sources  # noqa: F401
    import radio_sources as k
    check_wiring("radio_packs", r.RADIO_PACKS, r.RADIO_LIMITS, r.RADIO_COMMONS_KEYS, "radio_sources",
                 k.RADIO_SOURCES, k.RADIO_PICTURE_MAKING_OK, k.RADIO_TOPICS)
    import topics
    radio = topics.find("radio")
    assert radio.title == "Radio communications" and set(k.RADIO_TOPICS["radio"]) == set(radio.keys)
    ids = [t.id for t in topics.TOPICS]
    assert ids.index("radio") == ids.index("home") + 1
