"""A self-test of the medicine, medical supply and veterinary parsers (packs/med_vet_packs.py and
training-kit/kit/med_vet_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - the owner's rule holds: only current items (a year before 2000, a decade, a century, "antique", "museum",
    "discontinued" ... leave a picture out; a dose such as "1000 mg" or "COVID-19" does not), Commons files dated
    before 2000 are left out, PHIL photos must be dated 2000 or later, and archive photographers are left out of the
    Open Images pack;
  - files are left out for a child, a patient, blood, an operation or (in the object packs) a person, but "blood
    glucose" and "blood pressure" are not taken for blood;
  - a medicine's answer says "This looks like ..." and ends with the safety line; an instrument gets "What is this
    instrument used for?"; a caption-only category with no usable caption sets the picture aside;
  - the dental instrument names match the data set's 22 classes; Open Images rows use the right grammar and leave out
    probable patients; VOA files naming a wire agency are left out;
  - the kit's DailyMed titles become careful answers, only package pictures are taken, and the Open Food Facts
    supplements keep North American barcodes only.

Run it from the repository's folder:   python3 -m pytest packs/test_med_vet.py
"""

import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import med_vet_packs as m  # noqa: E402

CREDIT = "File:X.jpg by someone, CC BY 4.0, https://commons.wikimedia.org/wiki/File:X.jpg"


def test_current_items_only():
    """The owner's rule: old words leave a picture out; doses and COVID-19 do not."""
    for old in ("Surgical instruments, 1950s", "A 19th century scalpel", "Antique pill box", "Scalpel, 1885",
                "Museum display of forceps", "Accession number 1992.3.4", "Vintage first aid kit",
                "This medicine was discontinued in 2019", "Historical stethoscope", "Inhaler from 1996",
                "File:Pill organiser (AM 2017.92.14-13).jpg"):
        assert m.is_old(old), old
    for new in ("Paracetamol 1000 mg tablets", "Ibuprofen 1200mg", "COVID-19 vaccine vial", "Tylenol box, 2015",
                "Box of 100 tablets", "Insulin pen 300 units"):
        assert not m.is_old(new), new
    assert m.OLD_CATEGORY.search("Ointment tins") and m.OLD_CATEGORY.search("Patent medicines")
    assert not m.OLD_CATEGORY.search("Ointments")


def test_current_only_dates(monkeypatch):
    """Commons files dated before 2000 are left out; undated ones are kept."""
    pages = {"1": {"title": "File:Old.jpg", "imageinfo": [{"extmetadata": {"DateTimeOriginal": {"value": "1987"}}}]},
             "2": {"title": "File:New.jpg", "imageinfo": [{"extmetadata": {"DateTimeOriginal": {"value": "2019"}}}]},
             "3": {"title": "File:Undated.jpg", "imageinfo": [{"extmetadata": {}}]}}
    monkeypatch.setattr(m, "commons_get", lambda s, params: {"query": {"pages": pages}})
    monkeypatch.setattr(m, "session", lambda: None)
    monkeypatch.setattr(m.time, "sleep", lambda s: None)
    items = [(f"{n}.jpg", "u", [{"credit": f"x, CC0, https://commons.wikimedia.org/wiki/File:{n}.jpg"}])
             for n in ("Old", "New", "Undated")]
    assert [i[0] for i in m.current_only(items)] == ["New.jpg", "Undated.jpg"]


def test_left_out_because():
    """Children, patients, blood, operations and (unless allowed) people; not "blood glucose"."""
    assert m.left_out_because("File:Pill organizer.jpg", "A weekly pill organizer on a table") == ""
    assert m.left_out_because("File:Meter.jpg", "A blood glucose meter with test strips") == ""
    assert m.left_out_because("File:Cuff.jpg", "A blood pressure cuff and gauge") == ""
    assert "child" in m.left_out_because("File:X.jpg", "Inhaler for a child with asthma")
    assert "child" in m.left_out_because("File:X.jpg", "Pediatric stethoscope")
    assert "patient" in m.left_out_because("File:X.jpg", "IV drip beside a patient")
    assert "blood" in m.left_out_because("File:X.jpg", "Bloody bandage")
    assert "operation" in m.left_out_because("File:X.jpg", "Scalpel during surgery in progress")
    assert "person" in m.left_out_because("File:X.jpg", "A nurse holding a syringe")
    assert m.left_out_because("File:X.jpg", "A nurse holding a syringe", people_ok=True) == ""
    assert "old" in m.left_out_because("File:X.jpg", "Antique surgical kit")
    assert m.left_out_because("File:X.jpg", "Willis Conover at VOA in 1960", people_ok=True, current=False) == ""
    assert "nudity" in m.left_out_because("File:X.jpg", "nude model with bandages", people_ok=True)


def test_file_rows():
    """A medicine says "looks like" and the safety line; an instrument says what it is used for."""
    med = m.medicine("Ibuprofen", m.looks_like("ibuprofen", "a medicine for pain, fever and swelling"))
    rows = m.file_rows(med, "", "File:Ibu.jpg", CREDIT, "")
    assert rows[0]["question"] == m.MEDICINE_Q
    assert rows[0]["answer"] == ("This looks like ibuprofen, a medicine for pain, fever and swelling. Check the "
                                 "packaging or ask a pharmacist to be sure.")
    vet = m.medicine("Veterinary drugs", "This looks like a veterinary medicine.", vet=True)
    assert m.file_rows(vet, "", "File:V.jpg", CREDIT, "")[0]["answer"].endswith("ask a vet or pharmacist to be sure.")
    inst = m.instrument("Scalpels", "a scalpel", "A scalpel is a very sharp small knife.")
    rows = m.file_rows(inst, "", "File:S.jpg", CREDIT, "A disposable scalpel with a blue plastic handle on a tray")
    assert [r["question"] for r in rows] == [m.INSTRUMENT_Q, m.USE_Q, m.DESCRIBE_Q]
    assert rows[0]["answer"] == "This is a scalpel." and rows[0]["facts"]["commons_category"] == "Scalpels"
    assert m.file_rows(m.caption_only("Medical supplies"), "", "File:M.jpg", CREDIT, "Box") == []


def test_commons_items_and_set_aside(monkeypatch):
    """A fixed-answer category gives its rows; an old or personal file is left out, not set aside; a caption-only
    category's free file without a caption is set aside."""
    build_packs.reset_needs()
    build_packs.CONSIDERED.clear()
    files = {"Pill organizers": [("File:Organizer one.jpg", "Pill organizers"),
                                 ("File:Organizer two.jpg", "Pill organizers"),
                                 ("File:Organizer three.jpg", "Pill organizers")],
             "Medical supplies": [("File:Supply box.jpg", "Medical supplies")]}
    entries = {"File:Organizer one.jpg": "A seven-day pill organizer with blue lids",
               "File:Organizer two.jpg": "Antique pill box from the 1890s",
               "File:Organizer three.jpg": "A woman fills her pill organizer",
               "File:Supply box.jpg": "Box"}
    monkeypatch.setattr(m, "spec_files", lambda s, sp, most_subcategories=60: files[sp["category"]])
    monkeypatch.setattr(m, "free_entries", lambda s, titles: [(t, f"https://upload.example/{i}.jpg", CREDIT,
                                                               entries[t], "") for i, t in enumerate(titles)])
    monkeypatch.setattr(m, "session", lambda: None)
    specs = [m.thing("Pill organizers", "This is a pill organizer."), m.caption_only("Medical supplies")]
    items = m.commons_items(specs, 4, "medsup")
    assert [i[0] for i in items] == ["medsup-Organizer_one.jpg"]
    assert items[0][2][0] == {"question": m.WHAT_Q, "answer": "This is a pill organizer.", "credit": CREDIT,
                              "facts": {"commons_category": "Pill organizers"}}
    assert [n["name"] for n in build_packs.NEEDS] == ["medsup-Supply_box.jpg"]
    reasons = {c["name"]: c["reason"] for c in build_packs.CONSIDERED}
    assert "old" in reasons["File:Organizer two.jpg"] and "person" in reasons["File:Organizer three.jpg"]
    build_packs.reset_needs()


def test_dental():
    """Every class of the data set's data.yaml has a name and a use; the per-instrument zips are recognised."""
    classes = ['Aji bone cutter', 'Andrew Tongue Depressor', 'Angled artery forceps', 'Cross Bar elevator',
               'Curved gum scissors', 'Dental Aspirating Syringe', 'Dental elevator', 'Frazier Suction Tube',
               'Mandibular Cowhorn forceps', 'Mandibular anterior extraction forceps',
               'Mandibular lower incisors forceps', 'Mandibular lower molar forceps',
               'Maxillary anterior canine forceps', 'Maxillary molar dental extraction forceps',
               'Maxillary upper incisors forceps', 'Maxillary upper molar forceps',
               'Maxillary upper molars extraction forceps', 'Mayo Hegar needle holder', 'Orthodontic ligature cutter',
               'Straight artery forceps', 'Straight tweezers', 'Wire Orthopedic Cutter']
    assert sorted(m.DENTAL_USES) == sorted(classes)
    assert m.dental_class("Dental Elevator.zip") == "Dental elevator"
    assert m.dental_class("Group images.zip") == ""
    rows = m.dental_rows("Mayo Hegar needle holder")
    assert rows[0] == {"question": m.INSTRUMENT_Q, "answer": "This is a Mayo-Hegar needle holder.",
                       "credit": m.DENTAL_CREDIT}
    assert rows[1]["question"] == m.USE_Q and "stitches" in rows[1]["answer"]


def test_open_images_rows():
    """Plural grammar, the general label left out, no-answers, and probable patients left out."""
    rng = random.Random(1)
    rows = m.oi_medical_rows({"Medical glove": 1, "Medical equipment": 1, "Syringe": 1}, rng)
    assert rows[0] == {"question": m.MEDICAL_Q, "answer": "I can see medical gloves and a syringe."}
    assert rows[1] == {"question": "Are there medical gloves in this picture?",
                       "answer": "Yes, there are medical gloves in this picture."}
    no = m.oi_medical_rows({"Stethoscope": 1, "Scalpel": 0}, random.Random(0))
    assert {"question": "Is there a scalpel in this picture?",
            "answer": "No, I can't see a scalpel in this picture."} in no or len(no) == 2
    assert m.oi_medical_rows({"Syringe": 1}, rng) == []                     # only a label other packs ask about
    assert m.oi_medical_rows({"Stretcher": 1, "Man": 1}, rng) == []         # probably a patient
    assert m.oi_medical_rows({"Stretcher": 1}, rng)
    assert m.OLD_SOURCE.search("Naval History & Heritage Command") and not m.OLD_SOURCE.search("Colin Dunn")


def test_phil_left_out():
    """PHIL: public domain, dated 2000 or later, a supply named, not a lab animal or a patient."""
    base = {"public": True, "year": "2013", "caption": "This image depicts two N95 respirators on a table."}
    assert m.phil_left_out(base) == ""
    assert "2000" in m.phil_left_out(dict(base, year="1995"))
    assert "2000" in m.phil_left_out(dict(base, year=""))
    assert "public" in m.phil_left_out(dict(base, public=False))
    assert "supply" in m.phil_left_out(dict(base, caption="This image depicts a meeting of the team."))
    assert "animal" in m.phil_left_out(dict(base, caption="A syringe used to inject a mouse."))
    assert "patient" in m.phil_left_out(dict(base, caption="A nurse gives a patient a vaccine with a syringe."))
    assert m.phil_caption("This image depicts two N95 respirators, one white and one blue.").startswith("Two N95")


def test_voa():
    """VOA files naming a wire agency are left out."""
    assert m.voa_not_own("File:X.jpg", "Crowds at the convention (AP Photo)")
    assert m.voa_not_own("File:X.jpg", "Photo by Reuters")
    assert m.voa_not_own("File:Debate.jpg", "VOA's Sean Maroney at the convention") == ""
    assert m.voa_caption("From the #DemConvention floor -- quiet before the crush. @VOANews.") == \
        "From the DemConvention floor, quiet before the crush."


def test_kit_dailymed():
    """DailyMed titles become careful answers; only package pictures are taken."""
    import med_vet_sources as k
    assert k.dailymed_title("OZIPCO BROAD SPECTRUM DEWORMER (FENBENDAZOLE) POWDER [FAST SOLD LLC]") == \
        ("Ozipco Broad Spectrum Dewormer", "fenbendazole", "powder", "Fast Sold LLC")
    assert k.dailymed_title("METOPROLOL TARTRATE TABLET, FILM COATED [PD-RX PHARMACEUTICALS, INC.]")[2] == \
        "tablet, film coated"
    assert k.dailymed_title("NO MAKER HERE") is None
    answer = k.dailymed_answer("VETA-K1 (PHYTONADIONE) SOLUTION [BIMEDA INC.]", "a prescription animal medicine",
                               vet=True)
    assert answer == ("This looks like the package or label of Veta-K1 (phytonadione), solution: a prescription "
                      "animal medicine from Bimeda Inc. Check the packaging or ask a vet or pharmacist to be sure.")
    media = [{"mime_type": "image/jpeg", "name": "fenbendazole-structure.jpg", "url": "a"},
             {"mime_type": "image/jpeg", "name": "ozipco-powder-carton.jpg", "url": "b"}]
    assert k.label_picture(media)["url"] == "b"
    assert k.label_picture(media[:1]) is None
    assert k.left_out("PERSONAL LUBRICANT (GLYCERIN) GEL [X INC]", people_ok=True)
    assert k.COSMETIC.search("HAIR DYE 5N NATURAL BROWN (P-AMINOPHENOL) LIQUID [X]")
    assert not k.COSMETIC.search("IBUPROFEN TABLET, FILM COATED [X]")
    assert k.MED_VET_PICTURE_MAKING_OK == {s.key for s in k.MED_VET_SOURCES}


def test_kit_supplements_and_sa(monkeypatch):
    """North American barcodes only, protein powders out; the share-alike entry drops files by their words."""
    import med_vet_sources as k
    assert k.north_american_barcode("012345678905") and k.north_american_barcode("0754000000001")
    assert not k.north_american_barcode("3017620422003")
    hit = {"code": "012345678905", "product_name": "Vitamin D3 1000 IU", "brands": "Brand", "quantity": "100 tablets",
           "images": {"front_en": {"rev": "3"}}, "categories_tags": ["en:dietary-supplements"]}
    rows = k.supplement_rows(hit, "a dietary supplement", "Canada")
    assert [r[2]["question"] for r in rows] == [k.PRODUCT_Q, k.KIND_Q] and rows[0][2]["place"] == "Canada"
    assert k.supplement_rows(dict(hit, product_name="Whey protein"), "a dietary supplement", "USA") == []
    assert k.supplement_rows(dict(hit, product_name="Sports Hydration"), "a dietary supplement", "USA") == []
    assert k.supplement_rows(dict(hit, code="3017620422003"), "a dietary supplement", "USA") == []
    made = [("a.jpg", "u1", {"question": k.WHAT_Q, "answer": "This is a syringe."}),
            ("b.jpg", "u2", {"question": k.WHAT_Q, "answer": "This is a syringe."}),
            ("b.jpg", "u2", {"question": "Describe", "answer": "A nurse holds a syringe"}),
            ("c.jpg", "u3", {"question": "Describe", "answer": "Antique syringe from 1900"})]
    monkeypatch.setattr(k, "commons_sa_items", lambda specs, cap, test, prefix, adults_only=False: list(made))
    assert {i[0] for i in k.sa_items(k.MED_VET_SA, 10, 1, "x")} == {"a.jpg"}
