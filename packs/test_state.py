"""A self-test of the state-government parsers (packs/state_packs.py and training-kit/kit/state_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - a state or city caption loses its "Photo:" and credit lines, a Guard photo's ID number and an archive's record
    fields, and keeps the words about the picture;
  - photos are left out for official events, crime and victims, nudity, a date before 1990, and (in the emergency
    pack) when no emergency is named;
  - a photo's rows name its agency and place, and are marked "child" and "graphic" from its words;
  - the pack builder keeps only the agency's own photos (by the author line), sets a photo with a too-short caption
    aside for a description, and leaves out an official event (the Commons calls are replaced by made-up answers);
  - the tables agree (every pack has a limit, the kit entry is share-alike, the state table has 50 states, DC and
    Puerto Rico).

Run it from the repository's folder:   python3 -m pytest packs/test_state.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import state_packs as m  # noqa: E402


def test_state_caption():
    """Credit lines, "Photo:" lines, Guard ID numbers and archive record fields are taken out."""
    assert m.state_caption("Snow removal at Hogg Rock on US 26 near Government Camp. Photo: ODOT") == \
        "Snow removal at Hogg Rock on US 26 near Government Camp."
    assert m.state_caption("California Condor in flight over the Big Sur Coast. CDFW photo by Carie Battistone.") == \
        "California Condor in flight over the Big Sur Coast."
    assert m.state_caption("Title: A crew paints lane lines on Boylston Street in the rain. Creator: City "
                           "Photographer Date: 1998 Source: Collection #0246.001 Copyright: City of Boston") == \
        "A crew paints lane lines on Boylston Street in the rain."
    assert m.state_caption("Workers repair a pothole on Interstate 5 (Marc A. Hermann / MTA New York City "
                           "Transit).") == "Workers repair a pothole on Interstate 5."
    assert m.state_caption("170724-Z-WE055-010") == ""
    assert m.state_caption("Photo: Meadow Bailey") == ""
    assert m.english("Snowplow clears Highway 26 near Government Camp")
    assert not m.english("Le chasse-neige dégage la route et les voitures")


def test_why_not():
    """Official events, crime, nudity, old photos and (emergency pack) no emergency are left out."""
    assert "official" in m.why_not("Gov. Roy Cooper speaks at the maintenance yard", 2022, False)
    assert "official" in m.why_not("Ribbon cutting for the new I-485 express lanes", 2026, False)
    assert "crime" in m.why_not("Troopers arrest a suspect after a chase", 2019, False)
    assert "nudity" in m.why_not("Swimmers at the state park beach", 2019, False)
    assert "1990" in m.why_not("Snowplow on US 26", 1987, False)
    assert "1990" in m.why_not("Gas Works Park, circa 1979", 0, False)
    assert m.why_not("NCDOT truck plowing snow along US 421 in Watauga County.", 2026, False) == ""
    assert m.why_not("Soldiers fill sandbags as the Arkansas River floods in Fort Smith", 2019, True) == ""
    assert "emergency" in m.why_not("Soldiers train on the range at Camp Ripley", 2019, True)
    # Seen in the Minnesota Guard's stream: training whose words have "fire" or "Fires" in them.
    assert "emergency" in m.why_not("M109A6 155mm Howitzer Crews of the 1st Battalion-125th Field Artillery move into "
                                    "position for a battalion fire mission during training", 2017, True)
    assert "emergency" in m.why_not("A healthcare specialist with HHB, 2-142nd Fires Brigade, puts on his gear for "
                                    "the Best Warrior Competition", 2017, True)
    assert m.why_not("Guardsmen hand out bottled water at a water distribution site after the flood", 2019, True) == ""
    assert m.state_caption("Shiras Bull Moose (low resolution only).") == "Shiras Bull Moose."
    # Seen in the Oregon Guard's stream: a memorial event that names firefighters.
    assert "emergency" in m.why_not("9/11 Memorial Stair Climb is a tribute to the 343 firefighters who gave their "
                                    "lives", 2025, True)
    assert m.why_not("Firefighting crews from the Oregon National Guard battle the Holiday Farm wildfire", 2020,
                     True) == ""


def test_picture_names():
    """Two long titles that differ only at their end get different file names."""
    a = "File:9-11 Memorial Stair Climb at Autzen Stadium, Eugene, Oregon on September 11, 2025 - 1.jpg"
    b = "File:9-11 Memorial Stair Climb at Autzen Stadium, Eugene, Oregon on September 11, 2025 - 2.jpg"
    assert m.picture_name("stresp", a) != m.picture_name("stresp", b)
    assert m.picture_name("stresp", a).startswith("stresp-9-11_Memorial") and m.picture_name("x", a).endswith(".jpg")


def test_credit_parts():
    """The author and licence are read back from an agency_entries credit line."""
    credit = ("File:Snow removal (1).jpg by Oregon Department of Transportation, CC BY 2.0, "
              "https://commons.wikimedia.org/wiki/File:Snow_removal_(1).jpg")
    assert m.author_of(credit) == "Oregon Department of Transportation"
    assert m.licence_of(credit) == "CC BY 2.0"


def test_state_rows_marks():
    """The rows name the agency and place; a child and the injured are marked."""
    spec = m.ROADS[0]
    rows = m.state_rows("A crew clears a rockslide on Highway 38.", spec, "credit", "a crew clears a rockslide")
    assert rows[1] == {"question": m.WHO_Q, "answer": f"It is a photo by {spec['who']}.", "credit": "credit",
                       "place": "Oregon, USA", "place_kind": "origin"}
    assert not any(r.get("child") or r.get("content") for r in rows)
    rows = m.state_rows("Two injured drivers are helped from a crash.", spec, "credit", "two injured drivers")
    assert all(r["content"] == "graphic" for r in rows)
    rows = m.state_rows("A girl holds a turtle at a ranger program.", m.OUTDOORS[0], "credit", "a girl holds a turtle")
    assert all(r.get("child") for r in rows)


def test_agency_pack_logic(monkeypatch):
    """The builder keeps the agency's own photos, sets a short caption aside and leaves out official events."""
    page = "https://commons.wikimedia.org/wiki/File:"
    entries = [
        ("File:A.jpg", "u-a", f"File:A.jpg by Oregon Department of Transportation, CC BY 2.0, {page}A.jpg",
         "A snowplow clears Highway 26 near Government Camp after a storm.", 2019),
        ("File:B.jpg", "u-b", f"File:B.jpg by Some Visitor, CC BY 2.0, {page}B.jpg",
         "A snowplow clears Highway 26 near Government Camp after a storm.", 2019),
        ("File:C.jpg", "u-c", f"File:C.jpg by Oregon Department of Transportation, CC BY 2.0, {page}C.jpg",
         "Bridge work", 2018),
        ("File:D.jpg", "u-d", f"File:D.jpg by Oregon Department of Transportation, CC BY 2.0, {page}D.jpg",
         "Governor Kate Brown speaks at a press conference about the new bridge.", 2018),
    ]
    monkeypatch.setattr(m, "session", lambda: None)
    monkeypatch.setattr(m, "sample_members", lambda s, category, pages, rng: [e[0] for e in entries])
    monkeypatch.setattr(m, "agency_entries", lambda s, titles: [e for e in entries if e[0] in titles])
    monkeypatch.setattr(m, "commons_fetch", lambda items: [(name, b"jpeg", rows) for name, _, rows in items])
    build_packs.reset_needs()
    out = m.agency_pack(m.ROADS[:1], 4, "commons_state_roads", "stroad")
    pictures = [(name, row) for name, data, row in out if data]
    assert [name for name, _ in pictures] == [m.picture_name("stroad", "File:A.jpg")]
    assert pictures[0][1]["answer"] == "A snowplow clears Highway 26 near Government Camp after a storm."
    assert pictures[0][1]["place"] == "Oregon, USA"
    assert [n["name"] for n in build_packs.NEEDS] == [m.picture_name("stroad", "File:C.jpg")]
    assert build_packs.NEEDS[0]["licence"] == "CC BY 2.0" and build_packs.NEEDS[0]["not_for_picture_making"]
    build_packs.reset_needs()


def test_tables():
    """Every pack has a builder, a credit and a limit; the kit's entry is share-alike; the state table is whole."""
    assert set(m.STATE_PACKS) == set(m.STATE_LIMITS)
    assert all(spec["pages"] >= 1 for specs in (m.ROADS, m.OUTDOORS, m.RESPONSE, m.COMMUNITY) for spec in specs)
    import state_sources as k
    assert {s.group for s in k.STATE_SOURCES} <= {"share-alike", "noncommercial", "research"}
    assert k.STATE_PICTURE_MAKING_OK <= {s.key for s in k.STATE_SOURCES}
    assert len(k.STATE_SUMMARY) == 52 and "Puerto Rico" in k.STATE_SUMMARY
    assert all(set(v) <= set(k.AGENCY_KINDS) for v in k.STATE_SUMMARY.values())
    assert k.summary_table().count("\n") == 53


def test_kit_left_out():
    """The share-alike entry leaves out old, official, crime and nude files by their words."""
    import state_sources as k
    assert k.left_out("Streetcars at Ashmont station, circa 1947")
    assert k.left_out("Mayor Raymond L. Flynn at City Hall")
    assert k.left_out("Gov. Smith rides the new bus")
    assert not k.left_out("Hybrid buses at the Knoxville Station transit center")
