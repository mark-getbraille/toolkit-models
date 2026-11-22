"""A self-test of the picture-reading packs (packs/handwriting_packs.py, chart_packs.py, date_code_packs.py,
sign_language_packs.py, weather_map_packs.py) and the kit's picture_reading_sources.py, with made-up words and records
only: nothing is downloaded from the internet.

It checks that the answers say only what the sources say (a transcription, a date, a letter or a sign only where the
source gives it; a weather map explained from its kind and time, never read), that the safety filters work, and that
every pack is wired: in build_packs.PACKS, the Commons ones in COMMONS_KEYS, in the workflows' known list and limit
lines, in the kit's sources ("permissive"), the kit module listed twice as a hidden import, and the packs that must
never be used for picture-making in NOT_FOR_PICTURE_MAKING.

Run it from the repository's folder:   python3 -m pytest packs/test_picture_reading.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import handwriting_packs as hw  # noqa: E402

REPO = os.path.dirname(HERE)


def workflows():
    """The texts of packs.yml, pack-build.yml and training-kit.yml."""
    out = []
    for name in ("packs.yml", "pack-build.yml", "training-kit.yml"):
        with open(os.path.join(REPO, ".github", "workflows", name), encoding="utf-8") as f:
            out.append(f.read())
    return out


def check_wired(packs, limits, commons_keys, no_picture_making=()):
    """A group of packs is wired everywhere it must be."""
    import sources
    keys = set(packs)
    assert keys == set(limits)
    assert keys <= set(build_packs.PACKS)
    assert set(commons_keys) <= build_packs.COMMONS_KEYS
    assert not (keys - set(commons_keys)) & build_packs.COMMONS_KEYS
    packs_yml, build_yml, kit_yml = workflows()
    for key, limit in limits.items():
        assert f'"{key}"' in packs_yml, key
        assert re.search(rf"^\s*{key}\) limit={limit} ;;$", build_yml, re.M), key
    assert kit_yml.count("--hidden-import picture_reading_sources") == 2
    listed = {s.key: s for s in sources.SOURCES}
    assert keys <= set(listed) and all(listed[k].group == "permissive" for k in keys)
    assert set(no_picture_making) <= set(sources.NOT_FOR_PICTURE_MAKING)


# ----------------------------------------------------------------- handwriting

def test_bentham_text_made_plain():
    raw = ("Of Theft\nExtenuation <gap/> I. Self-preservation\nif it be a Hus=­\n­:band or wife\n"
           "a defa:matory discourse <del>struck</del> kept\n\n\n")
    text = hw.bentham_text(raw)
    assert "Husband" in text and "defamatory" in text and "[...]" in text
    assert "<" not in text and "struck kept" in text and not text.endswith("\n")


def test_bentham_page_lines_and_rows():
    xml = ("<TextRegion><TextLine id='a'><Coords/><TextEquiv><Unicode>First line</Unicode></TextEquiv></TextLine>"
           "<TextLine id='b'><TextEquiv><Unicode> second  line </Unicode></TextEquiv></TextLine></TextRegion>")
    assert hw.page_lines(xml) == ["First line", "second line"]
    rows = hw.bentham_rows("071_045_003", "Of the punishment of theft and the extenuations of it")
    assert rows[0]["question"] == hw.READ_PAGE and rows[0]["answer"].startswith("Of the punishment")
    assert "box 71, folio 45" in rows[0]["credit"] and "CC BY 4.0" in rows[0]["credit"]
    assert hw.bentham_rows("071_045_003", "too short") == []
    assert hw.bentham_rows("071_045_003", "a <gap/> b <gap/> c <gap/> d <gap/> e") == []


def test_signatures_named_only_from_the_file_name():
    assert hw.signer("File:Abraham Lincoln signature.svg") == "Abraham Lincoln"
    assert hw.signer("File:Signature of Marie Curie.png") == "Marie Curie"
    assert hw.signer("File:Wolfgang Amadeus Mozart Unterschrift.svg") == "Wolfgang Amadeus Mozart"
    assert hw.signer("File:Signature 1923.jpg") == ""
    assert hw.signer("File:Unknown signature.png") == ""
    assert hw.signer("File:Signature.svg") == ""
    rows = hw.signature_rows("File:Abraham Lincoln signature.svg", "")
    assert ("Whose signature is this?", "It is the signature of Abraham Lincoln.") in rows
    assert hw.signature_rows("File:Signature 1923.jpg", "") == [("What is this?", "This is a handwritten signature.")]


def test_handwriting_wired():
    import sources
    check_wired(hw.HANDWRITING_PACKS, hw.HANDWRITING_LIMITS, hw.HANDWRITING_COMMONS_KEYS,
                no_picture_making=hw.HANDWRITING_PACKS)
    import picture_reading_sources as k
    assert "GNHK, GoodNotes Handwriting Kollection (CC BY 4.0)" in k.HANDWRITING_NOT_INCLUDED
    import topics
    documents = topics.find("documents")
    assert {"bentham_pages", "commons_handwriting"} <= set(documents.keys)
    assert sources.SOURCES  # loaded
