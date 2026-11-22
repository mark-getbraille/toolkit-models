"""Self-test of the electronics, assistive technology, light construction and crafts manual collections
(manuals/electronics_manuals.py, building_manuals.py, crafts_manuals.py), with MADE-UP data only: nothing is
downloaded from the internet.

It checks that:
  - every new collection is listed in categories.py with its plain name, description, CC0 index licence and safety
    notice (the assistive one naming NLS's free repair, the VA and the state AT programmes);
  - every maker is link only, with its reason and an https address, is never fetched, and shares no key with another
    collection's makers (within each collection's own id prefix);
  - iFixit's pages are link only with their non-commercial rights; NLS's, the VA's and ACL's pages are "full" (US
    government works) and the FCC's and the makers' Braille eReader guides are link only;
  - the Internet Archive service-manual search pairs a kind of device with a kind of service paper and leaves out
    sales papers and ham transceivers; military public guides are marked military (so the release rule of
    military_release.py judges them);
  - a written index carries the collection's notice and guidance.

Run it from the repository's folder:   python3 -m pytest manuals/test_repair_build_crafts.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import building_manuals as BM  # noqa: E402
import crafts_manuals as CM  # noqa: E402
import electronics_manuals as EM  # noqa: E402

NEW = ("electronics_service", "electronics_test_equipment", "assistive_tech_repair", "home_construction",
       "pottery_kilns", "jewellery_tools", "craft_machines")


class NoFetch:
    """A fetcher that fails the test if anything is asked."""

    def text(self, url, headers=None, cache=True):
        raise AssertionError(f"a link-only maker was fetched: {url}")

    json = text

    def size(self, url):
        raise AssertionError(f"a link-only maker was fetched: {url}")


def test_categories_listed():
    for key in NEW:
        cat = C.CATEGORIES[key]
        assert cat["kind"] == "manuals" and cat["name"] and cat["description"] and "CC0" in cat["licence"], key
        assert cat["notice"], key
        assert cat.get("ia") or cat.get("ia_any") or cat.get("makers") or cat.get("documents"), key
    notice = C.CATEGORIES["assistive_tech_repair"]["notice"]
    for words in ("NLS", "1-888-657-7323", "VIST", "Assistive Technology Act", "swollen battery"):
        assert words in notice, words
    assert "silica" in C.CATEGORIES["pottery_kilns"]["notice"]
    assert "permit" in C.CATEGORIES["home_construction"]["notice"]


def test_makers_are_link_only_and_unique():
    ours = [m for key in NEW for m in C.CATEGORIES[key].get("makers", [])]
    assert ours
    for m in ours:
        assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["category"] in NEW
    ids = [(m["prefix"], m["key"]) for m in ours]
    assert len(ids) == len(set(ids))
    others = {(m.get("prefix", "fa"), m["key"]) for key, cat in C.CATEGORIES.items() if key not in NEW
              for m in cat.get("makers", [])}
    assert not set(ids) & others
    entries, notes = B.maker_entries(NoFetch(), ours)
    assert len(entries) == len(ours) and all(e["access"] == "link" for e in entries)
    at = {m["key"] for m in EM.AT_MAKERS}
    assert {"humanware", "vispero", "eschenbach", "zeiss-low-vision", "index-braille", "viewplus", "aph"} <= at


def test_documents():
    docs = {d["key"]: d for d in EM.SERVICE_DOCUMENTS + EM.AT_DOCUMENTS}
    for key, d in docs.items():
        assert d["access"] in ("full", "link") and d["reason"] and d["url"].startswith("https://"), key
        if key.startswith("ifixit-"):
            assert d["access"] == "link" and "NC-SA" in d["rights"], key
    for key in ("nls-dtbm-library-manual", "nls-dtbm-service-manual", "nls-da2-user-guide", "va-blind-rehabilitation",
                "acl-at-act"):
        assert docs[key]["access"] == "full" and "public domain" in docs[key]["rights"], key
    assert docs["fcc-ndbedp"]["access"] == "link" and docs["nls-braille-ereader"]["access"] == "link"
    entries, _ = B.document_entries(None, EM.AT_DOCUMENTS, "assistive_tech_repair")
    assert all(e["id"].startswith("doc-assistive_tech_repair-") for e in entries)
    assert all(e["manuals"][0].get("link_only") for e in entries if e["access"] == "link")


def test_service_search_and_guides():
    cat = C.CATEGORIES["electronics_service"]
    assert {"television", "radio", "amplifier", "laptop"} <= set(cat["ia_any"]["kinds"])
    assert {"service manual", "schematic"} <= set(cat["ia_any"]["documents"])
    entry = lambda t: {"name": t, "manuals": [{"title": t}]}          # noqa: E731
    assert B.ia_excluded(entry("Zenith 1975 television price list"), cat["ia_exclude"])
    assert B.ia_excluded(entry("Kenwood TS-430 transceiver service manual"), cat["ia_exclude"])
    assert not B.ia_excluded(entry("Sony KV-27 television service manual"), cat["ia_exclude"])
    for key in NEW:
        for g in C.CATEGORIES[key].get("public_guides", []):
            assert g["ia"] and g["title"] and g["by"], key
            if g["by"] in ("the US Army", "the US Navy"):
                assert g["military"], g["title"]
    assert "laminating" not in CM.CATEGORIES["craft_machines"]["ia"]           # office_supplies' word
    assert not set(BM.IA_WORDS) & {"ladder", "scaffold"}                      # ladders_handling's words


def test_written_index_has_notice(tmp_path):
    entries, _ = B.maker_entries(NoFetch(), BM.MAKERS)
    manifest = B.write("home_construction", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["notice"] == BM.NOTICE
    assert any("access-board.gov" in g["url"] for g in index["guidance"])


def test_arts_and_crafts_heading(tmp_path):
    """Arts and crafts is a heading of its own (the owner's request of 22 November 2026): the craft collections carry
    it, keys unchanged; craft_machines and heat_press_vinyl moved there from "Home manufacturing and making", whose
    3D printers, lasers, CNC, woodshop and metal shop stay; and the heading is written into the index and manifest."""
    assert CM.HEADING == "Arts and crafts"
    assert set(CM.HEADING_KEYS) == {"sewing_textile", "textile_craft_tools", "art_craft_supplies", "pottery_kilns",
                                    "jewellery_tools", "craft_machines", "heat_press_vinyl"}
    for key in CM.HEADING_KEYS:
        assert C.CATEGORIES[key]["heading"] == "Arts and crafts", key
    for key in ("printers_3d", "laser_cnc_making", "woodshop_machines", "metal_shop_welding"):
        assert C.CATEGORIES[key]["heading"] == "Home manufacturing and making", key
    assert sum(1 for c in C.CATEGORIES.values() if c.get("heading") == "Arts and crafts") == len(CM.HEADING_KEYS)
    manifest = B.write("pottery_kilns", [], str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["heading"] == manifest["heading"] == "Arts and crafts"
