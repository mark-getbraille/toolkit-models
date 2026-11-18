"""A self-test of the Canada parsers (packs/canada_packs.py and training-kit/kit/canada_sources.py), with made-up
records only: nothing is downloaded from the internet.

It checks that:
  - a caption's province is found ("Moose Jaw, Sask." -> Saskatchewan), and two provinces give none;
  - the archive pack takes public domain, CC0, CC BY and the Open Government Licence - Canada, never BY-SA or NC;
  - an archive caption loses its catalogue numbers and credit lines; its rows say who keeps it, its province is the
    place, and the dead or a child mark it graphic or child;
  - a Canadian road-sign drawing gets its sign number and its English meaning, and a French one gets none;
  - iNaturalist's "Québec" is matched to Quebec, and only CC0 and CC BY photos are taken;
  - the Commons specs carry ", Canada" places, and every pack has a limit;
  - a Canadian shelf barcode is told from a European one, a label in English and French is said only when the
    record says so;
  - the Montréal archive rows are in French with the archive's credit, "S/O" left out;
  - a canada.ca form page gives its title and the plain English PDF; a made-up blank PDF gives "What is this form?";
  - a recall page's product photos and alt texts are read, children's sleepwear recalls are left out;
  - the kit table's keys are unique and its groups known.

Run it from the repository's folder:   python3 -m pytest packs/test_canada.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import canada_packs as c  # noqa: E402
from test_us_modern import made_up_pdf  # noqa: E402


def test_province_in():
    """A province from its name or its old short form; none when two are named."""
    assert c.province_in("Main Street, Moose Jaw, Sask., 1912.") == "Saskatchewan"
    assert c.province_in("Rue Saint-Jean, Québec") == "Quebec"
    assert c.province_in("Halifax, N.S. and Saint John, N.B.") == ""
    assert c.province_in("A farm") == ""
    assert c.ca("Ontario") == "Ontario, Canada" and c.ca("") == "Canada"


def test_licences():
    """Public domain, CC0, CC BY and OGL-Canada are taken; share-alike and non-commercial are not."""
    for ok in ("Public domain", "PD-Canada", "CC0", "CC BY 4.0", "OGL-C", "Open Government Licence - Canada 2.0"):
        assert c.ca_free(ok), ok
    for no in ("CC BY-SA 4.0", "CC BY-NC 2.0", "OGL-C BY-SA", "", "Copyrighted"):
        assert not c.ca_free(no), no


def test_archive_caption_and_rows():
    """Catalogue numbers and credits go; the rows carry the keeper, the province and the marks."""
    text = ("Title: Main Street looking north, Moose Jaw, Sask., 1912. MIKAN 3301234. Library and Archives Canada, "
            "PA-012345")
    caption = c.archive_caption(text)
    assert "MIKAN" not in caption and "PA-012345" not in caption and "Library and Archives" not in caption
    assert caption.startswith("Main Street looking north, Moose Jaw")
    assert c.archive_caption("Aerial survey of beluga in Hudson Bay, August 2015. This metadata covers the "
                             "photographic data.") == "Aerial survey of beluga in Hudson Bay, August 2015."
    rows = c.archive_rows(caption, "Library and Archives Canada", "credit", text)
    assert rows[0]["place"] == "Saskatchewan, Canada" and rows[0]["question"] == c.DESCRIBE_Q
    assert rows[1] == {"question": c.KEPT_Q, "answer": "It is kept by Library and Archives Canada.",
                       "credit": "credit"}
    rows = c.archive_rows("Soldiers carry the wounded from the train at the station.", "LAC", "credit",
                          "the wounded")
    assert all(r["content"] == "graphic" for r in rows)
    rows = c.archive_rows("A girl skates on the frozen river in the town.", "LAC", "credit", "a girl skates")
    assert all(r.get("child") for r in rows)


def test_sign_meaning():
    """The sign number from the file name and the English meaning from the description; nothing from French."""
    assert c.ca_sign_meaning("File:Ontario Rb-1.svg", "Stop sign") == ("Rb-1", "Stop sign")
    assert c.ca_sign_meaning("File:Canada RA-1.svg", 'Sign reading "NO STOPPING"') == ("RA-1",
                                                                                       'it reads "NO STOPPING"')
    assert c.ca_sign_meaning("File:Québec P-10.svg", "Panneau d'arrêt du Québec") == ("P-10", "")
    assert c.ca_sign_meaning("File:Sign.svg", "") == ("", "")


def test_inaturalist():
    """Québec is matched to Quebec inside Canada (not Lake Ontario, not a US place); only CC0 and CC BY photos."""
    results = [{"id": 1, "name": "Québec", "admin_level": 20, "ancestor_place_ids": [6712]},
               {"id": 13336, "name": "Québec", "admin_level": 10, "ancestor_place_ids": [97394, 6712, 13336]}]
    assert c.inat_match("Quebec", results) == {"Quebec": 13336}
    assert c.inat_match("Ontario", [{"id": 1840, "name": "Ontario", "admin_level": 10,
                                     "ancestor_place_ids": [97394, 1, 48]}]) == {}
    obs = {"id": 5, "taxon": {"name": "Gavia immer", "preferred_common_name": "Common Loon", "id": 4626},
           "user": {"login": "someone"}, "photos": [{"id": 9, "license_code": "cc-by-nc", "url": "x/square.jpg"},
                                                    {"id": 10, "license_code": "cc-by", "url": "y/square.jpg"}]}
    name, url, rows = c.inat_item(obs, "Ontario", "What bird is this?")
    assert name == "inatca-10.jpg" and url == "y/large.jpg"
    assert rows[0]["answer"] == "This is a Common Loon (Gavia immer)." and rows[0]["place"] == "Ontario, Canada"
    assert c.inat_item(dict(obs, photos=[obs["photos"][0]]), "Ontario", "What bird is this?") is None


def test_specs_and_tables():
    """The specs' places end with Canada (or are left open for generic categories); every pack has a limit."""
    for spec in c.home_specs() + c.street_specs() + c.car_specs() + c.HOLIDAYS + c.GETTING_AROUND:
        assert spec["place"] in ("",) or spec["place"].endswith("Canada"), spec
    assert set(c.CANADA_PACKS) == set(c.CANADA_LIMITS)
    assert all(callable(v[0]) and v[1] for v in c.CANADA_PACKS.values())


def test_barcodes_and_labels():
    """A North American or GS1 Canada barcode is taken, a European one is not; English and French only when said."""
    import canada_sources as k
    assert k.ca_barcode("064200116176") and k.ca_barcode("0628915120096") and k.ca_barcode("7541234567890")
    assert not k.ca_barcode("3017620422003") and not k.ca_barcode("12345") and not k.ca_barcode("abc")
    assert k.bilingual_row({"languages_codes": {"en": 5, "fr": 4}}, {"credit": "c"})["answer"] == \
        "The label is in English and French."
    assert k.bilingual_row({"languages_codes": {"en": 5}}, {}) is None


def test_montreal_rows():
    """French title and description, "S/O" left out, the archive's credit and Montreal as the place."""
    import canada_sources as k
    text = ('"Titre","Description","Date","Cote","Fichier tif - 300 dpi","Fichier jpg - 200 dpi","Mention de crédits"\n'
            '"Rue Drummond","En direction Nord.",1928,"VM94,D4","http://x/a.tif","http://depot.example/jpeg/Z5.jpg",'
            '"Archives de la Ville de Montréal"\n'
            '"Parc Lafontaine","S/O","Décennie 1930","VM94,D2","","http://depot.example/jpeg/Z3.jpg",""\n')
    items = k.montreal_rows(text)
    assert [i[0] for i in items] == ["mtl-Z5.jpg", "mtl-Z5.jpg", "mtl-Z3.jpg", "mtl-Z3.jpg"]
    first = items[0][2]
    assert first["answer"] == "Rue Drummond. En direction Nord." and first["language"] == "fr"
    assert items[0][1].startswith("https://") and first["credit"].startswith("Archives de la Ville de Montréal")
    assert items[2][2]["answer"] == "Parc Lafontaine." and items[1][2]["place"] == "Montreal, Quebec, Canada"


def test_form_page_and_pdf():
    """A canada.ca form page gives its heading and its plain English PDF; a blank PDF gives the form rows."""
    import canada_sources as k
    page = ('<h1 property="name" id="wb-cont">TD1 2026 <span>Personal Tax Credits Return</span></h1>'
            '<a href="/content/dam/cra-arc/formspubs/pbg/td1/td1-fill-26e.pdf">fillable</a>'
            '<a href="/content/dam/cra-arc/formspubs/pbg/td1/td1-26f.pdf">français</a>'
            '<a href="/content/dam/cra-arc/formspubs/pbg/td1/td1-26e.pdf">PDF</a>')
    title, pdf = k.form_page_links(page)
    assert title == "TD1 2026 Personal Tax Credits Return"
    assert pdf == "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/td1/td1-26e.pdf"
    assert k.form_page_links("<h1>Nothing</h1>") == ("Nothing", "")
    pages = k.form_pictures(made_up_pdf(), title, pdf, "https://www.canada.ca/td1.html")
    name, data, rows = pages[0]
    assert data[:2] == b"\xff\xd8" and name == "cra-td1_26e-p1"
    questions = [r["question"] for r in rows]
    assert k.FORM_Q in questions and k.FILLED_Q in questions
    assert rows[0]["answer"].startswith("This is TD1 2026 Personal Tax Credits Return, a Canada Revenue Agency")
    assert "non-commercial" in rows[0]["credit"]


def test_recalls():
    """Product photos and their alt texts from a recall page; the product's name; sleepwear recalls left out."""
    import canada_sources as k
    page = ('<img src="/libraries/theme-gcweb/assets/sig-blk-en.svg" alt="Government of Canada" />'
            '<img class="x" data-src="/sites/default/files/styles/x_large/public/alert/recall/82796/Picture1.png?'
            'itok=R" src="data:image/svg+xml;x" alt="Front of product - FTVN Series Boiler"/>'
            '<img data-src="/sites/default/files/styles/x_large/public/alert/recall/82796/Picture2.png?itok=h" '
            'alt="Label on product"/>')
    pictures = k.recall_pictures(page)
    assert pictures == [("https://recalls-rappels.canada.ca/sites/default/files/styles/x_large/public/alert/recall/"
                         "82796/Picture1.png?itok=R", "Front of product - FTVN Series Boiler"),
                        ("https://recalls-rappels.canada.ca/sites/default/files/styles/x_large/public/alert/recall/"
                         "82796/Picture2.png?itok=h", "Label on product")]
    record = {"NID": "82796", "Title": "Residential gas boilers recalled", "Product": "Gas boilers.",
              "Issue": "Fire hazard", "URL": "https://recalls-rappels.canada.ca/en/alert-recall/x"}
    items = k.recall_rows(record, pictures)
    assert [i[2]["answer"] for i in items] == ["This is the FTVN Series Boiler.",
                                               "It was recalled in Canada for this reason: Fire hazard."]
    assert k.recall_product("Tahineh - 800 g - Front", record) == "the Tahineh"
    assert k.recall_product("Chili &amp; Lime Puffs front", record) == "the Chili & Lime Puffs"
    assert k.recall_product("Front of product", record) == "the Gas boilers"
    sleepwear = dict(record, Title="Children's sleepwear recalled", Product="Children's pyjamas")
    assert k.recall_rows(sleepwear, pictures) == []


def test_kit_table():
    """The kit entries: unique keys, known groups, picture-making only for collections without people."""
    import canada_sources as k
    keys = [s.key for s in k.CANADA_SOURCES]
    assert len(keys) == len(set(keys))
    assert {s.group for s in k.CANADA_SOURCES} <= {"share-alike", "noncommercial", "research"}
    assert k.CANADA_PICTURE_MAKING_OK <= set(keys)
    assert not set(keys) & set(c.CANADA_PACKS)
