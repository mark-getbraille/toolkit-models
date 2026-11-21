"""Self-tests of medications.py (the medicine books) with made-up answers only: nothing is downloaded. Every label,
company, brand and number here is invented for the test ("Examplofen", "Zoomzap", Example Pharma).

Run it from the repository's folder:   python3 -m pytest textbooks/test_medications.py
"""

import io
import json
import os
import struct
import sys
import urllib.error
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import medications as M  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402


def spl(doc_code, setid, title, sections, product="Examplofen", generic="EXAMPLOFEN", strength=("200", "mg"),
        approval="NDA099999", company="Example Pharma Inc.", unit_extra=""):
    """A made-up SPL XML label: its document type, set id, product (with one active and one inactive ingredient)
    and the sections given as XML."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<document xmlns="urn:hl7-org:v3">
 <code code="{doc_code}" displayName="TEST LABEL"/><title>{title}</title><effectiveTime value="20261001"/>
 <setId root="{setid}"/><versionNumber value="3"/>
 <author><assignedEntity><representedOrganization><name>{company}</name></representedOrganization></assignedEntity>
 </author>
 <component><structuredBody>
  <component><section><code code="48780-1"/><subject><manufacturedProduct><manufacturedProduct>
   <name>{product}</name><formCode displayName="TABLET"/>
   <asEntityWithGeneric><genericMedicine><name>{generic}</name></genericMedicine></asEntityWithGeneric>
   <ingredient classCode="ACTIB"><quantity><numerator unit="{strength[1]}{unit_extra}" value="{strength[0]}"/>
    <denominator unit="1" value="1"/></quantity><ingredientSubstance><name>{generic}</name></ingredientSubstance>
   </ingredient>
   <ingredient classCode="IACT"><ingredientSubstance><name>CORN STARCH</name></ingredientSubstance></ingredient>
  </manufacturedProduct>
  <consumedIn><substanceAdministration><routeCode displayName="ORAL"/></substanceAdministration></consumedIn>
  <subjectOf><approval><id extension="{approval}"/><code displayName="NDA"/></approval></subjectOf>
  </manufacturedProduct></subject></section></component>
  {sections}
 </structuredBody></component>
 <observationMedia ID="MM1"><text>Chemical structure of examplofen</text></observationMedia>
</document>"""


def sec(code, title, text, children=""):
    """A made-up label section."""
    return (f'<component><section><code code="{code}"/><title>{title}</title><text>{text}</text>{children}'
            f'</section></component>')


RX_SECTIONS = (
    sec("34066-1", "WARNING: RISK OF MADE-UP EVENTS", "<paragraph>Examplofen may cause made-up events.</paragraph>")
    + '<component><section><code code="34067-9"/><title>1 INDICATIONS AND USAGE</title><excerpt><highlight><text>'
      "<paragraph>Examplofen is a made-up medicine indicated for pretend pain. It is not real.</paragraph>"
      "</text></highlight></excerpt><text><paragraph>Examplofen is indicated for pretend pain.</paragraph></text>"
      "</section></component>"
    + sec("34068-7", "2 DOSAGE AND ADMINISTRATION", "<list listType=\"ordered\"><item>Take one tablet.</item>"
          "<item>Drink <content styleCode=\"bold\">water</content>.</item></list>"
          "<table><caption>Table 1</caption><tbody><tr><td>Adults</td><td>200 mg</td></tr></tbody></table>")
    + sec("34084-4", "6 ADVERSE REACTIONS", "<paragraph>Pretend headache.</paragraph>")
    + sec("43684-0", "8 USE IN SPECIFIC POPULATIONS", "",
          sec("42228-7", "8.1 Pregnancy", "<paragraph>Not studied in made-up pregnancies.</paragraph>")
          + sec("34081-0", "8.4 Pediatric Use", "<paragraph>Not for made-up children.</paragraph>"))
    + sec("34089-3", "11 DESCRIPTION",
          '<paragraph>A white tablet.</paragraph><renderMultiMedia referencedObject="MM1"/>')
    + sec("42231-1", "MEDICATION GUIDE", "<paragraph>Read this before you take Examplofen.</paragraph>")
    + sec("51945-4", "PACKAGE LABEL", "<paragraph>NDC 0000-0000 Examplofen 200 mg</paragraph>"))
OTC_SECTIONS = (
    sec("55105-1", "Purpose", "<paragraph>Pretend pain reliever</paragraph>")
    + sec("34067-9", "Uses", "<list><item>temporarily relieves pretend aches</item></list>")
    + sec("34071-1", "Warnings", "",
          sec("50570-1", "Do not use", "<paragraph>if allergic to examplofen</paragraph>")
          + sec("53414-9", "If pregnant or breast-feeding,", "<paragraph>ask a health professional.</paragraph>"))
    + sec("34068-7", "Directions", "<paragraph>take 1 tablet every 4 hours</paragraph>")
    + sec("42229-5", "Other information", "<paragraph>store at room temperature</paragraph>"))
VET_SECTIONS = (
    sec("34067-9", "Indications", "<paragraph>Zoomzap is for the control of pretend itching in dogs.</paragraph>")
    + sec("34068-7", "Dosage and Administration", "<paragraph>Give once daily.</paragraph>")
    + sec("50744-2", "Information for Dog Owners", "<paragraph>Watch your dog.</paragraph>"))
FARM_SECTIONS = sec("34067-9", "Indications", "<paragraph>For use in cattle and swine feed.</paragraph>")

RX_ID, OTC_ID, REPACK_ID, VET_ID, FARM_ID, HOMEO_ID = (f"0000000{i}-0000-0000-0000-000000000000" for i in range(6))
LABELS = {
    RX_ID: spl("34391-3", RX_ID, "Examplofen tablets", RX_SECTIONS),
    REPACK_ID: spl("34391-3", REPACK_ID, "Examplofen tablets", RX_SECTIONS, company="Some Repack LLC"),
    OTC_ID: spl("34390-5", OTC_ID, "Drug Facts", OTC_SECTIONS, approval="M013", strength=("100", "mg")),
    VET_ID: spl("50578-4", VET_ID, "zoomzap", VET_SECTIONS, product="Zoomzap", generic="ZAPICITINIB MALEATE",
                approval="NADA141999"),
    FARM_ID: spl("50576-8", FARM_ID, "Feedmix", FARM_SECTIONS, product="Feedmix", generic="PRETENDOMYCIN",
                 approval="NADA099111"),
    HOMEO_ID: spl("50577-6", HOMEO_ID, "calm", VET_SECTIONS, product="Calm", generic="CHAMOMILLA",
                  strength=("30", "[hp_C]")),
}
RXNORM = "\n".join([
    "SETID|SPL_VERSION|RXCUI|RXSTRING|RXTTY",
    f"{RX_ID}|3|1|examplofen 400 MG Oral Tablet|SCD",
    f"{RX_ID}|3|2|examplofen 400 MG Oral Tablet [Zingo]|SBD",
    f"{REPACK_ID}|3|1|examplofen 400 MG Oral Tablet|SCD",
    f"{OTC_ID}|3|3|examplofen sodium 100 MG Oral Tablet|SCD",
    f"{OTC_ID}|3|4|examplofen sodium 100 MG Oral Tablet [Painaway]|SBD",
])
META = "\n".join([
    "SETID|ZIP_FILE_NAME|UPLOAD_DATE|SPL_VERSION|TITLE",
    f"{RX_ID}|x.zip|10/01/2026|3|ZINGO (EXAMPLOFEN) TABLET [EXAMPLE PHARMA INC.]",
    f"{REPACK_ID}|y.zip|11/01/2026|3|EXAMPLOFEN TABLET [SOME REPACK LLC]",
    f"{OTC_ID}|z.zip|09/01/2026|3|PAINAWAY (EXAMPLOFEN SODIUM) TABLET [EXAMPLE PHARMA INC.]",
])


def zipped(name, text):
    """A zip file holding one text file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, text)
    return buf.getvalue()


def listing(rows):
    """A made-up DailyMed spls.json answer (one page)."""
    return json.dumps({"data": [{"setid": s, "title": t, "spl_version": 3, "published_date": "Oct 01, 2026"}
                                for s, t in rows], "metadata": {"total_pages": 1}})


def fda_zip():
    """A made-up Drugs@FDA data file."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Applications.txt",
                   "ApplNo\tApplType\tApplPublicNotes\tSponsorName\n099999\tNDA\t\tEXAMPLE PHARMA\n")
        z.writestr("Submissions.txt", "ApplNo\tSubmissionClassCodeID\tSubmissionType\tSubmissionNo\tSubmissionStatus\t"
                                      "SubmissionStatusDate\n099999\t7\tORIG\t1\tAP\t1999-04-20 00:00:00\n")
    return buf.getvalue()


def answer(url, cache=None, binary=False, tries=4):
    """The made-up answer of every address the builder reads (404 for anything else, robots.txt included)."""
    routes = [
        ("api.fda.gov/drug/label.json", json.dumps({"meta": {"license": "https://open.fda.gov/license/"}})),
        ("doctype=34391-3", listing([(RX_ID, "ZINGO (EXAMPLOFEN) TABLET [EXAMPLE PHARMA INC.]"),
                                     (REPACK_ID, "EXAMPLOFEN TABLET [SOME REPACK LLC]")])),
        ("doctype=50578-4", listing([(VET_ID, "ZOOMZAP (ZAPICITINIB MALEATE) TABLET [EXAMPLE ANIMAL HEALTH]")])),
        ("doctype=50576-8", listing([(FARM_ID, "FEEDMIX 10% TYPE A MEDICATED ARTICLE GRANULE [EXAMPLE FEEDS]")])),
        ("doctype=50577-6", listing([(HOMEO_ID, "CALM (CHAMOMILLA) LIQUID [EXAMPLE HOMEOPET]")])),
        ("spls.json", listing([])),
        ("rxnorm_mappings.zip", zipped("rxnorm_mappings.txt", RXNORM)),
        ("meta_data.zip", zipped("dm_spl_zip_files_meta_data.txt", META)),
        ("website-policies", "<p>They are in the public domain and may be republished, reprinted and otherwise "
                             "used freely by anyone</p>"),
        ("www.fda.gov/media/89850", fda_zip()),
        ("package_show", json.dumps({"result": {"license_title": "Open Government Licence - Canada"}})),
        ("drugproduct", json.dumps([{"drug_code": 1, "class_name": "Human", "brand_name": "EXAMPLO-CAN"},
                                    {"drug_code": 2, "class_name": "Veterinary", "brand_name": "ZAPCAN"},
                                    {"drug_code": 3, "class_name": "Human", "brand_name": "PAINAWAY CANADA"},
                                    {"drug_code": 4, "class_name": "Human", "brand_name": "EXAMPLOFEN TABLETS 200 MG"}
                                    ])),
        ("activeingredient", json.dumps([{"drug_code": 1, "ingredient_name": "EXAMPLOFEN"},
                                         {"drug_code": 2, "ingredient_name": "ZAPICITINIB"},
                                         {"drug_code": 3, "ingredient_name": "EXAMPLOFEN (EXAMPLOFEN SODIUM)"},
                                         {"drug_code": 4, "ingredient_name": "EXAMPLOFEN"}])),
        ("drug/schedule/", json.dumps([{"drug_code": 1, "schedule_name": "PRESCRIPTION"},
                                       {"drug_code": 3, "schedule_name": "NON-PRESCRIPTION DRUGS"},
                                       {"drug_code": 4, "schedule_name": "PRESCRIPTION"}])),
        ("spl-resources-all-drug-labels", '<a href="x/dm_spl_monthly_update_sep2026.zip">'
                                          '<a href="x/dm_spl_monthly_update_oct2026.zip">'),
    ]
    for setid, xml in LABELS.items():
        routes.append((f"spls/{setid}.xml", xml))
    for piece, body in routes:
        if piece in url:
            return body if binary or isinstance(body, str) else body.decode()
    raise urllib.error.HTTPError(url, 404, "not found", {}, None)


def use_fakes(monkeypatch):
    """Answer every request with the made-up answers, with fresh robots.txt records and nothing remembered."""
    monkeypatch.setattr(B, "fetch", answer)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(M, "_READ", {})


def words(text):
    """The words of some HTML (tags removed)."""
    import html
    import re
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", text)).split())


def test_names_and_forms():
    """RxNorm names give the ingredients and form; salts are ignored for matching; forms become ways of use."""
    assert M.parse_rxnorm("ibuprofen 200 MG Oral Tablet") == (["ibuprofen"], "Oral Tablet")
    assert M.parse_rxnorm("24 HR metformin hydrochloride 500 MG Extended Release Oral Tablet") == \
        (["metformin hydrochloride"], "Extended Release Oral Tablet")
    assert M.parse_rxnorm("acetaminophen 325 MG / codeine phosphate 30 MG Oral Tablet") == \
        (["acetaminophen", "codeine phosphate"], "Oral Tablet")
    assert M.parse_rxnorm("5 ML lidocaine hydrochloride 10 MG/ML Injection")[0] == ["lidocaine hydrochloride"]
    assert M.base_name("METFORMIN HYDROCHLORIDE") == "metformin" and M.base_name("sodium chloride") == "sodium"
    assert M.base_name("AMOXICILLIN (AMOXICILLIN TRIHYDRATE)") == "amoxicillin"
    assert M.combo_key(["codeine phosphate", "acetaminophen"]) == "acetaminophen + codeine"
    assert M.display_name(["guaifenesin", "acetaminophen", "dextromethorphan hydrobromide"]) == \
        "Acetaminophen, dextromethorphan hydrobromide and guaifenesin"
    assert M.form_family("Oral Tablet") == "by mouth"
    assert M.form_family("Extended Release Oral Tablet") == "by mouth, extended release"
    assert M.form_family("Injectable Solution") == "injection" and M.form_family("Topical Cream") == "on the skin"
    assert M.form_family("Ophthalmic Solution") == "in the eye" and M.form_family("Toothpaste") == "in the mouth"
    assert M.parse_title("QUELLIN (CARPROFEN) TABLET, CHEWABLE [ELANCO US INC.]") == \
        ("QUELLIN", ["CARPROFEN"], "TABLET, CHEWABLE", "ELANCO US INC.")
    assert M.parse_title("CARPROFEN TABLET, CHEWABLE [ZYVET]") == ("", ["CARPROFEN"], "TABLET, CHEWABLE", "ZYVET")
    assert M.parse_title("OTIC (NEOMYCIN SULFATE, AND TETRACAINE HYDROCHLORIDE) OINTMENT [X]")[1] == \
        ["NEOMYCIN SULFATE", "TETRACAINE HYDROCHLORIDE"]
    assert M.parse_title("IBUPROFEN (IBUPROFEN) TABLET [X]")[0] == ""      # the generic name is not a brand
    assert M.parse_title("AMOXICILLIN (AMOXICILLIN) CAPSULE AMOXICILLIN (AMOXICILLIN) TABLET [X]")[:2] == \
        ("", ["AMOXICILLIN"])                                                 # a label of several products
    brand, generics, _form, _company = M.parse_title("ZINGO (EXAMPLOFEN (AS SODIUM)) TABLET [X]")
    assert brand == "ZINGO" and M.combo_key(generics) == "examplofen"
    assert M.brand_words("CHILDREN'S MOTRIN", "ibuprofen") == "Children's Motrin"
    assert M.brand_words("APO-METFORMIN ER", "metformin") == "Apo-Metformin Er"
    assert M.brand_words("IBUPROFEN TABLETS 200 MG", "ibuprofen") == ""
    assert M.brand_words("Metformin ER", "metformin") == ""
    assert M.first_sentence("<p>INDICATIONS AND USAGE Carefully consider the risks of examplofen. Examplofen is "
                            "indicated for relief of pretend pain. More.</p>") == \
        "Examplofen is indicated for relief of pretend pain."


def test_kits_and_packs():
    """A pack counts as its medicine (placebo tablets and swabs aside); a pack of several medicines as their
    combination; a kit of unrelated medicines without a pack is left out."""
    text = "\n".join(["SETID|SPL_VERSION|RXCUI|RXSTRING|RXTTY",
                      "pill|1|1|levonorgestrel 0.1 MG / ethinyl estradiol 0.02 MG Oral Tablet|SCD",
                      "pill|1|2|inert ingredients 1 MG Oral Tablet|SCD", "pill|1|3|{21 (x) / 7 (y) } Pack|GPCK",
                      "shot|1|1|1 ML examplomab 10 MG/ML Injection|SCD",
                      "shot|1|2|isopropyl alcohol 0.7 ML/ML Medicated Pad|SCD",
                      "hp|1|1|amoxicillin 500 MG Oral Capsule|SCD", "hp|1|2|clarithromycin 500 MG Oral Tablet|SCD",
                      "hp|1|3|{x} Pack [Examplopak]|BPCK",
                      "kit|1|1|acetaminophen 325 MG Oral Tablet|SCD",
                      "kit|1|2|bacitracin 500 UNT/GM Topical Ointment|SCD"])
    kits = set()
    recs = M.rxnorm_records(text, kits)
    assert M.combo_key(recs["pill"]["names"]) == "ethinyl estradiol + levonorgestrel"
    assert recs["shot"]["names"] == {"examplomab"} and list(recs["shot"]["forms"]) == ["injection"]
    assert M.combo_key(recs["hp"]["names"]) == "amoxicillin + clarithromycin" and recs["hp"]["brands"] == {"Examplopak"}
    assert "kit" not in recs and kits == {"kit"}


def test_keys_and_pieces():
    """The keys: every book, human ones, one book; names go to the book of their first letter."""
    keys = M.expand_keys(["medicines"])
    assert len(keys) == len(M.RX_PIECES) + len(M.OTC_PIECES) + 1 and "med:animal" in keys
    assert M.expand_keys(["med:rx:e-f", "med:rx:zz", "med:otc"])[:2] == ["med:rx:e-f", "med:otc:a-b"]
    assert sources.expand_keys(["med:animal"]) == ["med:animal"]
    assert "med:rx:a" not in sources.expand_keys(["all"])       # asked for by name only
    assert M.in_piece("Famotidine", "e-f", M.RX_PIECES) and not M.in_piece("Gabapentin", "e-f", M.RX_PIECES)
    assert M.in_piece("5-fluorouracil", "u-z", M.RX_PIECES)
    assert B.licence_kind(M.LICENCE) == "open"
    assert sources.GROUPS["medicines"] and sources.GROUPS["vet_medicines"]


def test_label_in_plain_order():
    """A label's sections are put in the plain order, the boxed warning first under Warnings, the pregnancy
    subsection pulled out of "Use in specific populations", pictures as their description, the package label
    last; a part the label lacks says so; the label's own highlights and its first indication are kept."""
    label = M.read_label(LABELS[RX_ID])
    assert label.kind == "rx" and label.company == "Example Pharma Inc." and label.date == "2026-10-01"
    html = M.label_html(label, "Examplofen, by mouth: label of Zingo", {"NDA099999": {"sponsor": "EXAMPLE PHARMA",
                                                                                     "approved": "1999-04-20"}})
    text = words(html)
    order = [text.index(w) for w in ("Highlights", "What it is for", "How to take it", "Warnings WARNING: RISK",
                                     "Side effects", "Interactions The label has no separate section",
                                     "Storage", "Pregnancy and breastfeeding 8.1 Pregnancy",
                                     "Information for patients MEDICATION GUIDE", "Other parts of the label",
                                     "8.4 Pediatric Use", "Picture: Chemical structure", "PACKAGE LABEL")]
    assert order == sorted(order)
    assert "FDA application: NDA 099999, held by EXAMPLE PHARMA, first approved 1999-04-20." in text
    assert "<ol><li>Take one tablet.</li>" in html and "<strong>water</strong>" in html
    assert "<caption>Table 1</caption>" in html
    assert "Active: EXAMPLOFEN 200 mg. Inactive: corn starch" in text
    assert M.uses_sentence(label) == "Examplofen is a made-up medicine indicated for pretend pain."
    again = words(M.label_html(label, "x", {}))                   # the label is not changed by being written
    assert "8.1 Pregnancy" in again
    otc = M.read_label(LABELS[OTC_ID])
    text = words(M.label_html(otc, "x", {}))
    assert otc.kind == "otc" and "Marketing category: NDA M013" in text
    assert text.index("Pregnancy and breastfeeding If pregnant") > text.index("Storage Other information")
    assert "Do not use if allergic" in text
    assert M.read_label(LABELS[HOMEO_ID]).homeopathic


def test_choice_of_label():
    """A brand's label is preferred, then not a repackager's, then the newest year, then the most revised."""
    a = {"brand": False, "company": "SOME REPACK LLC", "date": "2026-11-01", "version": 9}
    b = {"brand": False, "company": "MAKER INC", "date": "2026-01-01", "version": 1}
    c = {"sbd": True, "brand": True, "company": "BRAND INC", "date": "2020-01-01", "version": 1}
    assert sorted([a, b, c], key=M.rank, reverse=True) == [c, b, a]
    old = dict(b, date="2025-03-01", version=30)
    assert sorted([old, b, dict(b, version=7)], key=M.rank, reverse=True) == [dict(b, version=7), b, old]
    pharmacy = {"brand": False, "company": "STATE HEALTH DEPARTMENT", "date": "2026-11-01", "version": 1}
    maker = dict(b, maker=M.first_word(b["company"]) in M.makers({"NDA1": {"sponsor": "MAKER INC"}}))
    assert sorted([pharmacy, maker], key=M.rank, reverse=True) == [maker, pharmacy]


def test_species():
    """Animal labels go to the pet or the farm book by the animals their uses name."""
    assert M.species(M.read_label(LABELS[VET_ID])) == {"pets"}
    assert M.species(M.read_label(LABELS[FARM_ID])) == {"farm"}


def test_build_books(monkeypatch, tmp_path):
    """Whole books from made-up answers: one page per medicine with its quick facts and notice, brand names (US and
    Canadian) leading to it, the about and brand pages, versioned files with the key and fingerprint, homeopathic
    products left out; the medicines' licence lines and groups reach textbooks.json."""
    use_fakes(monkeypatch)
    rx = M.books_for_key("med:rx:e-f")[0]
    assert [p.title for p in rx.pages] == ["About this book", "Brand names A to Z", "Examplofen"]
    page = rx.pages[2].body
    text = words(page)
    assert M.HUMAN_NOTICE in text and "Brand names (US): Zingo" in text
    assert "Brand names in Canada (Health Canada): Examplo-Can." in text      # not the generic name, not the OTC one
    assert "Boxed warning (the FDA's strongest warning): yes" in text
    assert "label of Zingo" in text and "Example Pharma Inc." in text            # the brand, not the repackager
    assert ("brand/zingo", "Zingo (Examplofen)", "examplofen") in rx.redirects
    assert rx.licence == M.LICENCE and M.HUMAN_NOTICE in rx.notice and rx.group == "medicines"
    otc = M.books_for_key("med:otc:d-h")[0]
    assert [p.title for p in otc.pages][2:] == ["Examplofen sodium"]
    assert "Brand names (US): Painaway." in words(otc.pages[2].body)
    assert "Brand names in Canada (Health Canada): Painaway Canada." in words(otc.pages[2].body)
    assert M.books_for_key("med:rx:a")[0].pages == []                           # no medicine starts with a
    left = []
    pets, farm = M.books_for_key("med:animal", left_out=left)
    assert [p.title for p in pets.pages][2:] == ["Zapicitinib maleate"] and pets.group == "vet_medicines"
    assert M.VET_NOTICE in words(pets.pages[2].body) and "How to give it" in words(pets.pages[2].body)
    assert "Information for owners Information for Dog Owners" in words(pets.pages[2].body)
    assert "Zapcan" in words(pets.pages[2].body)
    assert [p.title for p in farm.pages][2:] == ["Pretendomycin"]
    assert any("Homeopathic" in x["title"] for x in left)
    manifests = M.build_medicines(["med:rx:e-f", "med:animal"], str(tmp_path))
    entry = manifests["med:rx:e-f"]["books"][0]
    assert entry["file"].startswith("medicines_us_prescription_e_f.") and entry["release"] == "medicines"
    assert entry["key"] == "med:rx:e-f" and entry["fingerprint"] == "dailymed-2026-10"
    assert entry["licence_kind"] == "open" and entry["items"] == 1
    with open(tmp_path / entry["file"], "rb") as f:
        assert struct.unpack("<I", f.read(4))[0] == 72173914
    assert len(manifests["med:animal"]["books"]) == 2
    data = B.merge([str(tmp_path / n) for n in os.listdir(tmp_path) if n.startswith("manifest-")])
    assert "dailymed" in data["licence_lines"] and any("LactMed" in x["title"] for x in data["not_included"])
    assert data["groups"]["vet_medicines"] and data["group_notes"]["medicines"]
    monkeypatch.setattr(M, "_READ", {})
    assert updates.fingerprint("med:rx:a") == "dailymed-2026-10"


def test_licence_gone(monkeypatch):
    """When openFDA no longer names its public-domain licence, no book is made and the reason is said."""
    use_fakes(monkeypatch)
    monkeypatch.setattr(M, "licence_still_open", lambda: False)
    left = []
    assert M.books_for_key("med:rx:e-f", left_out=left) == [] and "licence" in left[0]["reason"]


def test_redirects_in_zim(tmp_path):
    """A book's redirects (brand names) are written into the ZIM file and change its content checksum."""
    book = B.Book(name="t", title="T", subject="s", level="reference", group="medicines", publisher="p",
                  country="c", licence=M.LICENCE, licence_url="u", source="s")
    book.pages = [B.Page("examplofen", "Examplofen", "<p>x</p>")]
    before = B.content_sha256(book)
    book.redirects = [("brand/zingo", "Zingo (Examplofen)", "examplofen")]
    assert B.content_sha256(book) != before
    entry = B.write_book(book, str(tmp_path), versioned=True)
    with open(tmp_path / entry["file"], "rb") as f:
        assert b"Zingo (Examplofen)" in f.read()
