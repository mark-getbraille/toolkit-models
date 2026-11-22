"""Self-test of the hardware, tools and shop equipment collections (manuals/hardware_tools.py, its categories in
categories.py, build_manuals.public_guide_entries and the "notice" of an index), with MADE-UP pages only: nothing is
downloaded from the internet.

It checks that:
  - the new categories are listed with their plain names, and power_tools, hand_tools and lawn_garden are extended
    (their own Internet Archive words kept, the makers, a notice and the guides added) without losing anything;
  - every maker has its access decision, a reason and an address; only RIKON is read; nothing is shared with the
    firearms makers (but Master Lock, under its own id) or the smoking makers; no manual-copying site is named;
  - a "read" maker's page gives entries in its own category with the maker's own type (never a firearm word such as
    "laser" or "safe"), and robots.txt is obeyed;
  - a public-domain guide is kept only with a PDF; a military manual follows the release rule (military_release.py):
    kept with or without Distribution Statement A (a truthful release line), link only and personal use with a
    restricted marking, left out with a classified one;
  - the written index carries the category's safety notice and guidance.

Run it from the repository's folder:   python3 -m pytest manuals/test_hardware_tools.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import hardware_tools as H  # noqa: E402
import smoking_vaping as S  # noqa: E402

NEW = ("door_hardware_locks", "cabinet_hardware", "fasteners_anchors", "plumbing_fittings", "electrical_devices",
       "garage_doors", "woodshop_machines", "metal_shop_welding", "automotive_shop", "trade_tools",
       "masonry_paint_drywall", "ladders_handling", "sewing_textile", "kitchen_equipment", "accessible_tools",
       "safety_ppe")


class FakeFetch:
    """Answers from a dictionary of made-up pages and Internet Archive metadata; records every address asked."""

    def __init__(self, pages, meta=None):
        self.pages, self.meta, self.asked, self.requests = pages, meta or {}, [], 0

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        if url not in self.pages:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.pages[url]

    def json(self, url, headers=None, cache=True):
        self.asked.append(url)
        ident = url.rsplit("/", 1)[-1]
        if ident not in self.meta:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.meta[ident]

    def size(self, url):
        self.asked.append("HEAD " + url)
        return 1234567


def setup_function():
    B._ROBOTS.clear()


def test_the_categories_are_listed_and_extended():
    for key in NEW:
        cat = C.CATEGORIES[key]
        assert cat["kind"] == "manuals" and cat["name"] and cat["notice"] and cat["makers"], key
        assert all(m["category"] == key for m in cat["makers"]), key
    for key in ("power_tools", "hand_tools", "lawn_garden"):
        cat = C.CATEGORIES[key]
        assert cat["makers"] and cat["notice"]
    assert {"drill", "circular saw", "impact driver", "nailer", "heat gun", "air compressor"} <= set(
        C.CATEGORIES["power_tools"]["ia"])
    assert "multimeter" in C.CATEGORIES["hand_tools"]["ia"] and "chipper" in C.CATEGORIES["lawn_garden"]["ia"]
    assert len(C.CATEGORIES["power_tools"]["ia"]) == len(set(C.CATEGORIES["power_tools"]["ia"]))
    assert "firearms" in C.CATEGORIES and "smoking_vaping" in C.CATEGORIES       # untouched
    titles = [g["title"] for g in C.CATEGORIES["power_tools"]["public_guides"]]
    assert titles == ["Hand and Power Tools (OSHA 3080, 1998)"]


def every_maker():
    return [m for key in NEW + ("power_tools", "hand_tools", "lawn_garden") for m in C.CATEGORIES[key]["makers"]]


def test_every_maker_is_sound():
    seen = set()
    for m in every_maker():
        assert m["access"] in ("read", "link") and m["reason"] and m["library"].startswith("https://"), m["key"]
        assert m["prefix"] == "hw" and m["types"] == []
        seen.add((m["category"], m["key"]))
        for site in B.NEVER_SITES:
            assert site not in str(m)
    assert [m["key"] for m in every_maker() if m["access"] == "read"] == ["rikon"]
    keys = {k for _, k in seen}
    # Master Lock makes gun locks and padlocks: listed in both, with different ids ("fa-" and "hw-").
    assert keys & {m["key"] for m in C.MAKERS} == {"master-lock"} and not keys & {m["key"] for m in S.SMOKING_MAKERS}
    for key in ("dewalt", "milwaukee", "makita", "ryobi", "bosch", "kwikset", "schlage", "simpson", "sharkbite",
                "leviton", "lutron", "liftmaster", "powermatic", "sawstop", "lincoln", "miller", "hypertherm",
                "starrett", "werner", "singer", "aph", "3m", "fluke", "klein", "wera"):
        assert key in keys, key
    # Makers whose robots.txt says ai-train=no, or whose terms forbid programs, are never read.
    for m in every_maker():
        if "ai-train=no" in m["reason"] or "terms of use (read" in m["reason"] or "refuses programs" in m["reason"]:
            assert m["access"] == "link", m["key"]


PAGE = """<html><body>
<p><a href="https://rikon.example.test/manuals/10-326-band-saw.pdf">10-326 14 in. Deluxe Bandsaw Manual</a></p>
<p><a href="https://rikon.example.test/manuals/laser-guide.pdf">Laser Guide Attachment Manual</a></p>
<p><a href="https://rikon.example.test/manuals/2026-catalog.pdf">2026 Catalog</a></p>
<p><a href="https://elsewhere.example.test/copy.pdf">A copy elsewhere</a></p>
</body></html>"""
MAKER = dict(H._COMMON, category="woodshop_machines", key="example", maker="Example Machines",
             type="woodworking machine", access="read", library="https://www.rikon.example.test/support",
             pages=["https://www.rikon.example.test/support"], hosts=["rikon.example.test"], reason="made up")


def test_a_read_makers_manuals_keep_the_makers_type():
    fetch = FakeFetch({"https://www.rikon.example.test/support": PAGE,
                       "https://www.rikon.example.test/robots.txt": "User-agent: *\nAllow: /\n",
                       "https://rikon.example.test/robots.txt": "User-agent: *\nAllow: /\n"})
    entries, notes = B.maker_documents(fetch, MAKER, None)
    assert [e["name"] for e in entries] == ["Example Machines 10-326 14 in. Deluxe Bandsaw Manual",
                                            "Example Machines Laser Guide Attachment Manual"]
    assert {e["type"] for e in entries} == {"woodworking machine"}           # never the firearm word "laser"
    assert all(e["category"] == "woodshop_machines" and e["id"].startswith("hw-example-") for e in entries)
    B._ROBOTS.clear()
    fetch = FakeFetch({"https://www.rikon.example.test/support": PAGE,
                       "https://www.rikon.example.test/robots.txt": "User-agent: *\nDisallow: /support\n"})
    entries, notes = B.maker_documents(fetch, MAKER, None)
    assert entries == [] and "robots.txt does not allow" in notes[0]


def ia_item(ident, front):
    """Made-up Internet Archive metadata and text of one item."""
    meta = {"metadata": {"identifier": ident}, "files": [{"name": f"{ident}.pdf", "source": "original", "size": 999},
                                                          {"name": f"{ident}_djvu.txt"}]}
    return meta, {f"https://archive.org/download/{ident}/{ident}_djvu.txt": front}


def test_public_guides_are_checked():
    items = {"navy_ok": "NAVEDTRA 14250 Approved for public release; distribution is unlimited.",
             "navy_b": "Distribution Statement B: authorized to US Government agencies only.",
             "army_none": "Lathe operations. Lesson 1.", "old_army": "War Department, 1941. The Machinist.",
             "osha": "Hand and Power Tools. OSHA 3080.", "navy_conf": "CONFIDENTIAL. Made-up course."}
    meta, pages = {}, {}
    for ident, front in items.items():
        m, p = ia_item(ident, front)
        meta[ident] = m
        pages.update(p)
    meta["no_pdf"] = {"metadata": {}, "files": [{"name": "x_djvu.txt"}]}
    guides = [H._guide("navy_ok", "Steelworker", "the US Navy", 1996, True),
              H._guide("navy_b", "Restricted", "the US Navy", 1996, True),
              H._guide("army_none", "Lathe", "the US Army", None, True),
              H._guide("old_army", "The Machinist", "the US Army", 1941, True),
              H._guide("osha", "Hand and Power Tools", "OSHA", 1998),
              H._guide("no_pdf", "No PDF", "OSHA", 2000),
              H._guide("navy_conf", "Classified", "the US Navy", 1960, True)]
    entries, notes = B.public_guide_entries(FakeFetch(pages, meta), guides, "metal_shop_welding")
    kept = {e["name"]: e for e in entries}
    assert set(kept) == {"Steelworker", "The Machinist", "Hand and Power Tools", "Lathe", "Restricted"}
    assert kept["Steelworker"]["manuals"][0]["release"].startswith("Distribution Statement A")
    assert "before distribution statements" in kept["The Machinist"]["manuals"][0]["release"]
    assert "print no distribution statement" in kept["Lathe"]["manuals"][0]["release"]
    assert "approved for public release" not in kept["Lathe"]["manuals"][0]["release"].lower()
    restricted = kept["Restricted"]["manuals"][0]
    assert restricted["link_only"] and restricted["personal_use"] and kept["Restricted"]["access"] == "link"
    assert "release" not in kept["Hand and Power Tools"]["manuals"][0]
    for e in entries:
        assert e["type"] == "guide" and e["category"] == "metal_shop_welding"
        assert e["manuals"][0]["rights"] == "a US government work (public domain)"
        assert e["manuals"][0]["url"].startswith("https://archive.org/download/")
    assert len(notes) == 3 and any("restricted marking" in n and "link only" in n for n in notes)
    assert any("no PDF" in n for n in notes) and any("classified" in n for n in notes)


def test_restricted_guide_with_an_open_government_copy():
    """A restricted-marked Internet Archive copy whose government address answers without a login (checked at build
    time, robots.txt allowing) is indexed openly, with a notice naming that address; when it does not answer, or
    robots.txt forbids asking, it stays link only and personal use."""
    gov = "https://www.made-up-agency.gov/library/navy-b.pdf"
    meta, pages = ia_item("navy_b", "Distribution Statement B: authorized to US Government agencies only.")

    class Fetch(FakeFetch):
        open_now = True

        def answers(self, url):
            self.asked.append("ANSWERS " + url)
            return self.open_now
    guide = dict(H._guide("navy_b", "Restricted", "the US Navy", 1996, True), gov=gov)
    fetch = Fetch(pages, {"navy_b": meta})
    entries, notes = B.public_guide_entries(fetch, [guide], "metal_shop_welding")
    manual = entries[0]["manuals"][0]
    assert not manual.get("link_only") and f"publishes it openly at {gov}" in manual["release"]
    assert "Distribution Statement B" in manual["release"] and "ANSWERS " + gov in fetch.asked
    B._ROBOTS.clear()
    fetch = Fetch(pages, {"navy_b": meta})
    fetch.open_now = False
    entries, notes = B.public_guide_entries(fetch, [guide], "metal_shop_welding")
    assert entries[0]["manuals"][0]["link_only"] and "personal use" in notes[0]
    B._ROBOTS.clear()
    pages["https://www.made-up-agency.gov/robots.txt"] = "User-agent: *\nDisallow: /"
    fetch = Fetch(pages, {"navy_b": meta})
    entries, notes = B.public_guide_entries(fetch, [guide], "metal_shop_welding")
    assert entries[0]["manuals"][0]["link_only"] and "ANSWERS " + gov not in fetch.asked


def test_military_guides_are_marked():
    for key, guide in H.GUIDES.items():
        assert guide["ia"] and guide["title"] and guide["by"]
        assert guide["military"] == (guide["by"] in ("the US Army", "the US Navy")), key


def test_the_index_has_its_notice_and_guidance(tmp_path):
    entries, _ = B.maker_entries(FakeFetch({}), [m for m in C.CATEGORIES["metal_shop_welding"]["makers"]
                                                 if m["access"] == "link"])
    manifest = B.write("metal_shop_welding", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["notice"].startswith("Read the safety section first. An arc burns the eyes")
    assert "https://www.osha.gov/welding-cutting-brazing" in [g["url"] for g in index["guidance"]]
    assert {m["key"] for m in index["makers"]} >= {"lincoln", "miller", "hobart", "esab", "hypertherm"}
    assert all(e["category"] == "metal_shop_welding" for e in entries)
