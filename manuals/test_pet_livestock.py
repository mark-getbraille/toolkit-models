"""Self-test of the collection "Pet and livestock supplies (manuals)" (manuals/pet_livestock_supplies.py), with
MADE-UP pages only: nothing is downloaded from the internet.

It checks that:
  - the category is listed under its key pet_livestock_supplies, with its Internet Archive words, makers, exclusions
    and guidance;
  - a made-up "read" maker gives entries in this category with their kinds (incubator, aquarium, clipper ...), and
    household pest control (rodent traps, insecticides, termite bait) is never put in it;
  - "link" makers are never fetched (their own page is listed), and every maker has its access decision and reason;
  - the makers the owner named are present, nothing is shared with the other collections' makers, and the category
    names stay pet- and livestock-specific;
  - no animal drug label source is linked (another collection's).

Run it from the repository's folder:   python3 -m pytest manuals/test_pet_livestock.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import pet_livestock_supplies as P  # noqa: E402
import smoking_vaping as S  # noqa: E402

SUPPORT = """<html><body>
<p><a href="https://files.example-pets.test/manuals/Advance-60-Incubator-Instructions.pdf">Advance 60 Incubator
Instructions</a></p>
<p><a href="https://files.example-pets.test/manuals/Canister-Filter-307.pdf">Canister Filter 307 Manual</a></p>
<p><a href="https://files.example-pets.test/manuals/Pro-Clipper.pdf">Pro Animal Clipper User Guide</a></p>
<p><a href="https://files.example-pets.test/manuals/Rat-Trap.pdf">Rodent Trap Setup Guide</a></p>
<p><a href="https://files.example-pets.test/manuals/Termite-Bait.pdf">Termite Bait Station Instructions</a></p>
<p><a href="https://files.example-pets.test/manuals/Catalog.pdf">2026 Catalog</a></p>
</body></html>"""
MAKER = dict(P._COMMON, key="example", maker="Example Pets", type="feeder", access="read",
             library="https://www.example-pets.test/support", pages=["https://www.example-pets.test/support"],
             hosts=["files.example-pets.test"], reason="made up")


class FakeFetch:
    """Answers from a dictionary of made-up pages; records every address asked."""

    def __init__(self, pages):
        self.pages, self.asked = pages, []

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        if url not in self.pages:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.pages[url]

    def size(self, url):
        self.asked.append("HEAD " + url)
        return 1234567


def setup_function():
    B._ROBOTS.clear()


def test_the_category_is_listed():
    cat = C.CATEGORIES["pet_livestock_supplies"]
    assert cat["name"] == "Pet and livestock supplies (manuals)"
    assert cat["kind"] == "manuals" and cat["makers"] is P.PET_MAKERS and cat["exclude"] == P.PET_EXCLUDE
    assert "egg incubator" in cat["ia"] and "aquarium filter" in cat["ia"]
    assert "smoking_vaping" in C.CATEGORIES and "firearms" in C.CATEGORIES


def test_a_read_makers_manuals_and_exclusions():
    fetch = FakeFetch({"https://www.example-pets.test/support": SUPPORT,
                       "https://www.example-pets.test/robots.txt": "User-agent: *\nAllow: /\n"})
    entries, _ = B.maker_documents(fetch, MAKER, P.PET_EXCLUDE)
    kinds = {e["name"]: e["type"] for e in entries}
    assert all(e["category"] == "pet_livestock_supplies" and e["id"].startswith("pl-example-") for e in entries)
    assert len(entries) == 3, kinds
    assert set(kinds.values()) == {"egg incubator", "aquarium equipment", "clipper"}
    words = " ".join(kinds).lower()
    for never in ("rodent", "termite", "catalog"):
        assert never not in words


def test_link_makers_are_never_fetched_and_every_maker_is_sound(tmp_path):
    fetch = FakeFetch({})
    entries, _ = B.maker_entries(fetch, P.PET_MAKERS)
    assert fetch.asked == []
    assert all(e["id"].startswith("pl-") and e["page"].startswith("https://") for e in entries)
    keys = [m["key"] for m in P.PET_MAKERS]
    assert len(keys) == len(set(keys))
    for m in P.PET_MAKERS:
        assert m["access"] == "link" and m["reason"].startswith("robots.txt read") and m["library"].startswith("https://")
    for key in ("petmate", "midwest", "tetra", "fluval", "aqueon", "zoo-med", "oster", "andis", "wahl", "brinsea",
                "little-giant", "tarter", "weaver-leather", "petsafe", "elanco"):
        assert key in keys, key
    assert not set(keys) & ({m["key"] for m in C.MAKERS} | {m["key"] for m in S.SMOKING_MAKERS})
    manifest = B.write("pet_livestock_supplies", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    urls = [g["url"] for g in index["guidance"]]
    assert "https://ordspub.epa.gov/ords/pesticides/f?p=PPLS:1" in urls
    assert not any("dailymed" in u or "animaldrugsatfda" in u for u in urls)
