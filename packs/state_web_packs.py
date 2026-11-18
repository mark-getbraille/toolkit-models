"""Pack builders for US STATE GOVERNMENT pictures taken from the agencies' OWN websites and data feeds (not from
Wikimedia Commons copies, which are packs/state_packs.py). Used by build_packs.py in the same way as its own PACKS:
each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "place" and "place_kind". A picture with more than one question comes once with its JPEG
and then again as (None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts
pictures.

WHAT WAS LOOKED FOR (November 2026). State agencies' own photo galleries, photo libraries, open-data portals (Socrata,
CKAN and ArcGIS Hub) and the still pictures of state traffic cameras, in the two states whose government works are
public domain by their own courts (California and Florida) and, elsewhere, wherever an agency put an open licence on
its pictures. Each site's terms page and robots.txt were read first. The full state-by-state record, with the terms
lines and the reasons each one was or was not used, is in training-kit/kit/state_web_sources.py (STATE_WEB_RECORD).
Only one source passed every test for an open pack:

  caltrans_cctv   Still pictures from the California Department of Transportation's (Caltrans) highway traffic
                  cameras, about 3,400 cameras in all twelve Caltrans districts, listed in Caltrans' own data feed
                  (the Commercial Wholesale Web Portal, https://cwwp2.dot.ca.gov/documentation/cctv/cctv.htm: "These
                  files are available for integration into your application ... There is no charge for the use of
                  this data"). Each camera offers its current picture and twelve earlier ones, so one build already
                  spreads over several hours of the day; later top-up passes, run on other days, add other hours,
                  seasons and weather. Licence: public domain. California's courts hold that a state agency cannot
                  claim copyright in a public record unless a law allows it (County of Santa Clara v. Superior Court,
                  170 Cal. App. 4th 1301, 2009; Commons' tag {{PD-CAGov}}, whose list of agencies allowed to claim
                  copyright does not include Caltrans), and Caltrans' own Conditions of Use
                  (https://dot.ca.gov/conditions-of-use) say: "In general, information presented on this website,
                  unless otherwise indicated, is considered in the public domain. It may be distributed or copied as
                  permitted by law." The camera pictures are made by Caltrans' own cameras, not by a private
                  photographer. robots.txt: cwwp2.dot.ca.gov serves none (the address answers an error), and
                  dot.ca.gov serves none (404), so nothing is disallowed. Caltrans says its camera "still images are
                  neither retained nor archived"; that is its own practice, not a limit on others.

HOW IT IS POLITE. One request at a time, a pause of three seconds before each (fetch_all with one worker), the
kit's User-Agent (build_packs.USER_AGENT, which names the project and its web page, not a person). A full build of
2,000 pictures takes about two hours.

WHAT THE ANSWERS SAY. Only what Caltrans' own camera list says (its route, the nearest place, the county, the district,
the camera's name and its listed direction) and the fixed words "a traffic camera view of a highway". Nothing is
written by an AI model and nothing is guessed (not the weather, the time or the traffic). A camera whose list entry has
neither a route nor a place is set aside for a description (build_packs.needs_description).

WHAT IS LEFT OUT. "Temporarily Unavailable" cards and blank frames (placeholder), a picture already taken from the same
camera in this build (the same bytes), cameras Caltrans lists as out of service. The pictures are small (320 by 260
pixels), taken from poles above the road: people are distant and number plates cannot be read at this size. All the
same the pack shows roads with people in their cars and on foot, so it is never used for picture-making (wire it into
the kit's PEOPLE_AND_BODILY_PACK_KEYS).

    python packs/state_web_packs.py caltrans_cctv --limit 4      (prints a few rows: a quick check)
"""

import collections
import hashlib
import io
import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, say, considered, needs_description, pass_random, fetch_all, listing_out_of_time
from food_packs import with_twins, count_pictures
from us_packs import DESCRIBE_Q

PAUSE = 3.0                 # seconds before each request to an agency's server
WHO_Q = "Who took this photo?"
WHERE_Q = "Where is this traffic camera?"

# ----------------------------------------------------------------- Caltrans traffic cameras

CALTRANS_LIST = "https://cwwp2.dot.ca.gov/data/d{d}/cctv/cctvStatusD{d:02d}.json"
CALTRANS_DOCS = "https://cwwp2.dot.ca.gov/documentation/cctv/cctv.htm"
CALTRANS_TERMS = "https://dot.ca.gov/conditions-of-use"
CALTRANS_DISTRICTS = tuple(range(1, 13))
CALTRANS_WHO = "It is a still picture from a California Department of Transportation (Caltrans) traffic camera."
CALTRANS_LICENCE = "public domain (California public record; Caltrans Conditions of Use)"
# Camera codes Caltrans puts in front of or after a camera's name: "TV102 --", "(C105)", "(C 348)", "68 - ",
# "(541)", "(C020)".
CODE_FRONT = re.compile(r"^\s*(\(\s*C\s*\d+\s*\)\s*|T[A-Z]{0,2}\d+[A-Z]?\s*--\s*|\d{1,4}\s+-\s+|C\d+\s*-\s+)", re.I)
CODE_ANY = re.compile(r"\(\s*(C\s*)?\d+\s*\)", re.I)
DIRECTIONS = {"north": "north", "south": "south", "east": "east", "west": "west"}


def caltrans_name(name):
    """A Caltrans camera name without its camera codes ("TV102 -- I-580 : West of SR-24" -> "I-580 : West of SR-24";
    "(C105)I-5 : Dairy Mart Road" -> "I-5 : Dairy Mart Road"); "" when nothing is left."""
    text = CODE_FRONT.sub("", name or "")
    text = CODE_ANY.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip(" -:")
    return re.sub(r"\s+:\s+", " : ", text)


def caltrans_cameras(data, district):
    """The cameras of one district's list (Caltrans' JSON, as read): [{"id", "name", "route", "place", "county",
    "direction", "district", "urls"}] for each camera in service with pictures; "urls" holds the current picture and
    the earlier ones Caltrans keeps (up to twelve)."""
    cameras = []
    for entry in (data or {}).get("data", []):
        cam = entry.get("cctv") or {}
        if str(cam.get("inService", "")).lower() != "true":
            continue
        loc = cam.get("location") or {}
        still = (cam.get("imageData") or {}).get("static") or {}
        urls = [still.get("currentImageURL", "")]
        urls += [still.get(f"referenceImage{k}UpdateAgoURL" if k == 1 else f"referenceImage{k}UpdatesAgoURL", "")
                 for k in range(1, 13)]
        urls = [u for u in urls if u.startswith("https://")]
        if not urls:
            continue
        ident = re.sub(r"\W+", "", urls[0].rsplit("/", 1)[-1].rsplit(".", 1)[0])[:40] or f"cam{cam.get('index')}"
        cameras.append({"id": f"d{district}-{ident}", "name": caltrans_name(loc.get("locationName", "")),
                        "route": (loc.get("route") or "").strip(), "place": (loc.get("nearbyPlace") or "").strip(),
                        "county": (loc.get("county") or "").strip(),
                        "direction": DIRECTIONS.get((loc.get("direction") or "").strip().lower(), ""),
                        "district": district, "urls": urls})
    return cameras


def caltrans_rows(cam, credit):
    """The rows of one camera picture, from the camera's own list entry only: a description, where the camera is,
    and who made the picture. [] when the entry names neither a route nor a place (set aside instead)."""
    if not cam["route"] and not cam["place"]:
        return []
    where = cam["route"] or "a state highway"
    if cam["place"]:
        where += f" near {cam['place']}"
    if cam["county"]:
        where += f", {cam['county']} County"
    where += ", California"
    named = f' Caltrans lists the camera as "{cam["name"]}".' if cam["name"] else ""
    facing = f" Its listed direction is {cam['direction']}." if cam["direction"] else ""
    base = {"credit": credit, "place": "California, USA", "place_kind": "origin"}
    return [
        dict(base, question=DESCRIBE_Q, answer=f"A traffic camera view of a highway: {where}.{named}{facing}"),
        dict(base, question=WHERE_Q, answer=f"On {where} (Caltrans district {cam['district']}).{named}"),
        dict(base, question=WHO_Q, answer=CALTRANS_WHO),
    ]


def placeholder(data):
    """True when a camera picture is a "Temporarily Unavailable" card or a blank frame: most of the picture (above the
    date strip at the bottom) is near white, or the whole picture is one flat shade. Pictures that cannot be read
    count as placeholders."""
    from PIL import Image, ImageStat
    try:
        img = Image.open(io.BytesIO(data)).convert("L")
    except Exception:  # noqa: BLE001 - not a picture
        return True
    width, height = img.size
    top = img.crop((0, 0, width, max(1, int(height * 0.85))))
    counts = top.histogram()                    # how many pixels of each shade, 0 (black) to 255 (white)
    white = sum(counts[225:]) / max(1, sum(counts))
    return white > 0.55 or ImageStat.Stat(img).stddev[0] < 6


def caltrans_picks(cameras, limit, rng):
    """Which pictures to take: (camera, picture number) pairs spread over the districts and over the cameras'
    current and earlier pictures. Each camera gives one picture, or more when the limit is larger than the cameras;
    the districts take turns so no district fills the pack."""
    if not cameras:
        return []
    each = max(1, -(-int(limit * 1.3) // len(cameras)))
    by_district = collections.defaultdict(list)
    for cam in cameras:
        numbers = list(range(len(cam["urls"])))
        rng.shuffle(numbers)
        by_district[cam["district"]] += [(cam, k) for k in numbers[:each]]
    for picks in by_district.values():
        rng.shuffle(picks)
    order, queues = [], [by_district[d] for d in sorted(by_district)]
    while any(queues):
        for q in queues:
            if q:
                order.append(q.pop())
    return order[:int(limit * 1.3) + 4]


def build_caltrans_cctv(limit):
    """Caltrans traffic camera stills (see the module notes)."""
    s, rng = session(), pass_random("caltrans_cctv")
    cameras = []
    for district in CALTRANS_DISTRICTS:
        if listing_out_of_time():
            break
        time.sleep(PAUSE)
        try:
            r = s.get(CALTRANS_LIST.format(d=district), timeout=120)
            r.raise_for_status()
            got = caltrans_cameras(r.json(), district)
        except Exception as e:  # noqa: BLE001 - a district that cannot be read is left out
            say(f"Caltrans district {district}: its camera list could not be read ({type(e).__name__})")
            continue
        say(f"Caltrans district {district}: {len(got)} cameras in service")
        cameras += got
    stamp = time.strftime("%Y%m%d%H", time.gmtime())
    items, aside = [], set()
    for cam, k in caltrans_picks(cameras, limit, rng):
        url = cam["urls"][k]
        name = f"caltrans-{cam['id']}-{stamp}-{k:02d}.jpg"
        credit = (f"Caltrans traffic camera {cam['name'] or cam['id']}, California Department of Transportation, "
                  f"{CALTRANS_LICENCE}, {CALTRANS_DOCS}")
        rows = caltrans_rows(cam, credit)
        # The address names a still that Caltrans replaces every few minutes: the hour of this build is added, so a
        # top-up pass on another day does not take it for a picture the pack already has (the server ignores it).
        fresh = f"{url}?t={stamp}"
        if not rows:
            if cam["id"] in aside:                  # one picture of such a camera is enough to describe
                continue
            aside.add(cam["id"])
            needs_description(name, fresh, credit, "public domain", text=cam["name"], title=cam["id"],
                              reason="its camera entry names neither a route nor a place", place="California, USA",
                              place_kind="origin", page_url=CALTRANS_DOCS,
                              extra={"county": cam["county"], "district": cam["district"],
                                     "not_for_picture_making": True})
            continue
        items.append((name, fresh, rows))
    say(f"caltrans_cctv: {len(items)} pictures to fetch from {len(cameras)} cameras")
    fetched, seen = [], set()
    for name, data, rows in fetch_all(items, workers=1, pause=PAUSE):
        digest = hashlib.sha1(data).hexdigest()
        if digest in seen:
            considered(name, "", "the same picture as one already taken from this camera")
            continue
        if placeholder(data):
            considered(name, "", "a 'Temporarily Unavailable' card or a blank frame, not a camera view")
            continue
        seen.add(digest)
        fetched.append((name, data, rows))
        if len(fetched) >= limit:
            break
    say(f"caltrans_cctv: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

STATE_WEB_PACKS = {
    "caltrans_cctv": (build_caltrans_cctv,
                      "Still pictures from California Department of Transportation (Caltrans) highway traffic cameras, "
                      "from Caltrans' own camera data feed; public domain (California public records, County of "
                      "Santa Clara v. Superior Court, 2009; Caltrans Conditions of Use: 'information presented on "
                      "this website, unless otherwise indicated, is considered in the public domain'); answers from "
                      "Caltrans' own camera list. https://cwwp2.dot.ca.gov/documentation/cctv/cctv.htm"),
}

# How many pictures a full build takes (one picture every three seconds or so: about two hours).
STATE_WEB_LIMITS = {
    "caltrans_cctv": 2000,      # about 3,400 cameras in service, 13 pictures each at any moment
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one state-website pack builder.")
    parser.add_argument("key", choices=sorted(STATE_WEB_PACKS))
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--districts", default="", help="only these Caltrans districts, e.g. 4,7 (a quick check)")
    args = parser.parse_args(argv)
    if args.districts:
        global CALTRANS_DISTRICTS
        CALTRANS_DISTRICTS = tuple(int(d) for d in args.districts.split(",") if d.strip())
    entries = STATE_WEB_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures")
    if build_packs.NEEDS:
        say(f"{len(build_packs.NEEDS)} pictures set aside for a description")
    return 0


if __name__ == "__main__":
    sys.exit(main())
