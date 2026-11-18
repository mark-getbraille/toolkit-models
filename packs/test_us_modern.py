"""A self-test of the modern-America parsers (packs/us_modern_packs.py and training-kit/kit/us_modern_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - an agency caption loses its credit line, web address and programme note, and a photo's year is read;
  - a form's name comes from its PDF title, the words at the top are cut to a short line, and a made-up blank PDF
    drawn by pypdfium2 gives "What is this form?", "Is this form filled in?" and "What does it say at the top?";
  - a control gets "What does the display or dial show?" only when its own description gives a reading;
  - school graduations, child-marked graduation photos and hospital photos naming a patient are left out;
  - ImageInWords rows use the human description, never the machine one, and mark a child;
  - a C3PI pill record becomes "This is Strattera 10 mg (atomoxetine) ..." with its imprint, colour and shape.

Run it from the repository's folder:   python3 -m pytest packs/test_us_modern.py
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import us_modern_packs as m  # noqa: E402


def test_agency_caption():
    """Credit lines, web addresses and programme notes are taken out of an agency caption."""
    text = ("Beginning farmer Ana Lopez checks her tomatoes in Davis, Calif., July 12, 2016. USDA photo by Lance "
            "Cheung. For more information visit www.usda.gov")
    assert m.agency_caption(text) == "Beginning farmer Ana Lopez checks her tomatoes in Davis, Calif., July 12, 2016."
    assert m.agency_caption("https://www.flickr.com/x #USDA") == ""
    assert m.photo_year({"DateTimeOriginal": {"value": "2016-07-12 10:01:00"}}) == 2016
    assert m.photo_year({}) == 0


def test_agency_rows_marks():
    """An agency photo naming the injured is marked graphic; one naming a child is marked child."""
    rows = m.agency_rows("A FEMA worker talks with residents next to injured neighbours.", "FEMA", "credit",
                         "injured neighbours")
    assert all(r["content"] == "graphic" for r in rows)
    rows = m.agency_rows("A girl eats lunch at a summer meals site.", "USDA", "credit", "a girl eats lunch")
    assert all(r.get("child") for r in rows)


def test_form_name_and_top():
    """A form's name from the PDF's title and subject, and a short line from the top of the page."""
    assert m.form_name("2026 Form W-4", "Employee's Withholding Certificate", "") == \
        "IRS Form W-4 for 2026, Employee's Withholding Certificate"
    assert m.form_name("Form 1099-NEC (Rev. December 2026)", "Nonemployee Compensation", "") == \
        "IRS Form 1099-NEC, Nonemployee Compensation"
    assert m.form_name("1490S-Patient's Request", "", "Form CMS-1490S") == "Form CMS-1490S"
    assert m.top_words("Form W-4\r\n2026\r\nEmployee's Withholding Certificate\r\n") == \
        "Form W-4 2026 Employee's Withholding Certificate"
    assert m.top_words("Page\r\n") == ""
    assert len(m.top_words(" ".join(["word"] * 80))) < 400


def made_up_pdf():
    """A one-page blank PDF with a title, made with pypdfium2 (no download)."""
    import pypdfium2 as pdfium
    import pypdfium2.raw as raw
    doc = pdfium.PdfDocument.new()
    page = doc.new_page(612, 792)
    font = raw.FPDFText_LoadStandardFont(doc, b"Helvetica")
    text = raw.FPDFPageObj_NewTextObj(doc, b"Helvetica", 18.0)
    words = "Form W-4 Employee Withholding Certificate"
    buffer = (words + "\0").encode("utf-16-le")
    raw.FPDFText_SetText(text, (raw.FPDF_WCHAR * (len(buffer) // 2)).from_buffer_copy(buffer))
    raw.FPDFPageObj_Transform(text, 1, 0, 0, 1, 50, 740)
    raw.FPDFPage_InsertObject(page, text)
    raw.FPDFPage_GenerateContent(page)
    del font
    out = io.BytesIO()
    doc.save(out)
    page.close()
    doc.close()
    return out.getvalue()


def test_form_pages():
    """A blank PDF gives one picture with the form questions (skipped where pypdfium2 is not installed)."""
    import pytest
    pytest.importorskip("pypdfium2")
    pages = m.form_pages(made_up_pdf(), "https://www.irs.gov/pub/irs-pdf/fw4.pdf", m.IRS_AGENCY, "IRS Form W-4")
    assert len(pages) == 1
    name, data, rows = pages[0]
    assert name == "form-fw4-p1.jpg" and data[:2] == b"\xff\xd8"
    questions = [r["question"] for r in rows]
    assert questions[:2] == [m.FORM_Q, m.FILLED_Q]
    assert rows[0]["answer"].startswith("This is IRS Form W-4, from the Department of the Treasury")
    assert any(r["question"] == m.TOP_Q and "Withholding" in r["answer"] for r in rows)


def test_readings_only_when_said():
    """A reading question only when the control's own description gives one."""
    with_text = [{"question": m.WHAT_Q, "answer": "This is an electric oven.", "credit": "c"},
                 {"question": m.DESCRIBE_Q, "answer": "An oven control panel. The oven is set to 350 degrees.",
                  "credit": "c"}]
    without = [{"question": m.WHAT_Q, "answer": "This is an electric oven.", "credit": "c"},
               {"question": m.DESCRIBE_Q, "answer": "A white oven in a small kitchen.", "credit": "c"}]
    out = m.with_readings([("a.jpg", "u1", with_text), ("b.jpg", "u2", without)])
    assert out[0][2][-1] == {"question": m.READING_Q, "answer": "The oven is set to 350 degrees.", "credit": "c",
                             "facts": {}}
    assert all(r["question"] != m.READING_Q for r in out[1][2])


def test_graduations_and_hospitals():
    """School graduations and child-marked graduation photos are left out; so are hospital photos naming a
    patient."""
    def item(name, category, answer, child=False):
        row = {"question": m.HAPPENING_Q, "answer": answer, "facts": {"commons_category": category}}
        return (name, "u-" + name, [dict(row, child=True) if child else row])
    items = [item("a", "Graduation ceremonies in the United States", "A graduation."),
             item("b", "High school graduations in Texas", "A graduation."),
             item("c", "Graduation ceremonies in the United States", "A graduation.", child=True),
             item("d", "Parades in the United States", "A parade.", child=True)]
    assert [i[0] for i in m.adult_graduations(items)] == ["a", "d"]
    rooms = [item("e", "Hospital rooms", "An empty hospital room."),
             item("f", "Hospital rooms", "A patient in a hospital bed."),
             item("g", "Post offices in the United States", "A post office with patients waiting.")]
    assert [i[0] for i in m.no_patients(rooms)] == ["e", "g"]


def test_iiw_rows():
    """ImageInWords: the human description and object descriptions; never the machine text; children marked."""
    record = {"image/key": "aar_test_1", "IIW": "A small girl in a red coat stands beside a wooden fence " * 3,
              "IIW-P5B": "MACHINE TEXT", "objects": [{"label": "Wooden fence", "description":
                                                      "A low wooden fence with peeling paint runs left to right."}]}
    rows = m.iiw_rows(record)
    assert rows[0]["question"] == build_packs.DETAILED and "MACHINE" not in json.dumps(rows)
    assert rows[1]["question"] == "Describe the wooden fence in this picture."
    assert all(r.get("child") for r in rows)
    assert m.iiw_rows({"image/key": "x", "IIW": "Too short."}) == []


def test_c3pi():
    """A C3PI record becomes a pill answer and an imprint answer."""
    import us_modern_sources as k
    xml = b"""<?xml version="1.0" encoding="ISO-8859-1"?><MedicosConsultants><ImageExport><Image>
      <NDC11>00002322730</NDC11><LabeledBy>ELI LILLY AND COMPANY</LabeledBy><GenericName>ATOMOXETINE</GenericName>
      <ProprietaryName>STRATTERA</ProprietaryName><File><Name>AB!C.JPG</Name><Type>JPG</Type><Size>200000</Size>
      </File><Class>C3PI_Test</Class><RatingImprint>Clear</RatingImprint><Imprint>Lilly;3227;Lilly;3227</Imprint>
      <ImprintType>PRINTED</ImprintType><Color>BLUE</Color><Color>WHITE</Color><Shape>CAPSULE</Shape></Image>
      <Image><NDC11>1</NDC11><File><Name>X.CR2</Name><Type>CR2</Type><Size>1</Size></File>
      <Class>C3PI_Reference</Class></Image></ImageExport></MedicosConsultants>"""
    records = k.c3pi_records(xml)
    assert records[0]["Color"] == ["BLUE", "WHITE"] and records[0]["FileName"] == "AB!C.JPG"
    rows = k.c3pi_rows(records[0], "PillProjectDisc1", {"AB!C.JPG": "STRATTERA 10MG"})
    assert rows[0][1] == k.C3PI + "PillProjectDisc1/images/AB!C.JPG"
    assert rows[0][2]["answer"] == ('This is Strattera 10 mg (atomoxetine): a blue and white capsule with "Lilly" '
                                    'and "3227" printed on it, from Eli Lilly And Company.')
    assert rows[1][2] == dict(rows[1][2], question=k.IMPRINT_Q, answer='It has "Lilly" and "3227" printed on it.')
    assert k.c3pi_rows(records[1], "PillProjectDisc1", {}) == []          # a raw camera file: not taken
    assert k.drug_name("LABETALOL HYDROCHLORIDE Tablets USP 100MG") == "Labetalol Hydrochloride Tablets USP 100 mg"
    assert k.imprint_words("E;720;E;720") == ["E", "720"]


def test_tables():
    """Every pack has a builder, a credit and a limit; the kit's entries are known groups with a cap."""
    assert set(m.US_MODERN_PACKS) == set(m.US_MODERN_LIMITS)
    import us_modern_sources as k
    assert {s.group for s in k.US_MODERN_SOURCES} <= {"share-alike", "noncommercial", "research"}
    assert k.US_MODERN_PICTURE_MAKING_OK <= {s.key for s in k.US_MODERN_SOURCES}


def test_not_modern():
    """Photos whose words say they are older than 1990 or museum pieces are left out; room numbers are not years."""
    assert m.NOT_MODERN.search("Electric clothes dryer c. 1940 - Wisconsin Historical Museum")
    assert m.NOT_MODERN.search("A 1970s era Jerrold brand cable box")
    assert not m.NOT_MODERN.search("Self-checkout lanes at a Kroger store in 2019")
    assert not m.NOT_MODERN.search("The phone in room 1204")


def test_abroad():
    """A US-category photo whose words say it was taken abroad is left out."""
    assert m.ABROAD.search("Marines play the annual Turkey Bowl game on Camp Foster, Okinawa, Japan, Nov. 27, 2024.")
    assert not m.ABROAD.search("A Thanksgiving dinner in Portland, Oregon.")


def test_commons_title():
    """The Commons file title is read back from a credit line."""
    credit = "File:A b.jpg by X, CC0, https://commons.wikimedia.org/wiki/File:A_b%C3%A9.jpg"
    assert m.commons_title(credit) == "File:A bé.jpg"
    assert m.commons_title("no page") == ""


def test_agency_filters():
    """Official events are recognised; a caption that only repeats the file name counts as none."""
    assert m.OFFICIAL.search("Secretary of Energy Rick Perry is joined by ... for a roundtable discussion")
    assert not m.OFFICIAL.search("A farmer loads hay bales onto a trailer near Ames, Iowa.")
    title = "File:20161111-Veterans Memorial Assembly at War Memorial Plaza, New Castle, DE-1382 (31318799326).jpg"
    assert m.only_the_name("20161111-Veterans Memorial Assembly at War Memorial Plaza, New Castle, DE-1382.", title)
    assert m.only_the_name("Veterans Memorial Assembly at War Memorial Plaza.", title)
    assert not m.only_the_name("People apply for disaster food stamps at the convention center.",
                               "File:FEMA - 11511 - Photograph by Michael Rieger.jpg")


def test_everyday_holidays():
    """Military holiday events and official speeches are left out of the holidays pack."""
    def item(name, answer):
        return (name, "u-" + name, [{"question": m.HAPPENING_Q, "answer": answer,
                                      "facts": {"commons_category": "Thanksgiving in the United States"}}])
    items = [item("a", "A family carves a turkey at home in Ohio."),
             item("b", "U.S. Air Force Chief Master Sgt. Carolyn Russell serves Thanksgiving meals at the Falcon "
                       "Dining Facility."),
             item("c", "Secretary of State Antony Blinken delivers remarks at the 2023 commencement.")]
    assert [i[0] for i in m.everyday_holidays(items)] == ["a"]
