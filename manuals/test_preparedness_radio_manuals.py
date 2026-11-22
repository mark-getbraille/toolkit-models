"""Self-test of the emergency preparedness and radio communications manual collections (manuals/preparedness_manuals.py,
manuals/radio_manuals.py and their lines in categories.py), with MADE-UP Internet Archive answers only: nothing is
downloaded.

It checks that each category is listed under its key with a plain name, a kind, a licence, a notice said first and
Internet Archive words; that the radio categories have their own heading ("Radio communications:") and the
preparedness ones theirs ("Emergency preparedness:"); that every maker is link-only (nothing read) with its reason, an
https address and no manual-copying site, and no maker id is used twice in a category prefix; that no Internet Archive
word repeats a word of another category; that the notices carry the generator and radio safety words (the same words
as the packs); that the military radio manuals are marked military so their own front text is read; and that a made-up
military manual printing a restricted marking is not listed.

Run it from the repository's folder:   python3 -m pytest manuals/test_preparedness_radio_manuals.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402
import preparedness_manuals as P  # noqa: E402
import radio_manuals as R  # noqa: E402

PREP = tuple(P.CATEGORIES)
RADIO = tuple(R.CATEGORIES)


def test_categories_listed_with_their_headings():
    assert PREP == ("emergency_power", "emergency_preparedness_gear")
    assert RADIO == ("radio_two_way", "radio_weather_alert", "radio_ham_makers", "radio_mesh_satellite",
                     "radio_military_manuals")
    for key in PREP + RADIO:
        cat = C.CATEGORIES[key]
        assert cat is (P.CATEGORIES.get(key) or R.CATEGORIES.get(key)), key
        assert cat["name"] and cat["kind"] == "manuals" and cat["licence"] and cat["notice"], key
        assert cat["ia"] and len(cat["ia"]) == len(set(cat["ia"])), key
        for guide in cat.get("guidance", []):
            assert guide["url"].startswith("https://") and guide["title"] and guide["by"], key
    for key in PREP:
        assert C.CATEGORIES[key]["name"].startswith("Emergency preparedness: "), key
    for key in RADIO:
        assert C.CATEGORIES[key]["name"].startswith("Radio communications: "), key
    assert not any(c["name"].startswith("Radio communications: ") for k, c in C.CATEGORIES.items() if k not in RADIO)


def test_safety_notices():
    for words in ("outdoors", "20 feet", "carbon monoxide", "911", "transfer switch", "licensed electrician"):
        assert words in C.CATEGORIES["emergency_power"]["notice"], words
    for key in RADIO:
        assert C.CATEGORIES[key]["notice"].startswith(R.RADIO_SAFETY), key
    assert "beaconregistration.noaa.gov" in C.CATEGORIES["radio_mesh_satellite"]["notice"]
    assert "SAME code" in C.CATEGORIES["radio_weather_alert"]["notice"]
    sys.path.insert(1, os.path.join(os.path.dirname(HERE), "packs"))
    import build_packs  # noqa: F401 - loaded first, as the pack files expect
    import preparedness_packs
    import radio_packs
    assert P.GENERATOR_NOTE == preparedness_packs.GENERATOR_NOTE
    assert R.RADIO_SAFETY == radio_packs.RADIO_SAFETY


def test_no_word_repeats_another_category():
    mine = set(PREP + RADIO)
    theirs = {w for k, c in C.CATEGORIES.items() if k not in mine for w in (c.get("ia") or [])}
    seen = set()
    for key in PREP + RADIO:
        words = set(C.CATEGORIES[key]["ia"])
        assert not words & theirs, (key, words & theirs)
        assert not words & seen, (key, words & seen)
        seen |= words


def test_makers_are_link_only():
    seen = set()
    for key in PREP + RADIO:
        for m in C.CATEGORIES[key].get("makers", []):
            assert m["access"] == "link" and m["reason"] and m["library"].startswith("https://"), m["key"]
            assert m["category"] == key and m["types"] == [] and "Program Downloader" in m["reason"]
            assert (m["prefix"], m["key"]) not in seen, m["key"]
            seen.add((m["prefix"], m["key"]))
            for site in B.NEVER_SITES:
                assert site not in str(m), m["key"]
    prefixes = {m["prefix"] for k in PREP + RADIO for m in C.CATEGORIES[k].get("makers", [])}
    others = {m.get("prefix") for k, c in C.CATEGORIES.items() if k not in PREP + RADIO for m in c.get("makers", [])}
    assert not prefixes & others, prefixes & others


class FakeFetch:
    """Made-up Internet Archive metadata and text files."""

    def __init__(self, files, text):
        self.files, self.text_body, self.asked = files, text, []

    def json(self, url, headers=None, cache=True):
        self.asked.append(url)
        return {"files": self.files, "metadata": {}}

    def text(self, url, headers=None, cache=True):
        self.asked.append(url)
        return self.text_body

    def size(self, url):
        return 1000


def test_military_manuals_read_their_front_text():
    guides = C.CATEGORIES["radio_military_manuals"]["public_guides"]
    assert guides and all(g["military"] and g["ia"] and g["year"] for g in guides)
    for doc in guides:
        for site in B.COPY_SITE_ITEMS:
            assert site not in doc["ia"].lower(), doc["ia"]
    files = [{"name": "x.pdf", "format": "Text PDF", "size": "100"}, {"name": "x_djvu.txt", "format": "DjVuTXT"}]
    tc = next(g for g in guides if g["ia"] == "TC9-64")
    ok = FakeFetch(files, "TC 9-64 ... Approved for public release; distribution is unlimited.")
    got, _notes = B.public_guide_entries(ok, [tc], "radio_military_manuals")
    assert len(got) == 1 and got[0]["manuals"][0]["rights"] == "a US government work (public domain)"
    restricted = FakeFetch(files, "TC 9-64 ... Distribution authorized to DoD components only.")
    got, notes = B.public_guide_entries(restricted, [tc], "radio_military_manuals")
    assert got == [] and notes
    old = next(g for g in guides if g["year"] < 1964)
    got, _notes = B.public_guide_entries(FakeFetch(files, "TM 11-2630 Antenna Equipment"), [old],
                                         "radio_military_manuals")
    assert len(got) == 1
