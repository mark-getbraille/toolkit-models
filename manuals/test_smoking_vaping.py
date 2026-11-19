"""Self-test of the collection "Vaporizers, pipes and smoking accessories (manuals)" (manuals/smoking_vaping.py,
build_manuals.maker_entries), with MADE-UP pages only: nothing is downloaded from the internet.

It checks that:
  - the category is listed under its key smoking_vaping with its plain name;
  - a "read" maker's support page gives one entry per manual on the maker's own file host, in this category (not
    "firearms"), with its own kinds of product (vaporizer, e-rig, hookah, e-cigarette ...), never a firearm word;
  - links to other sites are never kept, nor sales papers, nor anything excluded (extraction kits, butane hash oil,
    pill presses, grow kits, steam humidifiers that share the word "vaporizer");
  - robots.txt is obeyed, and "link" makers are never fetched (their library address is listed);
  - every maker has its access decision and reason, the makers named by the owner are present, the two makers whose
    terms forbid deep links are listed by their home page only, and nothing is shared with the firearms makers;
  - the written index carries the guidance pages and the makers' access decisions.

Run it from the repository's folder:   python3 -m pytest manuals/test_smoking_vaping.py
"""

import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import smoking_vaping as S  # noqa: E402

SUPPORT = """<html><body>
<h3>Example Peak Instruction Manual</h3>
<p><a href="https://files.example-vapes.test/s/files/Peak_Digital_IM_WEB.pdf"><span>Click here to download</span></a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Volcano-Instructions.pdf">Volcano Hybrid Instructions for
Use</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Hookah.pdf">Classic Hookah Assembly Guide</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Pod.pdf">XR Pod Kit User Manual</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Grinder.pdf">4-Piece Grinder Care</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Extractor.pdf">Closed Loop Extractor Manual</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-BHO.pdf">Butane Hash Oil Guide</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Press.pdf">Pill Press TDP-5 Manual</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Grow.pdf">Grow Tent Kit Manual</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Vicks.pdf">Steam Vaporizer (Humidifier) Manual</a></p>
<p><a href="https://files.example-vapes.test/s/files/Example-Catalog.pdf">2026 Catalog</a></p>
<p><a href="https://www.manualslib.com/manual/1/Example-Peak.html">Example Peak manual (copy)</a></p>
<p><a href="https://dealer.example.test/Example-Peak.pdf">Example Peak manual at a dealer</a></p>
</body></html>"""

MAKER = dict(S._COMMON, key="example", maker="Example Vapes", type="vaporizer", access="read",
             library="https://www.example-vapes.test/support", pages=["https://www.example-vapes.test/support"],
             hosts=["files.example-vapes.test"], reason="made up")


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
        return 2345678


def setup_function():
    B._ROBOTS.clear()


def test_the_category_is_listed():
    cat = C.CATEGORIES["smoking_vaping"]
    assert cat["name"] == "Vaporizers, pipes and smoking accessories (manuals)"
    assert cat["kind"] == "manuals" and cat["makers"] is S.SMOKING_MAKERS and cat["exclude"] == S.SMOKING_EXCLUDE
    assert "firearms" in C.CATEGORIES                  # the firearms collection is untouched


def test_a_read_makers_manuals_are_listed_in_this_category_with_their_kinds():
    fetch = FakeFetch({"https://www.example-vapes.test/support": SUPPORT,
                       "https://www.example-vapes.test/robots.txt": "User-agent: *\nAllow: /\n"})
    entries, notes = B.maker_documents(fetch, MAKER, S.SMOKING_EXCLUDE)
    by_name = {e["name"]: e for e in entries}
    assert len(entries) == 5, list(by_name)
    for e in entries:
        assert e["category"] == "smoking_vaping" and e["id"].startswith("sv-example-")
        assert e["manuals"][0]["kind"] == "pdf" and e["manuals"][0]["size"] == 2345678
        assert e["type"] not in ("pistol", "rifle", "firearm", "chemical", "safe")
    kinds = {name: e["type"] for name, e in by_name.items()}
    assert kinds["Example Peak Instruction Manual"] == "e-rig"     # the heading above "Click here"
    assert kinds["Example Vapes Volcano Hybrid Instructions for Use"] == "vaporizer"
    assert kinds["Example Vapes Classic Hookah Assembly Guide"] == "hookah"
    assert kinds["Example Vapes XR Pod Kit User Manual"] == "e-cigarette"
    assert kinds["Example Vapes 4-Piece Grinder Care"] == "grinder"
    words = " ".join(by_name).lower()
    for never in ("extractor", "hash oil", "pill press", "grow tent", "humidifier", "catalog", "copy", "dealer"):
        assert never not in words, never


def test_robots_txt_is_obeyed_and_link_makers_are_never_fetched():
    fetch = FakeFetch({"https://www.example-vapes.test/support": SUPPORT,
                       "https://www.example-vapes.test/robots.txt": "User-agent: *\nDisallow: /support\n"})
    entries, notes = B.maker_documents(fetch, MAKER, S.SMOKING_EXCLUDE)
    assert entries == [] and "robots.txt does not allow" in notes[0]
    fetch = FakeFetch({})
    entries, _ = B.maker_entries(fetch, [m for m in S.SMOKING_MAKERS if m["access"] == "link"])
    assert fetch.asked == []
    for e in entries:
        assert e["category"] == "smoking_vaping" and e["id"].endswith("-library") and e["id"].startswith("sv-")
        assert e["manuals"][0]["kind"] == "library" and e["page"].startswith("https://")
        assert "instructions for use" in e["name"]


def test_every_maker_is_sound():
    keys = set()
    for m in S.SMOKING_MAKERS:
        assert m["access"] in ("read", "link", "mention") and m["reason"] and m["key"] not in keys
        assert m["category"] == "smoking_vaping" and m["prefix"] == "sv"
        keys.add(m["key"])
        if m["access"] == "read":
            assert m["pages"] and m["hosts"]
        if m["access"] in ("read", "link"):
            assert m["library"].startswith("https://")
        for site in B.NEVER_SITES:
            assert site not in str(m)
    for key in ("storz-bickel", "pax", "davinci", "arizer", "firefly", "puffco", "g-pen", "dynavap", "raw",
                "khalil-mamoon", "grav", "vaporesso", "juul"):
        assert key in keys, key
    assert not keys & {m["key"] for m in C.MAKERS}          # nothing shared with the firearms makers
    assert {m["type"] for m in S.SMOKING_MAKERS} >= {"vaporizer", "e-rig", "water pipe", "hookah", "rolling",
                                                      "grinder", "e-cigarette"}
    home_only = {m["key"]: m["library"] for m in S.SMOKING_MAKERS if m["key"] in ("davinci", "raw")}
    assert home_only == {"davinci": "https://davincivaporizer.com/", "raw": "https://rawthentic.com/"}
    forbid = [m["key"] for m in S.SMOKING_MAKERS if "crawl, or scrape" in m["reason"] or "any robot" in m["reason"]]
    assert all(S.SMOKING_MAKERS[[x["key"] for x in S.SMOKING_MAKERS].index(k)]["access"] == "link" for k in forbid)


def test_the_index_has_guidance_and_makers(tmp_path):
    entries, _ = B.maker_entries(FakeFetch({}), [m for m in S.SMOKING_MAKERS if m["access"] != "read"])
    manifest = B.write("smoking_vaping", entries, str(tmp_path))
    index = json.loads(gzip.decompress((tmp_path / manifest["file"]).read_bytes()))
    assert index["key"] == "smoking_vaping"
    assert "https://www.samhsa.gov/find-help/helplines/national-helpline" in [g["url"] for g in index["guidance"]]
    assert {m["key"] for m in index["makers"]} == {m["key"] for m in S.SMOKING_MAKERS}
    assert "not published here" in index["copyright"]


def test_file_titles_for_makers_whose_headings_sit_beside_the_wrong_files():
    assert B.file_title("https://files.test/s/files/Peak_Digital_IM_WEB_080824.pdf?v=1") == "Peak Instruction Manual"
    assert B.file_title("https://files.test/PIVOT_QSG.pdf") == "PIVOT Quick Start Guide"
    assert B.file_title("https://files.test/PuffcoPro2Instructions.pdf?71739") == "PuffcoPro2 Instructions"
    page = ('<h3>Quick Start Guide</h3><p><a href="https://files.example-vapes.test/s/Peak_Digital_IM.pdf">'
            'Download</a></p>')
    fetch = FakeFetch({"https://www.example-vapes.test/support": page,
                       "https://www.example-vapes.test/robots.txt": "User-agent: *\nAllow: /\n"})
    entries, _ = B.maker_documents(fetch, dict(MAKER, file_titles=True), S.SMOKING_EXCLUDE)
    assert [e["name"] for e in entries] == ["Example Vapes Peak Instruction Manual"]
    assert [m["key"] for m in S.SMOKING_MAKERS if m.get("file_titles")] == ["puffco"]
