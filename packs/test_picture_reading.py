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


# ----------------------------------------------------------------- charts and diagrams

def test_openstax_figures_parsed_and_checked():
    import chart_packs as ch
    cnxml = ('<figure id="F1"><title>The Budget <emphasis>Constraint</emphasis></title>'
             '<media id="m1" alt="The graph shows a downward-sloping budget line from 5 burgers to 20 tickets.">'
             '<image mime-type="image/jpg" src="../../media/CNX_Econ_C02_001.jpg"/></media>'
             '<caption>Each point costs $10 in all.</caption></figure>'
             '<figure id="F2"><media id="m2" alt="A photograph of people riding camels near two pyramids.">'
             '<image src="../../media/photo.jpg"/></media><caption>A command economy. (credit: "Pyramids" by '
             'Someone/Flickr, CC BY 2.0)</caption></figure>'
             '<figure id="F3"><media alt="x"><image src="../../media/a.jpg"/></media><media alt="y">'
             '<image src="../../media/b.jpg"/></media></figure>'
             '<figure id="F4"><media alt="A diagram of the female reproductive system with its parts named.">'
             '<image src="../../media/r.jpg"/></media><caption>The reproductive system.</caption></figure>'
             '<figure id="F5"><media alt="A graph of prices against quantity with two curves crossing.">'
             '<image src="../../media/g.jpg"/></media><caption>Supply and demand meet here. (credit: modification '
             'of work by Jane Roe, all rights reserved)</caption></figure>')
    figs = ch.cnxml_figures(cnxml)
    assert [f[0] for f in figs] == ["F1", "F2", "F4", "F5"]
    assert figs[0][1] == "The Budget Constraint" and figs[0][5] == "CNX_Econ_C02_001.jpg" and figs[0][3] == ""
    assert figs[1][3].startswith("credit:") and figs[1][2] == "A command economy."
    rows = ch.figure_rows(figs[0], "Principles of Economics 3e", "page")
    assert rows[0] == {"question": ch.DESCRIBE, "answer": "The graph shows a downward-sloping budget line from 5 "
                       "burgers to 20 tickets.", "credit": "OpenStax, Principles of Economics 3e (page), figure F1, "
                       "CC BY 4.0"}
    assert rows[1]["answer"] == "The Budget Constraint: Each point costs $10 in all."
    assert ch.figure_rows(figs[1], "b", "p") == []          # a credited photo, not a chart
    assert ch.figure_rows(figs[2], "b", "p") == []          # reproduction: left out
    assert ch.figure_rows(figs[3], "b", "p") == []          # all rights reserved
    assert all(len(commit) == 40 for _r, commit, _s, _n in ch.OPENSTAX_BOOKS)
    assert ch.CC_BY_4.search('<md:license url="http://creativecommons.org/licenses/by/4.0/"/>')
    assert not ch.CC_BY_4.search('<md:license url="http://creativecommons.org/licenses/by-nc-sa/4.0/">')


def test_commons_charts_need_a_description():
    import chart_packs as ch
    rows_for = ch.chart("a pie chart")
    assert rows_for("File:Pie.svg", "Too short.") == []
    text = "Share of electricity generation in Germany by source in 2020, from official statistics."
    assert rows_for("File:Pie.svg", text) == [(ch.CHART_KIND, "This is a pie chart."), (ch.CHART_SHOWS, text)]


def test_tqa_rows():
    import picture_reading_sources as k
    lessons = [{"instructionalDiagrams": {"a": {"imagePath": "teaching_images/earth.png",
                                                "processedText": "The diagram shows the different layers of the "
                                                                 "earth: the crust, the mantle and the core"},
                                          "b": {"imagePath": "teaching_images/x.png", "processedText": "Too short"}},
                "topics": {"t": {"content": {"figures": [{"imagePath": "textbook_images/f.png",
                                                          "caption": "A volcano erupting ash into the sky"},
                                                         {"imagePath": "textbook_images/g.png", "caption": "Ash"}]}}}}]
    rows = k.tqa_rows(lessons, "train")
    assert rows == [("tqa_train_val_test/train/teaching_images/earth.png",
                     {"question": k.EXPLAIN, "answer": "The diagram shows the different layers of the earth: the "
                                                       "crust, the mantle and the core.", "split": ""}),
                    ("tqa_train_val_test/train/textbook_images/f.png",
                     {"question": k.FIGURE_SHOWS, "answer": "A volcano erupting ash into the sky.", "split": ""})]


def test_charts_wired():
    import chart_packs as ch
    import sources
    check_wired(ch.CHART_PACKS, ch.CHART_LIMITS, ch.CHART_COMMONS_KEYS, no_picture_making=("openstax_figures",))
    listed = {s.key: s for s in sources.SOURCES}
    assert listed["tqa_diagrams"].group == "noncommercial"
    import topics
    assert {"openstax_figures", "commons_charts", "tqa_diagrams"} <= set(topics.find("documents").keys)


# ----------------------------------------------------------------- date codes

def test_dates_only_where_the_file_says():
    import date_code_packs as dc
    rows = dc.date_rows("File:Milk.jpg", "Milk carton with best before 03/2021 printed on the top.")
    assert rows == [(dc.ASK_MARK, "It shows a best-before date."),
                    ("What is the best-before date on this package?", "The best-before date shown is 03/2021.")]
    assert dc.date_rows("File:Can.jpg", "Use by 2 JAN 2015")[1][1] == "The use-by date shown is 2 JAN 2015."
    assert dc.date_rows("File:Box.jpg", "Medicine box, EXP 05/2023")[1][1] == "The expiry date shown is 05/2023."
    assert dc.date_rows("File:Pills.jpg", "Lot number: A12B34, on a medicine box")[1][1] == \
        "The lot number shown is A12B34."
    # the mark named, but no date in the file's own words: only what kind of mark it is
    assert dc.date_rows("File:Best before date on yoghurt.jpg", "") == [(dc.ASK_MARK, "It shows a best-before date.")]
    # a date in the title only is not read (titles carry upload dates and catalogue numbers)
    assert len(dc.date_rows("File:Best before 2019-01-01 milk.jpg", "")) == 1
    # not a date mark, or not packaging
    assert dc.date_rows("File:Kids.jpg", "A lot of children use by the river.") == []
    assert dc.date_rows("File:Passport.jpg", "Passport expiry date 2020") == []
    assert dc.date_rows("File:Card.jpg", "A credit card with its expiration date: 05/24") == []
    assert dc.date_rows("File:Lot.jpg", "A parking lot in Ohio") == []
    # people checking shelves, chips' date codes and manuscripts are not packaging labels
    assert dc.date_rows("File:Checking expiration dates.jpg", "Staff Sgt. Roe checks expiration dates on supplies "
                                                              "and food packages.") == []
    assert dc.date_rows("File:Numpad date code on IC.jpg", "Week 18 Year 1982 date code on IC.") == []
    assert dc.date_rows("File:Theological miscellany.jpg", "Ms. codex. Lot: 34, a manuscript product") == []


def test_dates_wired():
    import date_code_packs as dc
    check_wired(dc.DATE_CODE_PACKS, dc.DATE_CODE_LIMITS, dc.DATE_CODE_COMMONS_KEYS,
                no_picture_making=dc.DATE_CODE_PACKS)
    import picture_reading_sources as k
    assert "ExpDate (Seker and Ahn, 2022, CC BY 4.0)" in k.DATE_NOT_INCLUDED
    import topics
    assert "commons_date_codes" in topics.find("food").keys


# ----------------------------------------------------------------- sign language

def test_signs_named_only_where_labelled():
    import sign_language_packs as sl
    letters = sl.alphabet_rows("ASL letters")
    assert letters("File:Sign language A.svg", "")[0] == (sl.ASK_LETTER, "The letter A, in the American Sign "
                                                                         "Language manual alphabet.")
    assert letters("File:ASL number 5.jpg", "") == [(sl.ASK_NUMBER, "The number 5, in American Sign Language.")]
    assert letters("File:BSL letter Q.jpg", "")[0][1].endswith("British Sign Language manual alphabet.")
    assert letters("File:Asl alphabet gallaudet.svg", "")[0][1].startswith("This is a chart of the American")
    assert letters("File:Hand photo.jpg", "") == []
    signing = sl.signing_rows("American Sign Language")
    assert signing("File:ASL sign for love.jpg", "") == [(sl.ASK_SIGN, "It is the American Sign Language sign for "
                                                                       "\"love\".")]
    assert signing("File:Hello.jpg", "A woman signing for \"hello\" in ASL")[0][1].endswith("for \"hello\".")
    assert signing("File:Event.jpg", "People at a deaf community event in Ohio") == [
        (sl.ASK_WHAT, "This shows American Sign Language.")]
    assert signing("File:Event.jpg", "") == []


def test_sign_language_wired():
    import sign_language_packs as sl
    import sources
    check_wired(sl.SIGN_LANGUAGE_PACKS, sl.SIGN_LANGUAGE_LIMITS, sl.SIGN_LANGUAGE_COMMONS_KEYS,
                no_picture_making=sl.SIGN_LANGUAGE_PACKS)
    assert "commons_sign_language" in sources.PEOPLE_AND_BODILY_PACK_KEYS


# ----------------------------------------------------------------- weather maps

ADVISORY = """<pre>Tropical Storm Idalia Advisory Number  10
NWS National Hurricane Center Miami FL       AL102023
SUMMARY OF 1000 PM CDT...0300 UTC...INFORMATION
-----------------------------------------------
LOCATION...22.0N 85.0W
ABOUT 10 MI...15 KM NW OF THE WESTERN TIP OF CUBA
MAXIMUM SUSTAINED WINDS...70 MPH...110 KM/H
PRESENT MOVEMENT...N OR 10 DEGREES AT 8 MPH...13 KM/H
MINIMUM CENTRAL PRESSURE...983 MB...29.03 INCHES

WATCHES AND WARNINGS
--------------------
</pre>"""


def test_weather_maps_explained_not_read():
    import datetime
    import weather_map_packs as w
    rows = w.wpc_rows("radsfcus_exp", datetime.datetime(2024, 1, 1, 12))
    assert "12:00 UTC on Monday 1 January 2024" in rows[0]["answer"] and w.FRONTS in rows[0]["answer"]
    assert "radar echoes" in rows[0]["answer"] and rows[0]["answer"].endswith(w.NOT_READ)
    assert rows[1]["answer"] == "It is the surface analysis for 12:00 UTC on Monday 1 January 2024."
    assert "public domain" in rows[0]["credit"]
    items = w.wpc_items(10, seed="test")
    assert len({i[0] for i in items}) == 10 and all(i[1].startswith(w.WPC_ARCHIVE) for i in items)
    heading, lines = w.advisory_summary(ADVISORY)
    assert heading == "Tropical Storm Idalia Advisory Number 10"
    assert lines == ["the centre is at 22.0 degrees north, 85.0 degrees west",
                     "about 10 miles (15 km) north-west of the Western Tip of Cuba",
                     "its strongest sustained winds are 70 mph (110 km/h)",
                     "it is moving north (10 degrees) at 8 mph (13 km/h)",
                     "its lowest central pressure is 983 mb (29.03 inches)"]
    rows = w.cone_rows("AL102023", "Hurricane IDALIA", "10", ADVISORY, 2023)
    assert rows[0]["answer"].startswith("This is the National Hurricane Center's five-day forecast cone graphic for "
                                        "Tropical Storm Idalia, advisory 10, in the 2023 Atlantic")
    assert w.CONE_LEGEND in rows[0]["answer"] and "al102023.public.010.shtml" in rows[0]["credit"]
    # without the advisory's words, nothing is said about where the storm is
    rows = w.cone_rows("EP012023", "Hurricane ADRIAN", "3", "", 2023)
    assert len(rows) == 1 and "Hurricane Adrian" in rows[0]["answer"] and "degrees" not in rows[0]["answer"]


def test_weather_maps_wired():
    import weather_map_packs as w
    check_wired(w.WEATHER_MAP_PACKS, w.WEATHER_MAP_LIMITS, ())
    import picture_reading_sources as k
    assert any("Storm Prediction Center" in key for key in k.WEATHER_NOT_INCLUDED)
    import topics
    assert {"wpc_surface_maps", "nhc_forecast_cones"} <= set(topics.find("documents").keys)


def test_captions_and_autographs():
    import described_commons as dcm
    assert dcm.own_caption_row("t", "The autograph of Bob Boone on a baseball.")["answer"].startswith("The autograph")
    assert dcm.own_caption_row("t", "This image is available from the Netherlands Institute for Art History.") is None
    assert dcm.own_caption_row("t", "Widmung von Rudolf Ernst Keller für Rudolf Hotzenköcherle, Zürich.") is None
    assert dcm.own_caption_row("t", "Too short.") is None
    assert hw.signer("File:Bob Boone's Autograph.jpg") == "Bob Boone"
    rows = hw.autograph_rows("File:Brandenburger family scrapbook page 6.jpg", "")
    assert rows == [("What is this?", "This is an autograph: something written or signed by hand by its author.")]
