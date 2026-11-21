"""Self-tests of animal_sounds.py (the NPS animal sounds book) with made-up pages only: nothing is downloaded. It
checks that only the animal groups of the gallery are taken (and the chickens), that each page's title, caption,
description, credit, audio transcript and MP3 address are read, that a page without a recording is passed over, and
that the book is written with its pages grouped by kind of animal, links to the recordings and the licence line.

Run it from the repository's folder:   python3 -m pytest textbooks/test_animal_sounds.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import animal_sounds as A  # noqa: E402

GALLERY = """<p><strong>Amphibians</strong></p><a href="/subjects/sound/sounds-pigfrog.htm">Pig Frog</a>
<p><strong>Birds</strong></p><a href="/subjects/sound/sounds-osprey.htm">Osprey</a>
<a href="https://www.nps.gov/subjects/sound/sounds-dawnchorus_bryce.htm">Dawn Chorus</a>
<p><strong>Cultural-Historical</strong></p><a href="/subjects/sound/sounds-cannon.htm">Cannon</a>
<a href="/subjects/sound/sounds-chickens.htm">Chickens</a>
<p><strong>Machines</strong></p><a href="/subjects/sound/sounds-jet.htm">Jet</a>
<p><strong>Mammals</strong></p><a href="/subjects/sound/sounds-elk.htm">Elk</a>
<a href="/subjects/sound/siteindex.htm">Site index</a>"""


def sound_html(title, mp3=True):
    """A made-up gallery page laid out as the real ones are."""
    audio = ('<audio controls><source src="https://www.nps.gov/nps-audiovideo/legacy/mp3/x-' + title.replace(" ", "")
             + '.mp3" type="audio/mp3" /></audio>') if mp3 else ""
    return (f'<h1 class="page-title">Sound Gallery - {title}</h1><figure><img alt="x"><figcaption>A {title.lower()} '
            f'calling at dawn. <p class="figcredit">Photo by Someone</p></figcaption></figure>{audio}'
            f'<div><p>Sound recording of a {title.lower()}, Example National Park, Utah.</p></div>'
            '<div><h4>Credit / Author:</h4><p>NPS/Jane Example</p></div>'
            f'<div><h4>Audio Transcript</h4><p>Loud rising whistles of a {title.lower()}.</p></div>'
            '<p>Listen to more natural and human-made sounds</p>')


def test_gallery_takes_only_animals():
    links = A.gallery_links(GALLERY)
    assert links == [("Amphibians", "https://www.nps.gov/subjects/sound/sounds-pigfrog.htm"),
                     ("Birds", "https://www.nps.gov/subjects/sound/sounds-osprey.htm"),
                     ("Birds", "https://www.nps.gov/subjects/sound/sounds-dawnchorus_bryce.htm"),
                     ("Birds", "https://www.nps.gov/subjects/sound/sounds-chickens.htm"),
                     ("Mammals", "https://www.nps.gov/subjects/sound/sounds-elk.htm")]


def test_sound_page_fields():
    s = A.sound_page(sound_html("Osprey"), "https://www.nps.gov/subjects/sound/sounds-osprey.htm")
    assert s["title"] == "Osprey" and s["caption"] == "A osprey calling at dawn."
    assert s["description"] == "Sound recording of a osprey, Example National Park, Utah."
    assert s["credit"] == "NPS/Jane Example" and s["transcript"] == "Loud rising whistles of a osprey."
    assert s["mp3s"] == ["https://www.nps.gov/nps-audiovideo/legacy/mp3/x-Osprey.mp3"]
    assert A.sound_page(sound_html("Osprey", mp3=False), "u") is None


def test_book(monkeypatch, tmp_path):
    pages = {A.GALLERY: GALLERY}
    for title, path in (("Pig frog", "sounds-pigfrog"), ("Osprey", "sounds-osprey"), ("Elk bugle", "sounds-elk"),
                        ("Chickens", "sounds-chickens")):
        pages[f"https://www.nps.gov/subjects/sound/{path}.htm"] = sound_html(title)
    pages["https://www.nps.gov/subjects/sound/sounds-dawnchorus_bryce.htm"] = sound_html("Dawn chorus", mp3=False)
    monkeypatch.setattr(B, "fetch", lambda url, cache=None, **kw: pages[url])
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: True)
    left = []
    book = A.nps_book(None, left)
    titles = [(p.unit, p.title) for p in book.pages]
    assert titles == [("", "About this book"), ("Amphibians", "Pig frog"), ("Birds", "Chickens"), ("Birds", "Osprey"),
                      ("Mammals", "Elk bugle")]
    assert left == [{"title": "https://www.nps.gov/subjects/sound/sounds-dawnchorus_bryce.htm",
                     "reason": "No recording on the page."}]
    osprey = next(p for p in book.pages if p.title == "Osprey")
    assert "What it sounds like: Loud rising whistles of a osprey." in osprey.body
    assert 'href="https://www.nps.gov/nps-audiovideo/legacy/mp3/x-Osprey.mp3"' in osprey.body
    assert "public domain" in book.pages[0].body and "xeno-canto" in book.pages[0].body
    entry = B.write_book(book, str(tmp_path), versioned=True)
    assert entry["licence_kind"] == "open" and entry["group"] == "science" and entry["article_count"] >= 6


def test_refused_by_robots(monkeypatch):
    monkeypatch.setattr(B, "allowed_by_robots", lambda url, cache=None: False)
    left = []
    assert A.nps_book(None, left) is None and "robots.txt" in left[0]["reason"]
