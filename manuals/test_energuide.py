"""A self-test of the EnerGuide (Natural Resources Canada) reader of manuals/build_manuals.py, with a made-up
open.canada.ca answer and a made-up ZIP only: nothing is downloaded from the internet.

It checks that:
  - the ZIP files are found in an open.canada.ca package_show answer, with their English names;
  - a ZIP's data CSV (written in Windows-1252, as NRCan's are) gives brand, model and kind, each model once, with the
    Open Government Licence - Canada attribution as its source;
  - the home appliances category asks for EnerGuide files, and only names that the files really have.

Run it from the repository's folder:   python3 -m pytest manuals/test_energuide.py
"""

import io
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_manuals as B  # noqa: E402
import categories as C  # noqa: E402

PACKAGE = {"result": {"resources": [
    {"format": "ZIP", "url": "https://example.org/005_dishwashers_lave-vaisselle.zip",
     "name_translated": {"en": "DISHWASHERS", "fr": "LAVE-VAISSELLE"}},
    {"format": "ZIP", "url": "https://example.org/008_ranges_cuisinieres.zip", "name": "RANGES"},
    {"format": "HTML", "url": "https://example.org/about.html", "name": "About"}]}}


def made_up_zip():
    """A ZIP like NRCan's: a data CSV in Windows-1252 (an accented French label), a dictionary and an info file."""
    rows = ('"REC_REF_KEY","MODEL_NUM_1","BRAND_NAME","TYPE_LABEL_EN","TYPE_LABEL_FR"\r\n'
            '1001,"DW100X","Maplewood","Built-in","Encastré"\r\n'
            '1002,"DW100X","Maplewood","Built-in","Encastré"\r\n'
            '1003,"","Nameless","Portable","Portatif"\r\n'
            '1004,"DW200","Northern","Portable","Portatif"\r\n')
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("005_dishwashers/005_Data_Données.csv", rows.encode("cp1252"))
        z.writestr("005_dishwashers/005_Dictionary_Dictionnaire.csv", "Field Name,Type\r\n")
        z.writestr("005_dishwashers/005_Information.csv", "Filename\r\n")
    return out.getvalue()


def test_files():
    """The ZIP files and their English names; the web page is not one."""
    assert B.energuide_files(PACKAGE) == [("dishwashers", "https://example.org/005_dishwashers_lave-vaisselle.zip"),
                                          ("ranges", "https://example.org/008_ranges_cuisinieres.zip")]
    assert B.energuide_files({}) == []


def test_models():
    """Brand, model and kind from the data CSV, each model once, the rows without a model left out."""
    models = B.energuide_models(made_up_zip(), "dishwashers", 10)
    assert [(m["brand"], m["model"]) for m in models] == [("Maplewood", "DW100X"), ("Northern", "DW200")]
    first = models[0]
    assert first["name"] == "Maplewood DW100X (Built-in dishwashers)"
    assert first["barcodes"] == [] and first["manuals"] == [] and first["market"] == "Canada"
    assert "Open Government Licence - Canada" in first["source"]
    assert len(B.energuide_models(made_up_zip(), "dishwashers", 1)) == 1


def test_category():
    """The home appliances category asks for EnerGuide files and says their licence."""
    cat = C.CATEGORIES["home_appliances"]
    assert "dishwashers" in cat["energuide"] and "ranges" in cat["energuide"]
    assert "Open Government Licence - Canada" in cat["licence"]
