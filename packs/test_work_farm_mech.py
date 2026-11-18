"""A self-test of the workplace, farm and building mechanical parsers (packs/work_farm_mech_packs.py and
training-kit/kit/work_farm_mech_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - the place is read from a category's name only for a US state, a Canadian province or the whole country, and
    "Where was this photo taken?" is asked only for a state or province;
  - a file is left out when its words name nudity, a child, an injury or accident, an old or museum machine, or (in
    the farm and building packs) a person;
  - a caption is used only when it is real English and says more than the file name;
  - a fixed-answer category gives its answer, and a caption-only category with no usable caption sets the picture
    aside for a description instead of using it;
  - the kit's share-alike entries leave out files by the same words.

Run it from the repository's folder:   python3 -m pytest packs/test_work_farm_mech.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import work_farm_mech_packs as w  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"


def test_category_place():
    """States, provinces and the two countries; not cities, not "by state"."""
    assert w.category_place("Tractors in Iowa") == "Iowa, USA"
    assert w.category_place("Barns in Washington (state)") == "Washington, USA"
    assert w.category_place("Barns in Ontario") == "Ontario, Canada"
    assert w.category_place("Factories in the United States") == "USA"
    assert w.category_place("Silos in Canada") == "Canada"
    assert w.category_place("Factories in Kansas City") == ""
    assert w.category_place("Tractors in the United States by state") == ""
    assert w.category_place("Grain dryers") == ""


def test_left_out_because():
    """The words that leave a file out, and people only where they are not allowed."""
    assert w.left_out_because("File:Barn.jpg", "A red barn by a field", people_ok=False) == ""
    assert "nudity" in w.left_out_because("File:X.jpg", "nude model in a barn", people_ok=True)
    assert "child" in w.left_out_because("File:X.jpg", "Boys driving a tractor", people_ok=True)
    assert "injury" in w.left_out_because("File:X.jpg", "Tractor rollover accident", people_ok=True)
    assert "1990" in w.left_out_because("File:X.jpg", "Antique tractor show", people_ok=True)
    assert "1990" in w.left_out_because("File:Combine 1952.jpg", "", people_ok=True)
    assert "person" in w.left_out_because("File:X.jpg", "A farmer checks his grain dryer", people_ok=False)
    assert w.left_out_because("File:X.jpg", "A worker drives a forklift", people_ok=True) == ""
    assert "1990" in w.left_out_because("File:Laborers near coal wharf - NARA - 524820.jpg", "", people_ok=True)
    assert "1990" in w.left_out_because("File:Spinning mill.jpg", "Photograph by Lewis Hine", people_ok=True)
    assert "person" in w.left_out_because("File:US Navy 1107 volunteer takes a sample.jpg", "", people_ok=False)
    assert "document" in w.left_out_because("File:Listing of material for a septic tank.jpg", "", people_ok=True)
    assert w.left_out_because("File:X.jpg", "Infantry vehicles in a warehouse", people_ok=True) == ""


def test_good_caption():
    """English captions that say more than the file name; not records, first-person stories or other languages."""
    assert w.good_caption("Grain bins on a farm near Ames, with an auger", "File:Bins.jpg")
    assert w.good_caption("Grain bins", "File:Grain bins.jpg") == ""
    assert w.good_caption("I took this at my uncle's farm", "File:X.jpg") == ""
    assert w.good_caption("Ein Traktor auf dem Feld mit der Egge", "File:X.jpg") == ""
    assert w.good_caption("Original digital file IMG_1234", "File:X.jpg") == ""
    assert w.good_caption("General notes: Use War and Conflict Number 202 when ordering a reproduction",
                          "File:X.jpg") == ""


def test_file_rows_fixed_answer_and_place():
    """The category's answer, the caption, and the state from the subcategory a file was found in."""
    sp = w.machine("Tractors in the United States by state", w.TRACTOR, 1)
    rows = w.file_rows(sp, "Tractors in Iowa", "File:T.jpg", CREDIT, "A green tractor pulling a planter in the spring")
    questions = [r["question"] for r in rows]
    assert questions == [w.MACHINE_Q, w.DESCRIBE_Q, w.WHERE_Q]
    assert rows[0]["answer"] == w.TRACTOR and rows[0]["place"] == "Iowa, USA"
    assert rows[2]["answer"] == "It was taken in Iowa, USA."
    assert rows[0]["facts"]["commons_category"] == "Tractors in Iowa"
    country = w.file_rows(w.thing("Silos in Canada", "This is a farm silo in Canada."), "", "File:S.jpg", CREDIT, "")
    assert [r["question"] for r in country] == [w.WHAT_Q]          # a whole country: no "where" question
    assert country[0]["place"] == "Canada"


def test_caption_only_and_set_aside(monkeypatch):
    """A caption-only category uses a good caption, and sets aside a free picture without one; a farm file naming a
    person is left out, not set aside."""
    build_packs.reset_needs()
    build_packs.CONSIDERED.clear()
    files = [("File:Field one.jpg", "Agriculture in Iowa"), ("File:Field two.jpg", "Agriculture in Iowa"),
             ("File:Field three.jpg", "Agriculture in Iowa")]
    entries = [("File:Field one.jpg", "https://upload.example/1.jpg", CREDIT,
                "Soybeans growing in long rows beside the gravel road in July", ""),
               ("File:Field two.jpg", "https://upload.example/2.jpg", CREDIT, "Field", ""),
               ("File:Field three.jpg", "https://upload.example/3.jpg", CREDIT,
                "A farmer stands beside his new grain bins in the evening", "")]
    monkeypatch.setattr(w, "spec_files", lambda s, sp, most_subcategories=60: files)
    monkeypatch.setattr(w, "free_entries", lambda s, titles: [e for e in entries if e[0] in titles])
    monkeypatch.setattr(w, "session", lambda: None)
    items = w.commons_items([w.caption_only("Agriculture in the United States")], 3, "farm", people_ok=False)
    assert [i[0] for i in items] == ["farm-Field_one.jpg"]
    rows = items[0][2]
    assert rows[0]["question"] == w.DESCRIBE_Q and rows[0]["answer"].startswith("Soybeans")
    assert rows[1] == {"question": w.WHERE_Q, "answer": "It was taken in Iowa, USA.", "credit": CREDIT,
                       "facts": {"commons_category": "Agriculture in Iowa"}, "place": "Iowa, USA"}
    assert [n["name"] for n in build_packs.NEEDS] == ["farm-Field_two.jpg"]
    assert build_packs.NEEDS[0]["place"] == "Iowa, USA" and build_packs.NEEDS[0]["licence"] == "CC BY 4.0"
    assert any("person" in c["reason"] for c in build_packs.CONSIDERED if c["name"] == "File:Field three.jpg")
    build_packs.reset_needs()


def test_is_free():
    """Open licences and open government licences in; share-alike, non-commercial and no-derivatives out."""
    for licence in ("CC0", "Public domain", "CC BY 2.0", "CC BY 4.0", "OGL-ON", "OGL-Canada-2.0", "OGL v3.0",
                    "No restrictions"):
        assert w.is_free(licence), licence
    for licence in ("CC BY-SA 4.0", "CC BY-NC 2.0", "CC BY-ND 4.0", "GFDL", "", "All rights reserved"):
        assert not w.is_free(licence), licence


def test_nrcs_rows():
    """The NRCS caption and the agency."""
    rows = w.nrcs_rows("Cover crops of cereal rye growing between corn rows in Iowa", CREDIT, "Iowa, USA")
    assert rows[0]["question"] == w.DESCRIBE_Q and rows[0]["place"] == "Iowa, USA"
    assert "US Department of Agriculture" in rows[1]["answer"]
    assert rows[2]["answer"] == "It was taken in Iowa, USA."
    assert w.nrcs_state("File:NRCSIA00016 - Iowa (2235)(NRCS Photo Gallery).jpg") == "Iowa, USA"
    assert w.nrcs_state("File:20200206-FPAC-ServiceCenter-0012 TONED.jpg") == ""
    assert "child" in w.left_out_because("File:X.jpg", "An elementary class plants a tree", people_ok=True)


def test_kit_share_alike_filters(monkeypatch):
    """The kit's share-alike entries leave out every row of a file whose words name a person (farm and building
    entry only), an accident or an old machine."""
    import work_farm_mech_sources as k
    made = [("a.jpg", "u1", {"question": k.WHAT_Q, "answer": "This is a gas furnace."}),
            ("a.jpg", "u1", {"question": "Describe", "answer": "A new gas furnace in a basement"}),
            ("b.jpg", "u2", {"question": k.WHAT_Q, "answer": "This is a gas furnace."}),
            ("b.jpg", "u2", {"question": "Describe", "answer": "A technician repairs his customer's furnace"}),
            ("c.jpg", "u3", {"question": "Describe", "answer": "Vintage furnace from 1925"})]
    monkeypatch.setattr(k, "commons_sa_items", lambda specs, cap, test, prefix, adults_only=False: list(made))
    farm = k.sa_items(k.FARM_MECH_SA, 10, 1, "x", people_ok=False)
    assert {i[0] for i in farm} == {"a.jpg"}
    work = k.sa_items(k.WORK_SA, 10, 1, "x", people_ok=True)
    assert {i[0] for i in work} == {"a.jpg", "b.jpg"}
    assert k.WORK_FARM_MECH_PICTURE_MAKING_OK == {"farm_mech_commons_sa"}
