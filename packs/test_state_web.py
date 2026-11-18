"""A self-test of the state-website parsers (packs/state_web_packs.py and training-kit/kit/state_web_sources.py), with
made-up records only: nothing is downloaded from the internet.

It checks that:
  - a Caltrans camera name loses its camera codes, and a camera list keeps only cameras in service with pictures;
  - a camera picture's rows say only what the camera list says (route, place, county, district, name, direction);
  - a camera entry with neither a route nor a place gives no rows (it is set aside);
  - "Temporarily Unavailable" cards and blank frames are recognised, and a real view is not;
  - the picks spread over the districts and stay near the limit;
  - the builder sets aside a camera with no route or place, leaves out a placeholder and a repeated picture
    (the downloads are replaced by made-up pictures);
  - TripCheck's camera list keeps ODOT's cameras and leaves out the city and county ones;
  - Washington Ecology's rows come from the photo's landmark, county and date, and photos before 1990 are left out;
  - the tables agree (every pack has a limit; the kit's groups and picture-making list are right; every record line
    has its terms URL, robots.txt result and result).

Run it from the repository's folder:   python3 -m pytest packs/test_state_web.py
"""

import io
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(HERE, "..", "training-kit", "kit"))
import build_packs  # noqa: E402,F401 - loaded first, as the builders expect
import state_web_packs as m  # noqa: E402


def jpeg(kind):
    """A made-up 320 x 260 camera picture: "view" (a grey road with stripes), "card" (white with a dark strip at the
    bottom, like Caltrans' "Temporarily Unavailable" card) or "blank" (one flat shade)."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (320, 260), (128, 128, 128) if kind != "card" else (255, 255, 255))
    draw = ImageDraw.Draw(img)
    if kind == "view":
        for x in range(0, 320, 20):
            draw.rectangle((x, 0, x + 8, 220), fill=(30, 30, 30))
            draw.rectangle((x + 10, 100, x + 14, 220), fill=(240, 240, 240))
    if kind == "card":
        draw.rectangle((0, 235, 320, 260), fill=(40, 40, 40))
        draw.text((60, 100), "Temporarily Unavailable", fill=(20, 20, 120))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=90)
    return out.getvalue()


def camera(name, route="I-580", place="Oakland", county="Alameda", direction="West", service="true", stills=True):
    """A made-up camera entry in Caltrans' JSON layout."""
    base = "https://cwwp2.dot.ca.gov/data/d4/cctv/image/tvtest/"
    static = {"currentImageURL": base + "tvtest.jpg" if stills else ""}
    if stills:
        static.update({("referenceImage1UpdateAgoURL" if k == 1 else f"referenceImage{k}UpdatesAgoURL"):
                       f"{base}previous/tvtest-{k}.jpg" for k in range(1, 13)})
    return {"cctv": {"index": "1", "inService": service,
                     "location": {"locationName": name, "route": route, "nearbyPlace": place, "county": county,
                                  "direction": direction},
                     "imageData": {"imageDescription": "", "static": static}}}


def test_caltrans_name():
    """Camera codes are taken out of Caltrans' camera names."""
    assert m.caltrans_name("TV102 -- I-580 : West of SR-24") == "I-580 : West of SR-24"
    assert m.caltrans_name("(C105)I-5 : Dairy Mart Road") == "I-5 : Dairy Mart Road"
    assert m.caltrans_name("SR-91 : (541) Carmenita Ave") == "SR-91 : Carmenita Ave"
    assert m.caltrans_name("68 - NB SR-99 S/O Mariposa Way") == "NB SR-99 S/O Mariposa Way"
    assert m.caltrans_name("(C 348) SR-163 : Friars N/E_B") == "SR-163 : Friars N/E_B"
    assert m.caltrans_name("SR-20 : At SR-1 - Looking East (C020)") == "SR-20 : At SR-1 - Looking East"
    assert m.caltrans_name("Hwy 99 at Mack") == "Hwy 99 at Mack"


def test_caltrans_cameras_and_rows():
    """Only cameras in service with pictures are kept; the rows say only what the list says."""
    data = {"data": [camera("TV102 -- I-580 : West of SR-24"), camera("Out of service", service="false"),
                     camera("No pictures", stills=False)]}
    cams = m.caltrans_cameras(data, 4)
    assert len(cams) == 1 and len(cams[0]["urls"]) == 13 and cams[0]["direction"] == "west"
    rows = m.caltrans_rows(cams[0], "credit")
    assert rows[0]["question"] == "Describe this picture."
    assert rows[0]["answer"] == ('A traffic camera view of a highway: I-580 near Oakland, Alameda County, California. '
                                 'Caltrans lists the camera as "I-580 : West of SR-24". Its listed direction is west.')
    assert rows[1]["answer"].startswith("On I-580 near Oakland, Alameda County, California (Caltrans district 4).")
    assert rows[2]["answer"] == m.CALTRANS_WHO
    assert all(r["place"] == "California, USA" and r["credit"] == "credit" for r in rows)
    bare = m.caltrans_cameras({"data": [camera("Somewhere", route="", place="", direction="Median")]}, 2)[0]
    assert bare["direction"] == "" and m.caltrans_rows(bare, "credit") == []


def test_placeholder():
    """Cards and blank frames are placeholders; a road view is not."""
    assert m.placeholder(jpeg("card"))
    assert m.placeholder(jpeg("blank"))
    assert m.placeholder(b"not a picture")
    assert not m.placeholder(jpeg("view"))


def test_picks_spread():
    """The picks take turns over the districts and stay near the limit."""
    cams = []
    for d in (1, 4, 7):
        cams += [{"id": f"d{d}-{i}", "district": d, "urls": [f"u{d}-{i}-{k}" for k in range(13)]} for i in range(50)]
    picks = m.caltrans_picks(cams, 30, random.Random(1))
    assert 30 <= len(picks) <= 30 * 1.3 + 4
    assert {cam["district"] for cam, _ in picks[:3]} == {1, 4, 7}
    assert len({cam["id"] for cam, _ in picks}) == len(picks)     # one picture per camera when cameras are plenty


def test_builder(monkeypatch):
    """The builder sets aside a camera with no route or place and leaves out placeholders and repeats."""
    class Answer:
        """A made-up answer to the camera list request."""
        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            """Nothing goes wrong."""

        def json(self):
            """The made-up list."""
            return self.data

    lists = {4: {"data": [camera("TV1 -- I-80 : Bay Bridge", route="I-80", place="Oakland"),
                          camera("TV2 -- I-880 : Broadway", route="I-880", place="Oakland"),
                          camera("TV3 -- I-580 : Grand Ave", route="I-580", place="Oakland"),
                          camera("Nowhere", route="", place="")]}}
    for n, entry in enumerate(lists[4]["data"]):           # each camera its own picture addresses
        static = entry["cctv"]["imageData"]["static"]
        for key in static:
            static[key] = static[key].replace("tvtest", f"tv{n}")

    class Session:
        """Made-up requests: the district list only."""
        def get(self, url, timeout=0):
            """The list of district 4."""
            return Answer(lists[4])

    pictures = iter([jpeg("view"), jpeg("card"), jpeg("view"), jpeg("view")])

    def fake_fetch(items, workers=1, pause=0.0):
        """Made-up downloads: a view, a card, the same view again, another view (changed by one pixel)."""
        out = []
        for i, (name, url, rows) in enumerate(items):
            data = next(pictures, None)
            if data is None:
                break
            if i == 3:
                from PIL import Image
                img = Image.open(io.BytesIO(data))
                img.putpixel((0, 0), (0, 0, 0))
                buf = io.BytesIO()
                img.save(buf, "JPEG", quality=95)
                data = buf.getvalue()
            out.append((name, data, rows))
        return out

    monkeypatch.setattr(m, "CALTRANS_DISTRICTS", (4,))
    monkeypatch.setattr(m, "PAUSE", 0)
    monkeypatch.setattr(m, "session", lambda: Session())
    monkeypatch.setattr(m, "fetch_all", fake_fetch)
    build_packs.reset_needs()
    out = m.build_caltrans_cctv(5)
    with_picture = [(name, row) for name, data, row in out if data]
    assert len(with_picture) == 2                            # the card and the repeat are left out
    assert all(row["question"] == "Describe this picture." for _, row in with_picture)
    assert len(out) == 6                                     # three rows each
    assert [n["reason"] for n in build_packs.NEEDS] == ["its camera entry names neither a route nor a place"]
    assert build_packs.NEEDS[0]["not_for_picture_making"]
    assert all("?t=" in n["url"] for n in build_packs.NEEDS)
    build_packs.reset_needs()


def test_tripcheck_cameras():
    """ODOT's cameras are kept; city and county cameras are left out; rows come from the list."""
    import state_web_sources as k
    data = {"features": [
        {"attributes": {"cameraId": 157, "filename": "217allen_pid404.jpg", "route": "OR217 ", "title": "OR217 at Allen"}},
        {"attributes": {"cameraId": 2, "filename": "a.JPG", "route": "CITY  ", "title": "Salem - Center and 17th"}},
        {"attributes": {"cameraId": 3, "filename": "b.jpg", "route": "OR213 ", "title": "Portland - 82nd Ave at Sandy"}},
        {"attributes": {"cameraId": 4, "filename": "c.jpg", "route": "CNTY  ", "title": "Clackamas Co - Harmony Rd"}},
        {"attributes": {"cameraId": 5, "filename": "US101 at Astoria_pid392.jpg", "route": "US101 ",
                        "title": "US101 at Astoria - ODOT District Office"}},
    ]}
    cams = k.tripcheck_cameras(data)
    assert [c["id"] for c in cams] == ["157", "5"]
    rows = k.tripcheck_rows(cams[0])
    assert rows[0]["answer"] == "A traffic camera view of a highway: OR217 at Allen, Oregon."
    assert rows[2]["answer"] == k.TRIPCHECK_WHO and rows[0]["credit"].startswith("Camera courtesy of ODOT")
    assert all(r["split"] == "" for r in rows)


def test_ecology_rows():
    """Ecology's rows come from the landmark, county and date; old or incomplete photos give none."""
    import state_web_sources as k
    record = {"PHOTO_NR": "PAC0619", "Vintage": 1990, "COUNTY_NM": "Pacific", "LANDMARK_DS": "Columbia River",
              "PHOTO_DATE": "5/13/1997",
              "FULLSIZE_URL": "https://fortress.wa.gov/ecy/gisresources/shoreline_photos/yr1990/fullsize/PAC0619.jpg"}
    rows = k.ecology_rows(record)
    assert rows[0]["answer"] == ("An oblique aerial photo of the Washington State shoreline: Columbia River, in Pacific "
                                 "County, Washington, taken on 13 May 1997.")
    assert rows[1]["answer"] == "On the marine shoreline of Washington State: Columbia River, in Pacific County, Washington."
    assert "non-commercial" in rows[0]["credit"]
    assert k.ecology_rows(dict(record, Vintage=1970, PHOTO_DATE="6/1/1977")) == []
    assert k.ecology_rows(dict(record, COUNTY_NM="")) == []
    assert k.ecology_rows(dict(record, FULLSIZE_URL="")) == []
    assert k.ecology_date("13/45/2000") == ("", 0)
    assert k.placeholder_file(os.path.join(HERE, "no-such-file.jpg"))


def test_tables():
    """Every pack has a builder, a credit and a limit; the kit's groups and lists agree; the record is whole."""
    assert set(m.STATE_WEB_PACKS) == set(m.STATE_WEB_LIMITS)
    import state_web_sources as k
    groups = {s.key: s.group for s in k.STATE_WEB_SOURCES}
    assert groups == {"tripcheck_cameras": "permissive", "wa_ecology_shoreline_nc": "noncommercial"}
    assert k.STATE_WEB_PICTURE_MAKING_OK <= set(groups) and "tripcheck_cameras" not in k.STATE_WEB_PICTURE_MAKING_OK
    assert all(s.terms.startswith("https://") and s.terms_summary for s in k.STATE_WEB_SOURCES)
    keys = ("state", "agency", "site", "offers", "terms", "terms_url", "robots", "result")
    assert all(set(e) == set(keys) and all(e[x] for x in keys) for e in k.STATE_WEB_RECORD)
    results = " ".join(e["result"] for e in k.STATE_WEB_RECORD)
    assert "caltrans_cctv" in results and "tripcheck_cameras" in results and "wa_ecology_shoreline_nc" in results
    assert k.record_table().count("\n") == len(k.STATE_WEB_RECORD) + 1
