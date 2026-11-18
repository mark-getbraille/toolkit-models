"""A self-test of the household device parsers (packs/device_packs.py and training-kit/kit/device_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - a Wikidata model's maker is said plainly ("Sony Group" -> "Sony"), its kind comes from Wikidata's own class when
    that is more telling ("smartphone model series" -> "smartphone"), and its rows are "What is this?", "What make and
    model is this?" and, only with a year, "About when was this made?";
  - a file of a model's box, insides or controller, or one whose words name a person, is left out, but a VCR with a
    tape in it is kept;
  - a Commons device file gets the category's answer, its own caption only when it says more than the file name, and
    "child" when its words name a child;
  - an NMAH record is read as a household device only from its object type (not prints and photographs of one), a
    patent model is said to be one, and a free record with too short a description is set aside for a description;
  - the kit's share-alike answers and CO3D's middle frames are made the same way.

Run it from the repository's folder:   python3 -m pytest packs/test_devices.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import device_packs as d  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"


def subject(label, kinds=(), makers=(), brands=(), starts=(), kind="videocassette recorder (VCR)"):
    """A made-up Wikidata model, as culture_packs.subjects gives one."""
    return {"id": "Q1", "label": label, "kindLabel": list(kinds), "makerLabel": list(makers),
            "brandLabel": list(brands), "start": list(starts), "kind": kind}


def test_company_and_maker():
    """Company endings are left out, and a maker is said only when Wikidata gives exactly one."""
    assert d.company("Sony Group") == "Sony"
    assert d.company("Canon Inc.") == "Canon"
    assert d.company("Matsushita Electric Industrial Co., Ltd.") == "Matsushita Electric Industrial"
    assert d.maker_of(subject("X", makers=["Sony Group"])) == "Sony"
    assert d.maker_of(subject("X", makers=["A Corp", "B Corp"], brands=["Brandy"])) == "Brandy"
    assert d.maker_of(subject("X", makers=["A Corp", "B Corp"])) == ""


def test_kind_words():
    """Wikidata's own class is used when it is more telling; brand names and "product model" are not kinds."""
    phone = subject("iPhone 4S", kinds=["iPhone", "smartphone model series"])
    assert d.kind_words(phone, "smartphone") == "smartphone"
    camera = subject("Canon EOS 600D", kinds=["digital single-lens reflex camera model"])
    assert d.kind_words(camera, "digital camera") == "digital single-lens reflex camera"
    cinema = subject("Panavision Genesis", kinds=["digital movie camera"])
    assert d.kind_words(cinema, "camcorder") == "digital movie camera"
    vcr = subject("JVC HR-3300", kinds=["product model"])
    assert d.kind_words(vcr, "videocassette recorder (VCR)") == "videocassette recorder (VCR)"


def test_model_rows():
    """The three questions, the maker said once, and no date question without a year."""
    rows = d.model_rows(subject("JVC HR-3300", makers=["JVC"], starts=["1976-09-09T00:00:00Z"]))
    assert rows[0]["answer"] == ("This is a JVC HR-3300, a videocassette recorder (VCR). This model first came out "
                                 "in 1976.")
    assert rows[1] == {"question": d.MAKE_Q, "answer": "It is a JVC HR-3300."}
    assert rows[2]["question"] == d.WHEN_Q and "1976" in rows[2]["answer"]
    rows = d.model_rows(subject("Hermes Baby", makers=["Paillard"], kind="typewriter"))
    assert rows[0]["answer"] == "This is a Hermes Baby, a typewriter made by Paillard."
    assert [r["question"] for r in rows] == [d.WHAT_Q, d.MAKE_Q]
    rows = d.model_rows(subject("IBM Selectric typewriter", makers=["IBM"], kind="typewriter"))
    assert rows[0]["answer"] == "This is an IBM Selectric typewriter."
    rows = d.model_rows(subject("Walkman X", makers=["Sony"], starts=["2040-01-01T00:00:00Z"], kind="boombox"))
    assert len(rows) == 2                                           # a year after now is not a date


def test_device_pictures_left_out():
    """Boxes, insides, controllers and people are left out; a tape in the machine is not."""
    vcr = subject("JVC HR-3300", makers=["JVC"])
    assert d.device_picture_rows(vcr, "File:JVC HR-3300 with box.jpg", "") == []
    assert d.device_picture_rows(vcr, "File:JVC HR-3300 inside.jpg", "") == []
    assert d.device_picture_rows(vcr, "File:Xbox controller.jpg", "") == []
    assert d.device_picture_rows(vcr, "File:VCR.jpg", "A man repairs a video recorder.") == []
    assert d.device_picture_rows(vcr, "File:JVC HR-3300 front.jpg", "A VCR with a tape half inserted.")


def test_commons_rows():
    """The category's answer, the caption only when it says more than the file name, and the child mark."""
    rows = d.commons_rows("File:Panasonic NV-J35.jpg", "Panasonic VHS recorder with a tape half inserted.",
                          "This is a VHS video recorder (VCR).", CREDIT)
    assert [r["question"] for r in rows] == [d.WHAT_Q, build_packs.ALT_TEXT]
    assert not any(r.get("child") for r in rows)
    assert len(d.commons_rows("File:Old fax machine.jpg", "Old fax machine", "This is a fax machine.", CREDIT)) == 1
    assert d.commons_rows("File:Mower.jpg", "A woman mowing the lawn.", "This is a lawn mower.", CREDIT) == []
    # A caption in another language is not used as a description; an Anefo photo is already the anefo pack.
    assert len(d.commons_rows("File:Semafoon.jpg", "Beschrijving : Semafoon officieel van de PTT", "This is a pager.",
                              CREDIT)) == 1
    assert d.commons_rows("File:Semafoon, Bestanddeelnr 916-8899.jpg", "", "This is a pager.", CREDIT) == []
    # A file whose words name a child is left out altogether (PERSON names children too).
    assert d.commons_rows("File:Kitchen.jpg", "A toaster oven in the children's kitchen.", "This is a toaster oven.",
                          CREDIT) == []


def test_nmah_kind_and_answer():
    """Object types name the device; prints of a device are not one; a patent model is said to be one."""
    assert d.nmah_kind("sewing machine patent model | Patent Model") == ("a sewing machine", True)
    assert d.nmah_kind("heater, sad iron") == ("an iron (for clothes)", False)
    assert d.nmah_kind("cyanotype") == ("", False)
    assert d.nmah_kind("lithograph | sewing machine") == ("", False)
    assert d.nmah_kind("mixer, drink, bow-drill") == ("", False)
    assert d.nmah_title_answer("Toaster", "a toaster", False) == "This is a toaster."
    assert d.nmah_title_answer("1851 - Isaac Singer's Sewing Machine Patent Model", "a sewing machine", True) == (
        "This is a sewing machine patent model (a small working model made for a patent), catalogued by the museum "
        "as \"1851 - Isaac Singer's Sewing Machine Patent Model\".")


def nmah_record(description):
    """A made-up NMAH record of a toaster with a CC0 picture."""
    return {"id": "edanmdm-nmah_1", "title": "Electric Toaster", "content": {
        "descriptiveNonRepeating": {"record_link": "https://n2t.net/ark:/65665/ng0", "online_media": {"media": [
            {"type": "Images", "content": "https://ids.si.edu/ids/deliveryService?id=X", "usage": {"access": "CC0"}}]}},
        "freetext": {"objectType": [{"content": "toaster"}], "date": [{"label": "date made", "content": "ca 1925"}],
                     "place": [{"label": "place made", "content": "United States: Minnesota, Minneapolis"}],
                     "notes": [{"label": "Description", "content": description}]}}}


def test_nmah_rows_and_set_aside():
    """A described record gives three rows; one with too short a description is set aside, not lost."""
    build_packs.reset_needs()
    got = d.nmah_device_rows(nmah_record("This two-slice electric toaster has hinged doors on each side that turn "
                                         "the bread when opened, and a nickel-plated body."))
    assert got is not None
    pictures, rows = got
    assert pictures == ["https://ids.si.edu/ids/deliveryService?id=X&max=2048"]
    assert [r["question"] for r in rows] == [d.WHAT_Q, build_packs.MUSEUM, d.WHEN_Q]
    assert rows[2]["answer"] == "The museum dates it around 1925."
    assert d.nmah_device_rows(nmah_record("A toaster.")) is None
    assert len(build_packs.NEEDS) == 1 and build_packs.NEEDS[0]["category"] == "open"
    build_packs.reset_needs()


def test_kit_answers_and_frames():
    """The kit's share-alike model answers and CO3D's middle frame of each video."""
    import sources  # noqa: F401 - loaded first, as the kit's files expect
    import device_sources as k
    rows = k.model_answers("Sony WM-2", "portable cassette player", ["Sony Group"], {"1983", "1981"})
    assert rows[0] == (k.WHAT_Q, "This is a Sony WM-2, a portable cassette player. This model first came out in "
                                 "1981.")
    assert rows[1] == (k.MAKE_Q, "It is a Sony WM-2.")
    assert k.model_answers("Hermes Baby", "typewriter", ["Paillard"], set())[0][1] == \
        "This is a Hermes Baby, a typewriter made by Paillard."
    names = [f"toaster/1_2_3/images/frame00000{n}.jpg" for n in (1, 2, 3)] + ["toaster/1_2_3/masks/frame000002.png",
                                                                             "toaster/1_2_3/pointcloud.ply"]
    assert k.co3d_frames(names) == {"toaster/1_2_3": "toaster/1_2_3/images/frame000002.jpg"}
    assert k.wd_year("1981-07-01T00:00:00Z") == "1981" and k.wd_year("2090-01-01T00:00:00Z") == ""


def test_english_captions_only():
    """A file caption in Italian is left out; the picture and its other rows stay."""
    entries = [("a.jpg", b"x", {"question": d.WHAT_Q, "answer": "This is an Olivetti ET Personal 540, a typewriter."}),
               (None, None, {"question": "Describe this picture.", "file": "pictures/a.jpg",
                             "answer": "La macchina da scrivere elettronica Olivetti ET Personal 540 chiusa."}),
               (None, None, {"question": "Describe this picture.", "file": "pictures/a.jpg",
                             "answer": "An Olivetti electronic typewriter with its cover closed."})]
    kept = d.english_captions_only(entries)
    assert len(kept) == 2 and kept[0][1] == b"x" and kept[1][2]["answer"].startswith("An Olivetti")
