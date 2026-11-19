"""Self-test of the firearms collection (categories.MAKERS, build_manuals.maker_entries), with MADE-UP pages only:
nothing is downloaded from the internet.

It checks that:
  - a "read" maker's library page gives one entry per manual on the maker's own hosts, titled from the link (or
    the heading above a "Click here to download" link, or a script's title:/subtitle:), with its type;
  - links to other sites (copying sites, dealers) are never kept, nor sales papers, nor anything excluded
    ("solvent trap" and suppressor build kits, automatic weapons such as MP5s, conversion and capacity-increase
    kits, reloading, armorer's manuals, automatic-fire parts), while a commercially made suppressor's owner's
    manual, a semi-automatic rifle's manual and a safety data sheet are kept, with their types;
  - robots.txt is obeyed: a page it disallows is not read;
  - "link" and "mention" makers are never fetched: a link maker gets its library address, a mention maker only its
    site in words;
  - Wikidata rows of excluded kinds (machine guns, suppressors) are left out;
  - the written index carries the safe-storage guidance and the makers' access decisions.

Run it from the repository's folder:   python3 -m pytest manuals/test_firearms.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402

LIBRARY = """<html><body>
<h3>EXAMPLE Owner's Manual for Model X1 pistols</h3>
<p><a href="https://files.example-maker.test/x1/EX-Instructions-for-use_X1_2025-EN-low.pdf"><span>Click here to
download</span></a></p>
<p><a href="/manuals/Example-R7-Revolver-Owners-Manual.pdf">Example R7 Revolver Owner's Manual</a></p>
<p><a href="/manuals/Example-S12-Shotgun-Manual.pdf">S12 Pump Shotgun Manual</a></p>
<p><a href="/manuals/Example-Suppressor-Manual.pdf">EX-30 Suppressor Owner's Manual</a></p>
<p><a href="/manuals/Example-Solvent-Trap.pdf">Universal Solvent Trap Kit Instructions</a></p>
<p><a href="/manuals/Example-Baffle-Kit.pdf">Suppressor Parts Kit Instructions</a></p>
<p><a href="/manuals/Example-MP5-Manual.pdf">EX MP5 Operator Manual</a></p>
<p><a href="/manuals/Example-Mag-Extension.pdf">+5 Magazine Extension Instructions</a></p>
<p><a href="/manuals/Example-7400.pdf">Model 7400 Semi-Automatic Rifle Manual</a></p>
<p><a href="/manuals/Example-Tube.pdf">Model 60 Tube Magazine Rifle Manual</a></p>
<p><a href="/manuals/SDS-Example-No9-Bore-Solvent.pdf">No. 9 Bore Solvent</a></p>
<p><a href="/manuals/Example-RDS.pdf">EX-1 Red Dot Sight Manual</a></p>
<h3>Are you over 18 years old?</h3>
<p><a href="/manuals/Ghost-X-Owners-Manual.pdf">Download</a></p>
<p><a href="/manuals/FLOW-Manual.pdf">FLOW Suppressor &rarr;</a></p>
<p><a href="/manuals/Regency.pdf">Regency Over Under</a></p>
<p><a href="/manuals/Example-Conversion-Kit.pdf">22 Conversion Kit Instructions</a></p>
<p><a href="/manuals/Example-Reloading-Press.pdf">Reloading Press Manual</a></p>
<p><a href="/manuals/Example-Armorers-Manual.pdf">X1 Armorer's Manual</a></p>
<p><a href="/manuals/Example-Warranty-Form.pdf">Warranty Form</a></p>
<p><a href="/manuals/Buyers-Guide-2026.pdf">Buyers Guide 2026</a></p>
<p><a href="https://www.manualslib.com/manual/1/Example-X1.html">Example X1 manual (copy)</a></p>
<p><a href="https://dealer.example.test/Example-X1.pdf">Example X1 manual at a dealer</a></p>
<p><a href="/support/owners-manuals/model-70-rifle.html">Model 70 Rifle</a></p>
<script>var m = [{ title: "Model 9", subtitle: "Air Rifle - Owner's Manual",
 url: "https://www.example-maker.test/uploads/9-Manual-RD1-REV-0926.pdf" }];</script>
</body></html>"""

MAKER = dict(key="example", maker="Example Arms", type="firearm", access="read",
             library="https://www.example-maker.test/manuals", pages=["https://www.example-maker.test/manuals"],
             hosts=["www.example-maker.test", "files.example-maker.test"],
             page_links=r"^https://www\.example-maker\.test/support/owners-manuals/[a-z0-9-]+\.html$",
             reason="made up")


class FakeFetch:
    """Answers from a dictionary of made-up pages; records every address asked."""

    def __init__(self, pages):
        self.pages, self.asked, self.requests = pages, [], 0

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        if url not in self.pages:
            raise RuntimeError(f"{url}: HTTP 404")
        return self.pages[url]

    def size(self, url):
        self.asked.append("HEAD " + url)
        return 123456


def setup_function():
    B._ROBOTS.clear()


def test_a_read_makers_manuals_are_listed_with_titles_and_types():
    fetch = FakeFetch({"https://www.example-maker.test/manuals": LIBRARY,
                       "https://www.example-maker.test/robots.txt": "User-agent: *\nAllow: /\n"})
    entries, notes = B.maker_documents(fetch, MAKER, C.FIREARMS_EXCLUDE)
    by_name = {e["name"]: e for e in entries}

    def find(words):
        hits = [e for name, e in by_name.items() if words in name]
        assert len(hits) == 1, (words, list(by_name))
        return hits[0]
    x1 = find("Owner's Manual for Model X1 pistols")                 # the heading above "Click here to download"
    assert x1["type"] == "pistol" and x1["manuals"][0]["kind"] == "pdf" and x1["manuals"][0]["size"] == 123456
    assert x1["model"] == "Model X1 pistols" and x1["brand"] == "Example Arms"
    assert find("R7 Revolver")["type"] == "revolver"
    assert find("S12 Pump Shotgun")["name"] == "Example Arms S12 Pump Shotgun Manual"    # the maker's name added
    assert find("S12 Pump Shotgun")["type"] == "shotgun"
    assert find("Model 9 Air Rifle - Owner's Manual")["type"] == "airgun"                # a script's title
    page = find("Model 70 Rifle")
    assert page["manuals"][0]["kind"] == "page" and page["type"] == "rifle"
    assert page["manuals"][0]["url"].endswith("/support/owners-manuals/model-70-rifle.html")
    assert find("EX-30 Suppressor")["type"] == "suppressor"         # a commercially made suppressor's manual
    assert find("Model 7400 Semi-Automatic Rifle")["type"] == "rifle"  # "semi-automatic" is not "automatic"
    assert find("Model 60 Tube Magazine Rifle")["type"] == "rifle"     # a gun maker's rifle, not a magazine
    sds = find("No. 9 Bore Solvent")
    assert sds["type"] == "chemical" and sds["manuals"][0]["document"] == "safety data sheet"
    assert find("Red Dot Sight")["type"] == "optic" and find("Red Dot Sight")["manuals"][0]["document"] == "manual"
    assert find("Ghost X Owners Manual")["model"] == "Ghost X"    # an age question is not a title
    assert find("FLOW Suppressor")["name"] == "Example Arms FLOW Suppressor"     # no arrow
    assert find("Regency Over Under")["type"] == "shotgun"
    names = " ".join(by_name).lower()
    assert "years old" not in names
    for never in ("solvent trap", "parts kit", "mp5", "extension", "conversion", "reloading", "armorer", "warranty",
                  "buyers", "copy", "dealer"):
        assert never not in names, never
    for e in entries:
        assert e["fcc_ids"] == [] and e["ic_ids"] == [] and "belongs to its maker" in e["manuals"][0]["rights"]
    assert not any(u.startswith("HEAD") and "dealer" in u for u in fetch.asked)


def test_robots_txt_is_obeyed():
    fetch = FakeFetch({"https://www.example-maker.test/manuals": LIBRARY,
                       "https://www.example-maker.test/robots.txt": "User-agent: *\nDisallow: /manuals\n"})
    entries, notes = B.maker_documents(fetch, MAKER, C.FIREARMS_EXCLUDE)
    assert entries == [] and "robots.txt does not allow" in notes[0]
    assert "https://www.example-maker.test/manuals" not in fetch.asked
    B._ROBOTS.clear()
    unreadable = FakeFetch({"https://www.example-maker.test/manuals": LIBRARY})
    unreadable.text = lambda url, headers=None, cache=True: (_ for _ in ()).throw(RuntimeError(f"{url}: HTTP 403"))
    assert B.robots_allows(unreadable, "https://www.example-maker.test/manuals") is False


def test_link_and_mention_makers_are_never_fetched():
    link = dict(key="lk", maker="Linked Arms", type="safe", access="link", library="https://linked.test/manuals",
                reason="terms forbid robots")
    mention = dict(key="mn", maker="Named Arms", type="firearm", access="mention", site="named.test",
                   reason="terms forbid links")
    fetch = FakeFetch({})
    entries, notes = B.maker_entries(fetch, [link, mention], C.FIREARMS_EXCLUDE)
    assert fetch.asked == []
    lk, mn = entries
    assert lk["page"] == "https://linked.test/manuals" and lk["manuals"][0]["kind"] == "library"
    assert lk["type"] == "safe" and lk["access"] == "link" and lk["access_reason"] == "terms forbid robots"
    assert mn["page"] == "" and mn["manuals"] == [] and mn["site"] == "named.test"


def test_every_maker_is_sound():
    keys = set()
    for m in C.MAKERS:
        assert m["access"] in ("read", "link", "mention") and m["reason"] and m["key"] not in keys
        keys.add(m["key"])
        if m["access"] == "read":
            assert m["pages"] and m["hosts"]
        if m["access"] in ("read", "link"):
            assert m["library"].startswith("https://")
        for site in B.NEVER_SITES:
            assert site not in str(m)
    assert {m["type"] for m in C.MAKERS} >= {"airgun", "safe", "lock", "holster", "magazine", "loader", "cleaning",
                                              "chemical", "optic", "laser", "light", "mount", "suppressor", "rifle",
                                              "shotgun"}
    assert C.CATEGORIES["firearms"]["name"] == "Firearms (owner's manuals)"


def test_wikidata_excluded_kinds_are_left_out():
    rows = [{"item": "http://www.wikidata.org/entity/Q1", "itemLabel": "Example P1", "kindLabel": "pistol",
             "url": "https://maker.test/p1.pdf"},
            {"item": "http://www.wikidata.org/entity/Q2", "itemLabel": "Example M2", "kindLabel": "machine gun",
             "url": "https://maker.test/m2.pdf"},
            {"item": "http://www.wikidata.org/entity/Q3", "itemLabel": "Example S3 solvent trap kit",
             "kindLabel": "rifle accessory", "url": "https://maker.test/s3.pdf"},
            {"item": "http://www.wikidata.org/entity/Q5", "itemLabel": "Example U5", "kindLabel": "assault rifle",
             "url": "https://maker.test/u5.pdf"},
            {"item": "http://www.wikidata.org/entity/Q6", "itemLabel": "Example B6", "kindLabel": "bolt-action rifle",
             "url": "https://maker.test/b6.pdf"},
            {"item": "http://www.wikidata.org/entity/Q4", "itemLabel": "Example A4", "kindLabel": "submachine gun",
             "url": "https://maker.test/a4.pdf"}]
    assert [e["name"] for e in B.wikidata_entries(rows, "firearms")] == ["Example P1", "Example B6"]


def test_the_index_has_guidance_and_makers(tmp_path):
    entries, _ = B.maker_entries(FakeFetch({}), [m for m in C.MAKERS if m["access"] != "read"])
    manifest = B.write("firearms", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["guidance"][0]["url"] == "https://projectchildsafe.org/securing-your-firearm/"
    assert {m["key"] for m in index["makers"]} == {m["key"] for m in C.MAKERS}
    assert "not published here" in index["copyright"]


def test_the_makers_cover_long_guns_accessories_cleaning_optics_and_suppressors():
    keys = {m["key"] for m in C.MAKERS}
    for key in ("remington", "mossberg", "savage", "winchester", "browning", "henry", "marlin", "ruger", "benelli",
                "beretta", "stoeger", "cz", "tikka", "weatherby", "bergara", "franchi", "ithaca", "rossi",
                "springfield", "sig", "smith-wesson",                                   # long guns
                "hoppes", "m-pro-7", "break-free", "ballistol", "otis", "real-avid", "lucas", "rem-oil",  # cleaning
                "safariland", "magpul", "master-lock", "gunvault",                       # holsters, magazines, locks
                "vortex", "leupold", "trijicon", "aimpoint", "eotech", "holosun", "burris", "bushnell", "nikon",
                "primary-arms", "surefire", "streamlight", "crimson-trace", "viridian", "harris",   # mounted
                "silencerco", "dead-air", "rugged", "thunder-beast", "banish", "huxwrx", "q", "griffin", "ase-utra",
                "jaki", "hausken", "a-tec"):                                             # commercial suppressors
        assert key in keys, key
    hoppes = next(m for m in C.MAKERS if m["key"] == "hoppes")
    entry = B.library_entry(hoppes)
    assert entry["name"] == "Hoppe's safety data sheets (the maker's own library)"
    assert entry["manuals"][0]["page"] == "https://www.primos.com/pages/hoppes-sds" and hoppes["access"] == "link"


def test_index_exclusions():
    import re
    rule = re.compile(C.FIREARMS_EXCLUDE, re.I)
    for never in ("Universal Solvent Trap Kit", "9mm solvent trap cups", "Suppressor build kit", "Baffle stack",
                  "Fuel filter adapter", "Drop-in auto sear", "Lightning link", "Forced reset trigger kit",
                  "Binary trigger group", "Bump stock", "80% lower jig", "Polymer 80% frame", "HK MP5",
                  "Uzi submachine gun", "M249 machine gun", "Short-barreled rifle", "Glock +5 magazine extension",
                  "Capacity increase kit", "Select-fire conversion"):
        assert rule.search(never), never
    for kept in ("Model 870 Pump-Action Shotgun", "Model 7400 Semi-Automatic Rifle", "Ghost-M Owner's Manual",
                 "Suppressor Cleaning Concentrate (SDS)", "Hoppe's No. 9 SDS", "BoreSnake", "Cable lock",
                 "Speed loader", "Riflescope manual", "Bipod"):
        assert not rule.search(kept), kept
