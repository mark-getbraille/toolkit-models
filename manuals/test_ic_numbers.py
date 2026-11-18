"""A self-test of the Canadian certification numbers (IC numbers) of manuals/build_manuals.py, with made-up Internet
Archive answers only: nothing is downloaded from the internet.

It checks that:
  - an IC number printed in an item's title or description ("IC: 4492A-XYZ123", "IC 4492A-XYZ123", "ISED: ...") is
    kept in the entry's "ic_ids", without "IC:", each once;
  - words that only look like one ("IC 555-TIMER", a chip; "CAN ICES-3(B)", the interference statement) are not;
  - every other source writes an empty "ic_ids" (EnerGuide prints no IC numbers);
  - a device record that gets an Internet Archive item's manuals gets its IC numbers too.
The rule is the toolkit's (app/toolkit/manuals/ised.py in mark-getbraille/video-transcriber), which reads "ic_ids".

Run it from the repository's folder:   python3 -m pytest manuals/test_ic_numbers.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402


def test_ic_numbers_in_text():
    assert B.ic_numbers("Example TC-100 talking clock FCC ID: 2AZZZ-TALK100 IC: 4492A-TALK100") == ["4492A-TALK100"]
    assert B.ic_numbers("IC 4492A-XYZ123; ISED: 10805A-WB1; ic: 4492a-xyz123") == ["4492A-XYZ123", "10805A-WB1"]
    assert B.ic_numbers("IC ID 1234-AB12") == ["1234-AB12"]
    for text in ("IC 555-TIMER chip", "CAN ICES-3(B)/NMB-3(B)", "IC: 123456A-X", "IC: 4492A-ABCDEFGHIJKL",
                 "IC: 4492A-XYZ-12", "MUSIC: 1234A-X1", "4492A-XYZ123", ""):
        assert B.ic_numbers(text) == [], text


def test_an_archive_item_keeps_the_ic_numbers_it_prints():
    doc = {"identifier": "example-tc100-guide", "title": "Example TC-100 Talking Clock User Guide",
           "description": "<p>Scanned guide. Label: FCC ID: 2AZZZ-TALK100 &amp; IC: 4492A-TALK100.</p>",
           "collection": ["manuals"], "item_size": 1000}
    entry = B.ia_entry(doc)
    assert entry["ic_ids"] == ["4492A-TALK100"] and entry["fcc_ids"] == []
    assert B.ia_entry({"identifier": "x", "title": "Example TC-200 guide"})["ic_ids"] == []
    assert B.ia_entry({"identifier": "y", "title": "Radio IC: 4492A-MR7", "description": ["a", "ISED 4492A-MR8"]})[
        "ic_ids"] == ["4492A-MR7", "4492A-MR8"]


def test_other_sources_write_an_empty_list_and_device_records_get_the_items_numbers():
    model = {"id": "energuide-1", "brand": "Example", "model": "TC-100", "name": "Example TC-100 (clock)",
             "barcodes": [], "fcc_ids": [], "ic_ids": [], "manuals": [], "market": "Canada"}
    item = B.ia_entry({"identifier": "example-tc100", "title": "Example TC-100 manual IC: 4492A-TALK100"})
    B.attach_manuals([model], [item])
    assert model["ic_ids"] == ["4492A-TALK100"] and model["manuals"] == item["manuals"]
    B.attach_manuals([model], [item])                       # twice: still once
    assert model["ic_ids"] == ["4492A-TALK100"]
    source = open(B.__file__, encoding="utf-8").read()
    assert source.count('"fcc_ids": []') == source.count('"ic_ids": ')      # every entry kind has the field
