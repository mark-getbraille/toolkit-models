"""Self-test of the vehicle and product recalls added on 2026-11-22 (recalls.py), with MADE-UP records only:
nothing is downloaded.

It checks that:
  - every key is registered once in the group "recalls" and asked for by recalls, group:recalls, rcl:nhtsa and one
    key each; the builder and the weekly check send rcl: keys here through refs_common's registry;
  - the letter groups give every make exactly one vehicle job;
  - NHTSA's flat-file lines (recalls and bulletins) become, per make, a part per model with an index of model years
    and a page per year holding each recall in full (with the "do not drive" warning) and each bulletin's summary;
    the smaller makes share an "other makes" book; equipment recalls go into the tire, child seat and equipment
    books;
  - a CPSC record becomes a page with its products, hazard, remedy and contact, in the right category book;
  - an API that has no robots.txt may be read, one whose robots.txt refuses programs or AI readers may not.

Run it from the repository's folder:   python3 -m pytest textbooks/test_recalls.py
"""

import io
import json
import os
import string
import sys
import urllib.error
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_textbooks as B  # noqa: E402
import directory_sources as D  # noqa: E402
import recalls as RC  # noqa: E402
import refs_common as R  # noqa: E402
import sources  # noqa: E402
import updates  # noqa: E402


def use(monkeypatch, routes):
    """Answer every request from routes [(piece of address, answer: text or bytes)]; anything else is 404."""
    def fetch(url, cache=None, binary=False, tries=4):
        for piece, answer in routes:
            if piece in url:
                if isinstance(answer, Exception):
                    raise answer
                if binary:
                    return answer if isinstance(answer, bytes) else answer.encode()
                return answer.decode() if isinstance(answer, bytes) else answer
        raise urllib.error.HTTPError(url, 404, "not found", {}, None)
    monkeypatch.setattr(B, "fetch", fetch)
    monkeypatch.setattr(B, "_robots", {})
    monkeypatch.setattr(D, "_ai", {})


def zipped(name, lines):
    """A zip file's bytes holding one text file of lines."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(name, "\r\n".join(lines).encode("cp1252"))
    return buf.getvalue()


def recall(campaign, make, model, year, kind="V", component="AIR BAGS:FRONTAL", dnd="", received="20190306"):
    """One made-up line of NHTSA's recall file (29 tab-separated fields)."""
    f = [""] * 29
    f[0], f[1], f[2], f[3], f[4], f[6], f[7] = "1", campaign, make, model, year, component, "Made-up Motors"
    f[10], f[11], f[13], f[15] = kind, "1200", "MFR", received
    f[19], f[20], f[21], f[22], f[27] = "THE BAG MAY NOT DEPLOY.", "INJURY RISK.", "DEALERS WILL REPLACE IT.", \
        "OWNERS MAY CALL THE HOTLINE.", dnd
    return "\t".join(f)


def bulletin(nid, make, model, year, summary="Rattle from the dash. Install a pad."):
    """One made-up line of NHTSA's manufacturer-communication file (14 fields)."""
    return "\t".join([nid, "", "20240105", "24-NA-001", "20231220", "", "Service Bulletin/Repair Instructions", make,
                      model, year, "STRUCTURE:BODY", "", "", summary])


def test_registered_in_the_recalls_group():
    assert sources.GROUPS["recalls"] == "Reference, vehicle and product recalls"
    keys = RC.all_keys()
    assert len(keys) == len(set(keys)) == len(RC.LETTER_GROUPS) + 2
    assert sources.expand_keys(["recalls"]) == keys == sources.expand_keys(["group:recalls"])
    assert sources.expand_keys(["rcl:nhtsa"]) == keys[:-1]
    assert R.module_for("rcl:cpsc") is RC
    assert set(RC.LICENCE_LINES) <= set(sources.LICENCE_LINES)
    assert all(row in sources.NOT_INCLUDED for row in RC.NOT_INCLUDED)


def test_builder_and_weekly_check_send_rcl_keys_here(monkeypatch, tmp_path):
    monkeypatch.setattr(RC, "sign", lambda key: f"signed {key}")
    assert updates.fingerprint("rcl:cpsc") == "signed rcl:cpsc"
    called = []
    monkeypatch.setattr(RC, "build", lambda keys, out, cache=None, date=None: called.append(keys) or {})
    B.build(["rcl:nhtsa:c"], str(tmp_path))
    assert called == [["rcl:nhtsa:c"]]


def test_each_make_in_one_letter_group():
    for first in string.ascii_uppercase + string.digits:
        groups = [g for g in RC.LETTER_GROUPS if RC.in_letters(first + "MAKE", g)]
        assert len(groups) == 1, first
    assert RC.norm_make("Mercedes-Benz") == RC.norm_make("MERCEDES BENZ") == "MERCEDES BENZ"


def nhtsa_routes(monkeypatch):
    """The made-up flat files: Chevrolet big enough for its own book, Checker small, and a tire recall."""
    monkeypatch.setattr(RC, "MIN_CAMPAIGNS", 2)
    recalls = [recall("19V182000", "CHEVROLET", "MALIBU", "2019", dnd="Yes"),
               recall("19V182000", "CHEVROLET", "MALIBU", "2018"),
               recall("20V001000", "CHEVROLET", "MALIBU", "2019", component="BRAKES", received="20200110"),
               recall("12V555000", "CHECKER", "MARATHON", "9999"),
               recall("18T010000", "CHENGSHAN", "TRUCK TIRE", "9999", kind="T", component="TIRES"),
               recall("19V999000", "DODGE", "RAM", "2019")]
    bulletins = [bulletin("10074303", "CHEVROLET", "MALIBU", "2019"), bulletin("10074304", "CHEVROLET", "VOLT", "2017")]
    use(monkeypatch, [("FLAT_RCL_POST_2010.zip", zipped("FLAT_RCL_POST_2010.txt", recalls)),
                      ("TSBS_RECEIVED_2020-2024.zip", zipped("TSBS_RECEIVED_2020-2024.txt", bulletins))])


def test_nhtsa_vehicle_books(monkeypatch):
    nhtsa_routes(monkeypatch)
    left_out = []
    books = RC.nhtsa_books("c", None, left_out)
    names = [b.name for b in books]
    assert names == ["nhtsa_chevrolet", "nhtsa_other_makes_c"]                 # Dodge is another job's
    chevy = books[0]
    paths = [p.path for p in chevy.pages]
    assert paths == ["malibu", "malibu-2019", "malibu-2018", "volt", "volt-2017"]
    index, y2019 = chevy.pages[0], chevy.pages[1]
    assert index.unit == y2019.unit == "MALIBU" and '<a href="malibu-2019">2019</a>: 2 recalls, 1 bulletins' in index.body
    assert y2019.body.index("Recall 20V001000") < y2019.body.index("Recall 19V182000")    # newest first
    assert "<strong>Do not drive this vehicle</strong>" in y2019.body
    for words in ("Defect: THE BAG MAY NOT DEPLOY.", "Consequence: INJURY RISK.", "Remedy: DEALERS WILL REPLACE IT.",
                  "Notes: OWNERS MAY CALL THE HOTLINE.", "Units potentially affected: 1200",
                  "Service Bulletin/Repair Instructions 24-NA-001", "Rattle from the dash. Install a pad."):
        assert words in y2019.body, words
    assert "Do not drive" in chevy.pages[2].body                                # the campaign's warning, every year
    other = books[1]
    assert [p.title for p in other.pages] == ["CHECKER MARATHON: model years", "CHECKER MARATHON year not given"]
    assert chevy.published == "2023-12-20" and chevy.licence.startswith("Public domain")
    assert any(o["url"].endswith("FLAT_RCL_POST_2010.zip") and o["sha256"] for o in chevy.originals)
    assert any("FLAT_RCL_PRE_2010.zip" in x["title"] for x in left_out)          # missing in this test: said


def test_nhtsa_equipment_books(monkeypatch):
    nhtsa_routes(monkeypatch)
    books = RC.nhtsa_books("equipment", None, [])
    assert [b.name for b in books] == ["nhtsa_tires_recalls", "nhtsa_child_seats_recalls", "nhtsa_equipment_recalls"]
    tires = books[0]
    assert [p.title for p in tires.pages] == ["CHENGSHAN TRUCK TIRE: model years", "CHENGSHAN TRUCK TIRE year not "
                                                                                   "given"]
    assert "Components: TIRES" in tires.pages[1].body and "bulletin" not in tires.pages[1].body.lower()
    assert not books[1].pages and not books[2].pages                            # no pages: left out by the build


CPSC_ROW = {"RecallID": 11068, "RecallNumber": "27096", "RecallDate": "2026-11-19T00:00:00",
            "LastPublishDate": "2026-11-19T00:00:00", "Title": "Made-up Company Recalls Magnetic Toys",
            "Description": "This recall involves magnetic stick figure toys.", "URL": "https://cpsc.gov/Recalls/x",
            "ConsumerContact": "Made-up Company by email.",
            "Products": [{"Name": "Magnetic Toys", "Type": "Toy Figures", "NumberOfUnits": "About 100"}],
            "Hazards": [{"Name": "Magnets can be swallowed."}], "Remedies": [{"Name": "Stop using them."}],
            "RemedyOptions": [{"Option": "Refund"}], "Injuries": [{"Name": "None reported."}],
            "Retailers": [{"Name": "Sold online."}], "Images": [{"URL": "https://x/y.png", "Caption": "The toys"}]}


def test_cpsc_books(monkeypatch):
    lamp = dict(CPSC_ROW, RecallID=2, RecallNumber="1", RecallDate="1999-02-01T00:00:00", Title="Lamps Recalled",
                Products=[{"Name": "Desk lamp", "Type": "Lamps"}])
    use(monkeypatch, [("RecallDateStart=2026", json.dumps([CPSC_ROW])), ("RecallDateStart=1999", json.dumps([lamp])),
                      ("RecallDateStart=", "[]")])
    books = RC.cpsc_books(None, [])
    assert [b.name for b in books] == ["cpsc_recalls_children", "cpsc_recalls_electrical"]
    page = books[0].pages[0]
    assert page.title == "Made-up Company Recalls Magnetic Toys" and page.unit == "Recalls of 2026"
    for words in ("<h2>Hazard</h2><p>Magnets can be swallowed.</p>", "<h2>Remedy</h2><p>Stop using them.</p>",
                  "Magnetic Toys, type: Toy Figures, units: About 100", "<h2>Consumer contact</h2>",
                  "<h2>Pictures (captions only)</h2><p>The toys</p>", "Recall number 27096, 2026-11-19."):
        assert words in page.body, words
    assert books[0].published == "2026-11-19" and books[1].published == "1999-02-01"


def test_api_readable(monkeypatch):
    use(monkeypatch, [("www.saferproducts.gov/robots.txt", urllib.error.HTTPError("x", 403, "denied", {}, None))])
    assert R.api_readable(RC.CPSC_API)                                         # no robots rules: may be read
    use(monkeypatch, [("/robots.txt", "User-agent: *\nDisallow: /RestWebServices/\n")])
    assert not R.api_readable(RC.CPSC_API)
    use(monkeypatch, [("/robots.txt", "User-agent: *\nAllow: /\nContent-Signal: ai-train=no\n")])
    assert not R.api_readable(RC.CPSC_API)
