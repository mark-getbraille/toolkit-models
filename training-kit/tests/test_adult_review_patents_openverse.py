"""Tests of the US patent drawings and Openverse product-photo collections of kit/adult_review_sources.py: the patent
figure-description reader ("FIG. 1 is a perspective view of ..."), the copyright and mask-work notice skip (37 CFR
1.71(d)/(e)), the patent screening, reading drawing sheets out of a PDF, and the Openverse filters (no person, no
Flickr, no adult site, licence kinds, sexual acts and BDSM, dedupe against the Commons collections).
Every patent, record and picture here is made up: nothing is downloaded from the internet.

Run:  xvfb-run -a python3 -m pytest -q training-kit/tests     (on Windows: python -m pytest -q training-kit\\tests)
"""

import io
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(KIT, "kit"))

import adult_review_sources as ars  # noqa: E402

# A made-up patent in the USPTO full-text layout (us-patent-grant), with its brief description of the drawings.
PATENT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<us-patent-grant lang="EN" id="US09999999-20200101">
<us-bibliographic-data-grant>
<publication-reference><document-id><country>US</country><doc-number>09999999</doc-number><kind>B2</kind>
<date>20200101</date></document-id></publication-reference>
<invention-title id="d2e43">PERSONAL MASSAGER WITH FLEXIBLE NECK</invention-title>
<us-parties><inventors><inventor sequence="00"><addressbook><last-name>Example</last-name><first-name>Ann</first-name>
</addressbook></inventor><inventor sequence="01"><addressbook><last-name>Sample</last-name><first-name>Bo</first-name>
</addressbook></inventor></inventors></us-parties>
</us-bibliographic-data-grant>
<abstract id="abstract"><p id="p-0001">A hand-held massager with a motor in its handle.</p></abstract>
<description id="description">
<heading id="h-0001" level="1">BACKGROUND</heading>
<p id="p-0002">Massagers are known.</p>
<description-of-drawings>
<heading id="h-0002" level="1">BRIEF DESCRIPTION OF THE DRAWINGS</heading>
<p id="p-0003" num="0003"><figref idref="DRAWINGS">FIG. 1</figref> is a perspective view of a massager according to
one embodiment of the present invention;</p>
<p id="p-0004" num="0004"><figref idref="DRAWINGS">FIG. 2</figref> is a side elevation view showing the motor inside
the handle; and</p>
<p id="p-0005" num="0005"><figref idref="DRAWINGS">FIG. 3</figref> is a cross-sectional view taken along line 3-3 of
<figref idref="DRAWINGS">FIG. 2</figref>.</p>
</description-of-drawings>
<p id="p-0006">The massager has a sleep mode to save the battery.</p>
</description>
</us-patent-grant>"""


# ----------------------------------------------------------------- patent figure descriptions

def test_patent_text_reads_the_brief_description_of_the_drawings():
    info = ars.patent_text(PATENT_XML)
    assert info["title"] == "PERSONAL MASSAGER WITH FLEXIBLE NECK"
    assert info["number"] == "9999999" and info["date"] == "20200101"
    assert info["inventors"] == ["Ann Example", "Bo Sample"]
    assert len(info["drawings"]) == 3
    assert "hand-held massager" in info["abstract"]


def test_figure_descriptions_in_plain_words():
    figures = ars.brief_figures(ars.patent_text(PATENT_XML)["drawings"])
    assert figures == [
        (["1"], "a view at an angle (perspective) of a massager"),
        (["2"], "a side view showing the motor inside the handle"),
        (["3"], "a cross-section view as if cut along line 3-3 of figure 2"),
    ]


def test_figure_labels_lists_ranges_and_letters():
    figures = ars.brief_figures(["FIGS. 4A and 4B are top plan views of the ring. FIGS. 5 through 7 are schematic "
                                 "diagrams of the control circuit; FIG. 8 is an exploded view thereof."])
    assert figures[0] == (["4A", "4B"], "views from above of the ring")
    assert figures[1] == (["5", "6", "7"], "simplified diagrams of the control circuit")
    assert figures[2] == (["8"], "an exploded view (the parts drawn apart)")
    assert ars.brief_figures(["The invention is described below."]) == []


def test_heading_layout_without_description_of_drawings_element():
    xml = ("<us-patent-grant><description><heading>BRIEF DESCRIPTION OF THE DRAWINGS</heading><p>FIG. 1 is a front "
           "view of a condom.</p><heading>DETAILED DESCRIPTION</heading><p>FIG. 1 shows more.</p></description>"
           "</us-patent-grant>")
    assert ars.brief_figures(ars.patent_text(xml)["drawings"]) == [(["1"], "a front view of a condom")]


def test_patent_draft_with_and_without_a_known_figure():
    figures = ars.brief_figures(ars.patent_text(PATENT_XML)["drawings"])
    text, note = ars.patent_draft("a device for stimulating the clitoris", "PERSONAL MASSAGER WITH FLEXIBLE NECK",
                                  2, 3, figures)
    assert text.startswith('This is a drawing from a US patent for a device for stimulating the clitoris, titled '
                           '"Personal massager with flexible neck": figure 2, a side view showing the motor inside the '
                           'handle.')
    assert note == ""
    text, note = ars.patent_draft("a condom", "Condom", 1, 2, figures)          # 2 sheets, 3 figures: not matched
    assert "drawing sheet 1 of 2" in text and "figure 3, a cross-section view" in text
    assert "Which figure is on this sheet" in note


def test_patent_kind_credit_and_body_note():
    assert ars.patent_kind(["A61H 19/44", "A61H19/00"]).startswith("a long, rounded device")
    assert ars.patent_kind(["A61F6/065"]).startswith("a female condom")
    assert ars.patent_kind(["A61F6/04"]) == "a condom"
    assert ars.patent_kind(["600/038000"]) == "a sexual device"
    assert ars.patent_credit("9999999", "PERSONAL MASSAGER", ["Ann Example", "Bo Sample", "Cy Third"], "2020") == \
        "US Patent 9,999,999, Personal massager, Ann Example, Bo Sample and others, 2020; public domain (USPTO)"
    _text, note = ars.patent_draft("a condom", "Condom", 1, 1, [(["1"], "a side view of the condom on a penis")])
    assert "only an adult body" in note


# ----------------------------------------------------------------- copyright notice and screening

def test_copyright_or_mask_work_notice_leaves_the_patent_out():
    for notice in ("A portion of the disclosure of this patent document contains material which is subject to "
                   "copyright protection.", "This document contains material subject to mask work protection.",
                   "© 2015 Example Corp.", "(c) 2015 Example Corp. All rights reserved."):
        why = ars.patent_problem("Personal massager", "", "", notice)
        assert "copyright or mask-work notice" in why
    info = ars.patent_text(PATENT_XML)
    assert ars.patent_problem(info["title"], info["abstract"], " ".join(info["drawings"]), info["text"],
                              PATENT_XML) == ""
    assert "copyright" in ars.patent_problem("Massager", "", "", "", "<p>Copyright 2010 Someone</p>")


def test_patent_screening():
    assert ars.patent_problem("Personal massager", "", "", "The device has a sleep mode and a Young's modulus "
                              "of this kind.") == ""                                 # technical words are not people
    assert "child" in ars.patent_problem("Massager", "", "", "Keep away from children.")
    assert "animal" in ars.patent_problem("Rabbit-style vibrator", "", "", "")
    assert "animal" in ars.patent_problem("Massager", "", "", "Also suitable for a dog.")
    assert "restraint or BDSM" in ars.patent_problem("Massager", "", "", "Used with a restraint system.")
    assert "harm, no consent" in ars.patent_problem("Device", "", "", "Used on an unconscious person.")
    assert ars.patent_problem("Device", "", "FIG. 1 shows a young woman", "")      # screen() on the figures
    assert "under 18" in ars.patent_problem("Device", "", "", "suitable for a 16-year-old")


# ----------------------------------------------------------------- drawing sheets out of a PDF

def fake_pdf(pictures):
    """A small PDF-like file holding the given (dictionary, data) pictures, as the USPTO's PDF builder stores them."""
    out = b"%PDF-1.2\r"
    for number, (head, data) in enumerate(pictures, start=10):
        out += (f"{number} 0 obj\r<< /Type /XObject {head} /Length {len(data)} >>\rstream\r").encode() + data + \
            b"\rendstream\rendobj\r"
    return out + b"trailer\r<< >>\r%%EOF"


def test_pdf_images_reads_fax_coded_and_jpeg_sheets():
    pytest.importorskip("PIL")
    from PIL import Image, ImageDraw
    sheet = Image.new("1", (300, 400), 1)
    ImageDraw.Draw(sheet).rectangle((50, 50, 250, 350), outline=0, width=4)
    # Pillow writes a black-and-white TIFF as "0 is black"; fax coding in a PDF counts 0 as white, so the sheet is
    # inverted before it is coded, to give the same bits as a real USPTO drawing sheet.
    from PIL import ImageOps
    tiff = io.BytesIO()
    ImageOps.invert(sheet.convert("L")).convert("1").save(tiff, "TIFF", compression="group4")
    with Image.open(io.BytesIO(tiff.getvalue())) as t:
        offset, size = t.tag_v2[273][0], t.tag_v2[279][0]
    g4 = tiff.getvalue()[offset:offset + size]
    jpeg = io.BytesIO()
    Image.new("RGB", (200, 150), "white").save(jpeg, "JPEG")
    pdf = fake_pdf([
        ("/Filter /CCITTFaxDecode /DecodeParms << /Columns 300 /K -1 /Rows 400 >> /Height 400 /Subtype /Image "
         "/Width 300 /BitsPerComponent 1", g4),
        ("/Filter /DCTDecode /Height 150 /Subtype /Image /Width 200 /BitsPerComponent 8", jpeg.getvalue()),
        ("/Filter /JBIG2Decode /Height 10 /Subtype /Image /Width 10", b"not read"),
    ])
    found = ars.pdf_images(pdf)
    assert len(found) == 2
    with Image.open(io.BytesIO(found[0])) as first:
        first.load()
        assert first.size == (300, 400)
        grey = first.convert("L")
        assert grey.getpixel((10, 10)) == 255 and grey.getpixel((50, 200)) == 0   # white page, black line
    with Image.open(io.BytesIO(found[1])) as second:
        assert second.size == (200, 150)
    assert ars.pdf_images(b"") == [] and ars.pdf_images(b"not a pdf") == []


def test_patent_fetch_without_a_key_is_skipped_cleanly(tmp_path, monkeypatch):
    monkeypatch.delenv(ars.USPTO_KEY_ENV, raising=False)
    said = []
    summary = ars.fetch_us_patent_drawings(str(tmp_path / "patents"), 5, said.append)
    assert "skipped" in summary and ars.USPTO_KEY_ENV in summary and "Nothing was downloaded" in summary
    assert not (tmp_path / "patents").exists()


# ----------------------------------------------------------------- Openverse filters

def record(**fields):
    """A made-up Openverse image record (a product photo on Wikimedia Commons, CC BY 4.0) with fields changed."""
    item = {"id": "abc-123", "title": "Silicone dildo, product photo", "source": "wikimedia", "provider": "wikimedia",
            "license": "by", "license_version": "4.0", "url": "https://upload.wikimedia.org/x/Dildo.jpg",
            "foreign_landing_url": "https://commons.wikimedia.org/w/index.php?curid=12345", "creator": "Uploader",
            "creator_url": "", "tags": [{"name": "sex toy"}, {"name": "silicone"}], "mature": False,
            "unstable__sensitivity": []}
    item.update(fields)
    return item


def test_openverse_keeps_a_product_photo_without_a_person():
    why, product = ars.ov_check(record(), "open")
    assert why == "" and product.startswith("dildo")
    why, product = ars.ov_check(record(title="Female condom in its packet", tags=[{"name": "female condom"}]),
                                "open")
    assert why == "" and product == "female condom"
    why, product = ars.ov_check(record(title="Menstrual cups", source="wellcome_collection", tags=[],
                                       foreign_landing_url="https://wellcomecollection.org/works/x"), "open")
    assert why == "" and product == "menstrual cup"
    assert ars.ov_check(record(title="Adult toys: a vibrator"), "open")[0] == ""


@pytest.mark.parametrize("fields, kind, words", [
    ({"source": "flickr", "provider": "flickr"}, "open", "Flickr"),
    ({"source": "rawpixel", "provider": "rawpixel"}, "open", "were not checked"),
    ({"license": "by-nc"}, "open", "licence not in this collection"),
    ({"license": "by-nd"}, "share-alike", "licence not in this collection"),
    ({"license": "by-sa"}, "open", "licence not in this collection"),
    ({"license": "by"}, "share-alike", "licence not in this collection"),
    ({"foreign_landing_url": "https://www.xhamster.com/photos/1"}, "open", "porn or adult site"),
    ({"unstable__sensitivity": ["user_reported_sensitivity"]}, "open", "sensitive or mature"),
    ({"mature": True}, "open", "sensitive or mature"),
    ({"title": "Dildo, Newfoundland town sign"}, "open", "place, sign, machine"),
    ({"title": "Concrete vibrator", "tags": [{"name": "construction"}]}, "open", "not about a sex toy"),
    ({"title": "Woman holding a dildo"}, "open", "a person may be in the picture"),
    ({"tags": [{"name": "sex toy"}, {"name": "person", "accuracy": 0.97, "provider": "clarifai"}]}, "open",
     "a person may be in the picture"),
    ({"tags": [{"name": "sex toy"}, {"name": "hand"}]}, "open", "a person may be in the picture"),
    ({"title": "Dildo for pegging"}, "open", "sexual act, porn, fetish or BDSM"),
    ({"tags": [{"name": "sex toy"}, {"name": "bondage"}]}, "open", "violence, no consent"),
    ({"tags": [{"name": "sex toy"}, {"name": "leather"}]}, "open", "sexual act, porn, fetish or BDSM"),
    ({"title": "Tiny dildo"}, "open", "youthful or doubtful wording"),
    ({"title": "Dildo shaped like a horse"}, "open", "animal"),
])
def test_openverse_leaves_out(fields, kind, words):
    why, product = ars.ov_check(record(**fields), kind)
    assert words in why and product == ""


def test_openverse_share_alike_kind_and_licence_names():
    assert ars.ov_check(record(license="by-sa", license_version="2.0"), "share-alike")[0] == ""
    assert ars.ov_licence(record(license="by-sa", license_version="2.0")) == ("share-alike", "CC BY-SA 2.0")
    assert ars.ov_licence(record(license="pdm")) == ("open", "public domain (Public Domain Mark)")
    assert ars.ov_licence(record(license="cc0")) == ("open", "CC0")
    assert ars.ov_licence(record(license="by-nc-sa")) == ("", "")


def commons_info(licence="CC BY 4.0", categories="Dildos|Silicone products", description="A pink silicone dildo."):
    """Made-up Commons file details as the Commons API gives them (extmetadata values)."""
    return {"mime": "image/jpeg", "thumburl": "https://upload.wikimedia.org/thumb/x.jpg",
            "extmetadata": {"LicenseShortName": {"value": licence}, "Categories": {"value": categories},
                            "ImageDescription": {"value": description}}}


def test_openverse_commons_recheck_and_dedupe():
    product_categories = {"Sex toys", "Vibrators", "Condoms"}
    assert ars.ov_commons_check(commons_info(), "Pink dildo.jpg", "open", product_categories) == ""
    assert "already in the Commons" in ars.ov_commons_check(commons_info(categories="Vibrators|Pink"), "x.jpg",
                                                            "open", product_categories)
    assert "Commons licence" in ars.ov_commons_check(commons_info(licence="CC BY-SA 4.0"), "x.jpg", "open",
                                                     product_categories)
    assert "Commons licence" in ars.ov_commons_check(commons_info(licence="CC BY-NC 2.0"), "x.jpg", "open",
                                                     product_categories)
    assert ars.ov_commons_check(commons_info(licence="CC BY-SA 4.0"), "x.jpg", "share-alike",
                                product_categories) == ""
    assert "problem category" in ars.ov_commons_check(commons_info(categories="Dildos|Deletion requests"), "x.jpg",
                                                      "open", product_categories)
    assert "person" in ars.ov_commons_check(commons_info(description="A man holding a dildo."), "x.jpg", "open",
                                            product_categories)


def test_openverse_draft_text():
    text, thin = ars.ov_draft("Wikimedia Commons", "dildo (a sex toy shaped like a penis)", "Pink silicone dildo",
                              "A pink silicone dildo on a white background.", ["sex toy", "silicone"])
    assert text.startswith("A product photograph of a dildo (a sex toy shaped like a penis) from Wikimedia Commons")
    assert "Its tags: sex toy, silicone." in text and not thin
    assert ars.ov_product("Fotografie verschiedener Sextoys") == "sex toy"
    text, thin = ars.ov_draft("Europeana", "sex toy", "Fotografie von verschiedenen Sexspielzeugen aus dem Laden", "",
                              [])
    assert "(in the original language)" in text and thin


def test_openverse_fetch_with_made_up_answers(tmp_path, monkeypatch):
    pytest.importorskip("PIL")
    from PIL import Image
    picture = io.BytesIO()
    Image.new("RGB", (400, 300), "white").save(picture, "JPEG")
    answers = {"results": [
        record(id="museum-1", title="Condom in its wrapper", source="wellcome_collection", tags=[],
               foreign_landing_url="https://wellcomecollection.org/works/abc", url="https://iiif.example/abc.jpg"),
        record(id="flickr-1", source="flickr", foreign_landing_url="https://www.flickr.com/photos/x/1"),
        record(id="commons-1"),
    ], "page_count": 1}
    asked = []
    monkeypatch.setattr(ars.time, "sleep", lambda _s: None)
    monkeypatch.setattr(ars.rs, "session", lambda: object())
    monkeypatch.setattr(ars.rs, "get_json", lambda _s, url, **kw: asked.append(kw["params"]) or answers)
    monkeypatch.setattr(ars, "commons_query", lambda _s, _p: None)              # Commons does not answer
    monkeypatch.setattr(ars.rs, "download_picture", lambda _s, url: picture.getvalue())
    said = []
    summary = ars.fetch_openverse_products(str(tmp_path / "ov"), 5, said.append)
    assert all(p["license"] == "cc0,pdm,by" and p["excluded_source"] == "flickr" for p in asked)
    assert "1 new pictures added" in summary
    assert any("could not be checked on Commons now" in line for line in said)
    credits = (tmp_path / "ov" / "CREDITS.txt").read_text(encoding="utf-8")
    assert "openverse-museum-1.jpg" in credits and "not endorsed by Openverse" in credits
    tried = (tmp_path / "ov" / ".review-tried.json").read_text(encoding="utf-8")
    assert "commons-12345.jpg" not in tried and "openverse-flickr-1.jpg" in tried   # Commons file tried next time


# ----------------------------------------------------------------- the collection entries

def test_new_collections_are_review_only_sexual_content():
    for key, category in (("us_patent_drawings", "open"), ("openverse_products", "open"),
                          ("openverse_products_sa", "share-alike")):
        source = ars.source_by_key(key)
        assert source["review_only"] is True and source["content"] == "sexual"
        assert source["category"] == category and callable(source["fetch"])
        assert source["terms"].startswith("https://") and source["cap"] > 0
    assert ars.source_by_key("us_patent_drawings")["cap"] == 1500
    keys = [s["key"] for s in ars.ADULT_REVIEW_SOURCES]
    assert len(keys) == len(set(keys))
    assert any("Flickr" in k for k in ars.NOT_INCLUDED) and any("Google Patents" in k for k in ars.NOT_INCLUDED)


def test_english_kind_is_not_a_child_word():
    """"kind" means a child in Dutch and German, but "a kind of" / "all kinds" in English does not leave a record out."""
    assert ars.screen("A kind of screen painted with lovers") == ""
    assert ars.screen("Two lovers among all kinds of flowers") == ""
    assert ars.screen("Twee figuren, een kind en een vrouw")           # Dutch: a child
    assert ars.screen("Ein Kind schläft")                               # German: a child
