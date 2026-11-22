"""A self-test of the musical instrument care packs (packs/instrument_care_packs.py) and the kit's instrument care
collections (training-kit/kit/instrument_care_sources.py), with made-up labels only: nothing is downloaded.

It checks that pickups carry the electrical safety note and wooden soundboard parts the humidity note (the same words
in the kit), that broad categories keep only files whose words name an instrument, that Open Images rows say only
what the labels say, that no label or Commons category is asked by another pack, and the wiring.

Run it from the repository's folder:   python3 -m pytest packs/test_instrument_care.py
"""

import random

import life_skills_checks as L
import instrument_care_packs as i
import gaps_oi_packs as g


def test_notes():
    answers = {s[0]: s[2][0][1] for s in i.STRING_PARTS + i.WIND_PERCUSSION_PARTS + i.PIANO_PARTS + i.CARE}
    assert answers["Guitar pickups"].endswith(i.ELECTRIC_NOTE)
    assert answers["F-holes"].endswith(i.CARE_NOTE) and answers["Fingerboards"].endswith(i.CARE_NOTE)
    import instrument_care_sources as k
    assert (k.ELECTRIC_NOTE, k.CARE_NOTE) == (i.ELECTRIC_NOTE, i.CARE_NOTE)
    frets = next(s for s in i.STRING_PARTS if s[0] == "Frets")
    assert frets[3].search("Frets of a classical guitar") and not frets[3].search("A woman frets on a bench")


def test_open_images_rows():
    rows = g.oi_gap_rows({"Ukulele": 1, "Capo": 1, "Mandolin": 0}, i.INSTRUMENT_OI, random.Random(1))
    said = {r["question"]: r["answer"] for r in rows}
    assert said["What musical instruments are in this picture?"] == "I can see a ukulele."
    assert said["What music accessories are in this picture?"] == "I can see a capo."


def test_nothing_asked_twice():
    L.check_open_images([i.INSTRUMENT_OI], {"instrument_care_packs"})
    L.check_categories([i.STRING_PARTS, i.WIND_PERCUSSION_PARTS, i.PIANO_PARTS, i.CARE], {"instrument_care_packs"})


def test_wiring():
    import instrument_care_sources as k
    L.check_wiring(i.INSTRUMENT_CARE_PACKS, i.INSTRUMENT_CARE_LIMITS, i.INSTRUMENT_CARE_COMMONS_KEYS,
                   "instrument_care_sources", k.INSTRUMENT_CARE_SOURCES, k.INSTRUMENT_CARE_PICTURE_MAKING_OK)
    import topics
    assert set(i.INSTRUMENT_CARE_PACKS) <= set(topics.find("art").keys)
