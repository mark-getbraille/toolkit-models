"""A self-test of the college and university parsers (packs/university_packs.py and
training-kit/kit/university_sources.py), with made-up records only: nothing is downloaded from the internet.

It checks that:
  - a DPLA item is taken only when it is an image, its data provider is a college or university (not a state archive
    or public library) and its rights URI is open (NoC-US, the Public Domain Mark, CC0 or CC BY), and its rows carry
    the record's own words, the place and the holding library;
  - the full-size picture is found (mediaMaster, a CONTENTdm IIIF address, a IIIF manifest of version 2 or 3);
  - pictures are left out for nudity, swimwear, crime, portraits and records, camps and school pupils, official
    events and old slurs, and (modern packs) for being older than 1990; a child is marked, a dead or injured child is
    left out;
  - college captions and library records are cleaned into a description;
  - the kit's DPLA entries take only their own rights (never NoDerivatives) and add nothing without a key.

Run it from the repository's folder:   python3 -m pytest packs/test_university.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import university_packs as u  # noqa: E402

NOC = "http://rightsstatements.org/vocab/NoC-US/1.0/"


def doc(**changes):
    """A made-up DPLA item (the fields the builder reads), with changes."""
    d = {"id": "abc123", "isShownAt": "https://example.edu/item/1",
         "dataProvider": {"name": "Example State University Libraries"}, "provider": {"name": "Example Hub"},
         "rights": NOC, "object": "https://cdm.example.edu/utils/getthumbnail/collection/photos/id/42",
         "sourceResource": {"title": ["Students studying in the library reading room"],
                            "description": ["Several students sit at long wooden tables with books and lamps."],
                            "type": ["image"], "subject": [{"name": "Libraries"}, {"name": "College students"}],
                            "date": [{"displayDate": "circa 1995", "begin": "1995-01-01"}],
                            "spatial": [{"name": "Denton (Tex.)", "city": "Denton", "state": "Texas",
                                         "country": "United States"}]}}
    d.update(changes)
    return d


def test_dpla_item_taken_with_its_words_place_and_library():
    """An open image item of a university library: its title and description, place, year and holding library."""
    item, reason = u.dpla_item(doc())
    assert reason == ""
    assert item["answer"] == ("Students studying in the library reading room. Several students sit at long wooden "
                              "tables with books and lamps.")
    assert item["place"] == "Denton, Texas, USA" and item["year"] == 1995
    assert "No Copyright - United States" in item["credit"] and "Example State University Libraries" in item["credit"]
    rows = u.dpla_rows(item)
    assert [r["question"] for r in rows] == [u.DESCRIBE_Q, u.WHERE_Q]
    assert rows[1]["answer"] == "It was taken in Denton, Texas, USA."
    assert rows[0]["facts"]["holding_library"] == "Example State University Libraries"
    assert not any(r.get("child") for r in rows)


def test_dpla_item_refused():
    """Not an image, not a college, a state archive, or rights that are not open."""
    assert u.dpla_item(doc(sourceResource={"type": ["text"], "title": ["A letter"]}))[0] is None
    assert u.dpla_item(doc(dataProvider={"name": "Ohio History Connection"}))[0] is None
    assert u.dpla_item(doc(dataProvider={"name": "Texas State Library and Archives Commission"}))[0] is None
    assert u.dpla_item(doc(rights="http://rightsstatements.org/vocab/InC/1.0/"))[0] is None
    assert u.dpla_item(doc(rights="http://creativecommons.org/licenses/by-nc/4.0/"))[0] is None
    assert u.dpla_item(doc(rights="http://creativecommons.org/licenses/by-sa/4.0/"))[0] is None
    for ok in ("http://creativecommons.org/publicdomain/mark/1.0/", "http://creativecommons.org/publicdomain/zero/1.0/",
               "https://creativecommons.org/licenses/by/4.0/"):
        assert u.dpla_item(doc(rights=ok))[0] is not None
    assert u.dpla_rights_name("http://creativecommons.org/licenses/by/3.0/us/") == "CC BY 3.0"


def test_pictures():
    """mediaMaster first; a CONTENTdm thumbnail made into its IIIF address; IIIF manifests of version 2 and 3."""
    assert u.dpla_picture(doc(mediaMaster=["https://x.edu/full.jpg"])) == "https://x.edu/full.jpg"
    assert u.dpla_picture(doc()) == "https://cdm.example.edu/iiif/2/photos:42/full/!2048,2048/0/default.jpg"
    assert u.dpla_picture(doc(object="https://x.edu/thumb/small.jpg")) == ""
    v2 = {"sequences": [{"canvases": [{"images": [{"resource": {"@id": "https://x.edu/a.jpg",
                                                                "service": {"@id": "https://x.edu/iiif/a"}}}]}]}]}
    assert u.iiif_image(v2) == "https://x.edu/iiif/a/full/!2048,2048/0/default.jpg"
    v3 = {"items": [{"items": [{"items": [{"body": {"id": "https://x.edu/b.jpg",
                                                    "service": [{"id": "https://x.edu/iiif/b"}]}}]}]}]}
    assert u.iiif_image(v3) == "https://x.edu/iiif/b/full/!2048,2048/0/default.jpg"
    assert u.iiif_image({}) == ""


def test_left_out_because():
    """Safety, privacy and age rules; the year only for the modern packs."""
    ok = "Students walk across the quad in the autumn"
    assert u.left_out_because(ok, 2015) == ""
    assert "nudity" in u.left_out_because("Bathing beauty contest on the beach", 1950, modern=False)
    assert "crime" in u.left_out_because("Police arrest a suspect near campus", 2001)
    assert "privacy" in u.left_out_because("Portrait of the class of 1998", 1998)
    assert "privacy" in u.left_out_because("Football team photo", 2005)
    assert "minors" in u.left_out_because("Summer camp campers at the lake", 2010)
    assert "minors" in u.left_out_because("High school visit day on campus", 2010)
    assert "official" in u.left_out_because("Board of trustees luncheon", 2012)
    assert "official" in u.left_out_because("2013 PTK Induction", 2013)
    assert "slur" in u.left_out_because("Squaw with basket", 1905, modern=False)
    assert "child" in u.left_out_because("Injured child after the flood", 1937, modern=False)
    assert "1990" in u.left_out_because(ok, 1975)
    assert u.left_out_because(ok, 1975, modern=False) == ""
    assert u.left_out_because("A campus map on the wall of the student union", 2010) == ""


def test_rows_marked():
    """A child in the words marks every row; the dead or injured mark them graphic."""
    spec = u.stream("Files from X Flickr stream", "X College", "Salem, Virginia, USA", 1, r"X")
    rows = u.stream_rows("A mother and her daughter tour the campus in the spring.", spec, "credit", "daughter")
    assert [r["question"] for r in rows] == [u.DESCRIBE_Q, u.WHO_Q, u.WHERE_Q]
    assert all(r.get("child") for r in rows)
    assert rows[1]["answer"] == "It is a photo by X College."
    graphic = u.stream_rows("Students help clear debris after the storm that injured two.", spec, "c",
                            "storm injured two")
    assert all(r.get("content") == "graphic" for r in graphic)
    country = u.stream_rows("Postcard of a grain elevator beside the railway track.",
                            u.stream("C", "a library", "Canada", 1, "."), "c", "", who_row=False)
    assert [r["question"] for r in country] == [u.DESCRIBE_Q]


def test_college_caption():
    """File-name notes and credit lines go; a caption that only repeats the file name is too short."""
    raw = ("13399-Homecoming Tailgate and Game-1778.jpg Scenes from the homecoming tailgate before the football "
           "game on November 2. Photo by Jane Doe.")
    cap = u.college_caption(raw, "File:13399-Homecoming Tailgate and Game-1778 (10714728646).jpg")
    assert cap.startswith("Scenes from the homecoming tailgate") and "Jane Doe" not in cap and ".jpg" not in cap
    assert not u.long_enough(u.college_caption("2013 CCV Graduation", "File:2013 CCV Graduation (9026805800).jpg"),
                             "File:2013 CCV Graduation (9026805800).jpg")
    assert not u.long_enough(u.college_caption("_97A8288", "File:97A8288 (41831866431).jpg"), "File:97A8288.jpg")
    assert not u.long_enough("Wade Henderson and Stephen B. Bright.", "File:25th Rauh Lecture.jpg")
    assert u.long_enough("Students shop in the college bookstore for hockey shirts.", "File:Frozen Four 2014.jpg")


def test_archive_caption():
    """A library record written into a Commons description: its title and description, not its fields."""
    raw = ("Title: Basketball Pavilion Creator: Hester, Joseph Neland, 1883-1961 Date: 1927 Place: Dallas, Texas "
           "Description: Pictured is the Basketball Pavilion, a temporary wooden building on the campus.")
    assert u.archive_caption(raw, "File:Basketball Pavilion (15479665712).jpg") == (
        "Basketball Pavilion. Pictured is the Basketball Pavilion, a temporary wooden building on the campus.")
    uw = ("Chief Seattle fountain covered in snow, Pioneer Square, Seattle, Washington, n.d. Photographer: Unknown "
          "Subjects (LCSH): Chief Seattle Fountain (Seattle, Wash.)")
    assert u.archive_caption(uw, "File:X.jpg") == "Chief Seattle fountain covered in snow, Pioneer Square, Seattle, " \
                                                  "Washington."
    miami = ("Persistent URL: digital.lib.muohio.edu/u?/snyder,55 Subject (TGM): Football; Sports; Location: Oxford")
    cap = u.archive_caption(miami, "File:Action at Miami-Ohio Wesleyan football game 1921 (3191452100).jpg")
    assert cap == "Action at Miami-Ohio Wesleyan football game."


def test_is_open():
    """Public domain, CC0 and CC BY; "No restrictions" only where allowed; never SA, NC or ND."""
    assert u.is_open("CC BY 2.0") and u.is_open("Public domain") and u.is_open("CC0")
    assert not u.is_open("CC BY-SA 2.0") and not u.is_open("CC BY-NC 2.0") and not u.is_open("CC BY-ND 4.0")
    assert not u.is_open("No restrictions") and u.is_open("No restrictions", no_known_ok=True)


def test_dpla_without_key(monkeypatch):
    """No key: the open pack makes nothing and says so."""
    monkeypatch.delenv("DPLA_API_KEY", raising=False)
    assert u.build_dpla_campus(5) == []


def test_kit_entries(monkeypatch):
    """The kit's DPLA entries: their rights only, never NoDerivatives; the answer and picture; no key, nothing."""
    import university_sources as k
    assert k.SA_RIGHTS.match("http://creativecommons.org/licenses/by-sa/4.0/")
    assert not k.SA_RIGHTS.match("http://creativecommons.org/licenses/by/4.0/")
    assert k.NC_RIGHTS.match("http://creativecommons.org/licenses/by-nc/3.0/")
    assert k.NC_RIGHTS.match("http://creativecommons.org/licenses/by-nc-sa/4.0/")
    assert not k.NC_RIGHTS.match("http://creativecommons.org/licenses/by-nc-nd/4.0/")
    d = doc()
    assert k.dpla_answer(d["sourceResource"]).startswith("Students studying in the library reading room.")
    assert k.dpla_answer({"title": ["Campus"]}) == ""
    assert k.dpla_picture(d) == "https://cdm.example.edu/iiif/2/photos:42/full/!1600,1600/0/default.jpg"
    assert k.dpla_place(d["sourceResource"]) == "Denton, Texas, USA"
    assert k.LEFT_OUT.search("Summer camp at the lake") and k.LEFT_OUT.search("yearbook portrait")
    assert not k.LEFT_OUT.search("Students walk across the campus quad")
    monkeypatch.delenv("DPLA_API_KEY", raising=False)
    assert k.prepare_dpla(k.UNIVERSITY_SOURCES[0], "/nonexistent", k.SA_RIGHTS, "x", 1) == []
    assert not k.UNIVERSITY_PICTURE_MAKING_OK


def test_archive_streams_leave_out_printed_matter():
    """Book pages, documents and printed matter in the library collections are not scenes."""
    import re
    skip = re.compile(u.NOT_A_SCENE, re.I)
    assert skip.search("File:First Folio- As You Like It, p. 22 (22795586632).jpg")
    assert skip.search("File:Commencement program 1925.jpg")
    assert not skip.search('File:"Hoar Frost" Edmonton, Alberta.jpg')
    assert all(s["skip"] is not None for s in u.ARCHIVE_STREAMS)


def test_postcard_notes_and_library_titles():
    """Peel's postcard notes are cut off; a library title that is also the file's name is accepted."""
    raw = ("Image of 7th Avenue in Virden with overlaid maple leaves and a flag in the corner. Notes Other: Glossy "
           "print post card.")
    assert u.archive_caption(raw, "File:7th Avenue, Virden, Man..jpg") == (
        "Image of 7th Avenue in Virden with overlaid maple leaves and a flag in the corner.")
    title = "File:Action at the Miami-Ohio Wesleyan football game 1921 (3191452100).jpg"
    cap = "Action at the Miami-Ohio Wesleyan football game."
    assert not u.long_enough(cap, title) and u.long_enough(cap, title, name_ok=True)
