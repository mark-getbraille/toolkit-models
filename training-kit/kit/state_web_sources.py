"""US STATE GOVERNMENT pictures from the agencies' OWN websites and data feeds that cannot be ready-made packs, and the
agency-by-agency record of what was looked at (November 2026). The one open source found, Caltrans' traffic camera
stills, is a pack in packs/state_web_packs.py; the Wikimedia Commons copies of state photo streams are
packs/state_packs.py and kit/state_sources.py.

WHAT WAS LOOKED AT. In California and Florida, whose courts hold that state agencies cannot claim copyright in public
records unless a law allows it (see state_sources.py for the cases and Commons' {{PD-CAGov}} and {{PD-FLGov}}), the
agencies' own photo libraries, galleries and camera feeds; in other states, the open-data portals (Socrata's catalogue
of data.wa.gov, data.ny.gov, data.oregon.gov, data.colorado.gov, data.texas.gov, data.ct.gov, data.mo.gov,
opendata.maryland.gov, data.illinois.gov, data.delaware.gov, data.vermont.gov, data.nj.gov, data.pa.gov and
data.michigan.gov; data.ca.gov's CKAN catalogue; ArcGIS Hub) searched for photo, image, picture and camera datasets, and
the traffic camera systems of California, Oregon, Washington, New York, Minnesota and Arkansas. For each: the terms
page, read in full, and robots.txt, read before anything else was fetched. Several agency sites now carry Cloudflare's
"Content-Signal: search=yes,ai-train=no" line in robots.txt, which their robots.txt calls "a condition of accessing
this website" and "express reservations of rights"; those sites are never used to teach a model, whatever their
licence. The full record is STATE_WEB_RECORD below.

HOW IT IS POLITE. One request at a time, three seconds apart, with the kit's User-Agent (sources.USER_AGENT, the
project's name; no person is named).

The collections (STATE_WEB_SOURCES), each downloaded by the kit on the user's own computer, straight from the agency,
never re-shared by the kit's makers:
  permissive (used in every training; not re-shared, see below)
    tripcheck_cameras        Still pictures from the Oregon Department of Transportation's (ODOT) roadside cameras on
                             TripCheck (about 750 ODOT cameras on state highways; city and county cameras shown on
                             TripCheck are left out). ODOT's TripCheck questions page (https://tripcheck.com/Pages/
                             ATFAQ.asp): "The Oregon Department of Transportation allows businesses, private citizens
                             and organizations to use data and images found on TripCheck" and "ODOT should be credited
                             for use of the camera. Language such as 'Camera courtesy of ODOT' is acceptable." The same
                             page says "ODOT does not save camera images", partly "because of privacy concerns", so the
                             pictures are not gathered into a published pack: each user's kit takes its own few. robots.txt:
                             tripcheck.com serves none (404). Answers: the camera's own title and route from TripCheck's
                             camera list, and "a traffic camera view of a highway".
  noncommercial (personal-use box, Alt+Q; the result is personal use only)
    wa_ecology_shoreline_nc  Oblique aerial photos of Washington's marine shoreline (Puget Sound, the Pacific coast and
                             the lower Columbia River) taken by the Washington State Department of Ecology, the 1990s,
                             2000-2001, 2006-2007 and 2016 surveys (about 93,000 photos; the 1976-1977 survey is left
                             out as older than 1990). Ecology's copyright page (https://ecology.wa.gov/about-us/
                             accountability-transparency/website-information/copyright-information): "Use of images,
                             audio and video from Ecology's websites — for non-commercial purposes only, provided: Users
                             maintain all copyright notices and other notices contained therein; Users credit the
                             Washington State Department of Ecology; and users offer the works freely and openly to
                             others under the terms stated here." The photo list is Ecology's public map service
                             (https://gis.ecology.wa.gov/serverext/rest/services/GIS/CoastalAtlas/MapServer/37); the
                             photos are on fortress.wa.gov. robots.txt: gis.ecology.wa.gov serves none (404),
                             fortress.wa.gov answers nothing, ecology.wa.gov has no Content-Signal line. Answers: the
                             photo's own landmark, county and date from Ecology's list, and "an oblique aerial photo of
                             the Washington State shoreline".

STATE_WEB_PICTURE_MAKING_OK holds wa_ecology_shoreline_nc only: aerial views of coastline taken from an aircraft, where
people are specks. The traffic cameras show people in cars and on foot, so they are never used for picture-making.

    python kit/state_web_sources.py --record            (prints the agency-by-agency record)
    python kit/state_web_sources.py tripcheck_cameras --cap 4      (a quick check; prints a few rows)
"""

import datetime
import json
import os
import random
import re
import time
import urllib.parse

from extra_sources import say
from sources import Source, USER_AGENT, fetch_pictures

PAUSE = 3.0                 # seconds before each request to an agency's server
DESCRIBE_Q = "Describe this picture."
WHO_Q = "Who took this photo?"


def http():
    """A requests session with the kit's User-Agent."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    return s


def placeholder_file(path):
    """True when a downloaded camera picture is a "camera unavailable" card or a blank frame: most of it (above a
    date strip at the bottom) is near white, or the whole picture is one flat shade (as packs/state_web_packs.py
    placeholder)."""
    from PIL import Image, ImageStat
    try:
        img = Image.open(path).convert("L")
    except Exception:  # noqa: BLE001 - not a picture
        return True
    width, height = img.size
    counts = img.crop((0, 0, width, max(1, int(height * 0.85)))).histogram()
    return sum(counts[225:]) / max(1, sum(counts)) > 0.55 or ImageStat.Stat(img).stddev[0] < 6


def fetch_rows(items, folder, check=None):
    """Download each picture once, one at a time and PAUSE seconds apart (items are (file name, address, row); rows
    with the same file name share it); the rows whose picture came and passes check(path) (when given), with
    "picture" set."""
    by_name, order = {}, []
    for name, url, row in items:
        if name not in by_name:
            by_name[name] = (url, [])
            order.append(name)
        by_name[name][1].append(row)
    got = fetch_pictures([(n, by_name[n][0], {"name": n}) for n in order], folder, workers=1, pause=PAUSE)
    rows = []
    for result in got:
        if check and not check(result["picture"]):
            continue
        rows += [dict(row, picture=result["picture"]) for row in by_name[result["name"]][1]]
    return rows


# ----------------------------------------------------------------- ODOT TripCheck cameras

TRIPCHECK_LIST = "https://tripcheck.com/Scripts/map/data/cctvinventory.js"
TRIPCHECK_PICTURE = "https://tripcheck.com/RoadCams/cams/"
TRIPCHECK_TERMS = "https://tripcheck.com/Pages/ATFAQ.asp"
TRIPCHECK_WHO = "It is a still picture from an Oregon Department of Transportation (ODOT) roadside camera on TripCheck."
# Cameras of cities and counties that TripCheck also shows (their owners' terms were not read): left out.
NOT_ODOT = re.compile(r"^\s*(city|cnty|county)\s*$", re.I)
NOT_ODOT_TITLE = re.compile(r"^\s*(Portland|Salem|Eugene|Bend|Medford|Gresham|Beaverton|Hillsboro|Springfield|Corvallis|"
                            r"Albany|Tigard|Lake Oswego|Keizer|Wilsonville|Tualatin|[A-Z][\w.]*( [A-Z][\w.]*)? "
                            r"Co(unty)?\.?) - ", re.I)


def tripcheck_cameras(data):
    """The ODOT cameras of TripCheck's camera list (its JSON, as read): [{"id", "title", "route", "file"}], without the
    city and county cameras."""
    cameras = []
    for feature in (data or {}).get("features", []):
        a = feature.get("attributes") or {}
        title, route, file = (a.get("title") or "").strip(), (a.get("route") or "").strip(), a.get("filename") or ""
        if not file or not title or NOT_ODOT.match(route) or NOT_ODOT_TITLE.match(title):
            continue
        cameras.append({"id": str(a.get("cameraId") or a.get("publishedImageId")), "title": re.sub(r"\s+", " ", title),
                        "route": route, "file": file})
    return cameras


def tripcheck_rows(cam):
    """The rows of one ODOT camera picture, from TripCheck's own camera list only."""
    route = f", on {cam['route']}" if cam["route"] and cam["route"].lower() not in cam["title"].lower() else ""
    credit = f"Camera courtesy of ODOT (TripCheck camera '{cam['title']}'), {TRIPCHECK_TERMS}"
    return [{"question": DESCRIBE_Q, "answer": f"A traffic camera view of a highway: {cam['title']}{route}, Oregon.",
             "split": "", "credit": credit},
            {"question": "Where is this traffic camera?", "answer": f"{cam['title']}{route}, Oregon.", "split": "",
             "credit": credit},
            {"question": WHO_Q, "answer": TRIPCHECK_WHO, "split": "", "credit": credit}]


def prepare_tripcheck_cameras(source, data_dir, work, cap):
    """ODOT TripCheck camera stills: one current picture from each of cap + test cameras chosen at random (a later
    run takes other cameras, hours and weather); "camera unavailable" cards are left out."""
    s = http()
    time.sleep(PAUSE)
    r = s.get(TRIPCHECK_LIST, timeout=120)
    r.raise_for_status()
    cameras = tripcheck_cameras(r.json())
    say(f"  TripCheck: {len(cameras)} ODOT cameras listed")
    rng = random.Random(f"tripcheck/{datetime.date.today()}")
    rng.shuffle(cameras)
    stamp = time.strftime("%Y%m%d%H")
    items = []
    for cam in cameras[:int((cap + source.test) * 1.2) + 2]:
        name = f"tripcheck-{cam['id']}-{stamp}.jpg"
        url = TRIPCHECK_PICTURE + urllib.parse.quote(cam["file"])
        items += [(name, url, row) for row in tripcheck_rows(cam)]
    return fetch_rows(items, os.path.join(data_dir, source.key), check=lambda p: not placeholder_file(p))


# ----------------------------------------------------------------- Washington Ecology shoreline photos

ECOLOGY_LIST = "https://gis.ecology.wa.gov/serverext/rest/services/GIS/CoastalAtlas/MapServer/37/query"
ECOLOGY_TERMS = ("https://ecology.wa.gov/about-us/accountability-transparency/website-information/"
                 "copyright-information")
ECOLOGY_WHERE = "Vintage >= 1990"
ECOLOGY_WHO = ("It is an oblique aerial photo from the Washington State Department of Ecology's survey of the state's "
               "marine shoreline.")
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")


def ecology_date(text):
    """Ecology's photo date ("5/13/1997") in words ("13 May 1997"), and its year; ("", 0) when it cannot be read."""
    m = re.match(r"^\s*(\d{1,2})/(\d{1,2})/(\d{4})", text or "")
    if not m or not 1 <= int(m.group(1)) <= 12:
        return "", 0
    return f"{int(m.group(2))} {MONTHS[int(m.group(1)) - 1]} {m.group(3)}", int(m.group(3))


def ecology_rows(record):
    """The rows of one shoreline photo from Ecology's own list (its landmark, county and date); [] when it has no
    picture address, no county, or is dated before 1990."""
    url = (record.get("FULLSIZE_URL") or "").strip()
    county = (record.get("COUNTY_NM") or "").strip()
    landmark = re.sub(r"\s+", " ", (record.get("LANDMARK_DS") or "").strip())
    when, year = ecology_date(record.get("PHOTO_DATE") or record.get("PHOTO_DT") or "")
    if not url.startswith("https://") or not county or (year and year < 1990) or (record.get("Vintage") or 0) < 1990:
        return []
    place = f"{landmark}, in {county} County, Washington" if landmark else f"{county} County, Washington"
    taken = f", taken on {when}" if when else ""
    credit = (f"Washington State Department of Ecology, shoreline photo {record.get('PHOTO_NR', '')}, non-commercial "
              f"use with credit, {ECOLOGY_TERMS}")
    return [{"question": DESCRIBE_Q, "answer": f"An oblique aerial photo of the Washington State shoreline: {place}"
                                               f"{taken}.", "split": "", "credit": credit},
            {"question": "Where is this?", "answer": f"On the marine shoreline of Washington State: {place}.",
             "split": "", "credit": credit},
            {"question": WHO_Q, "answer": ECOLOGY_WHO, "split": "", "credit": credit}]


def prepare_wa_ecology_shoreline_nc(source, data_dir, work, cap):
    """Washington Ecology's shoreline photos of 1990 onwards: pages of 200 records at random places in Ecology's list,
    until there are enough photos for cap + test."""
    s = http()
    want = int((cap + source.test) * 1.1) + 2
    time.sleep(PAUSE)
    count = s.get(ECOLOGY_LIST, params={"where": ECOLOGY_WHERE, "returnCountOnly": "true", "f": "json"},
                  timeout=120).json().get("count", 0)
    say(f"  Washington Ecology: {count} shoreline photos of 1990 onwards listed")
    rng = random.Random("wa_ecology_shoreline")
    offsets = list(range(0, count, 200))
    rng.shuffle(offsets)
    items, seen = [], set()
    for offset in offsets:
        if len(seen) >= want:
            break
        time.sleep(PAUSE)
        r = s.get(ECOLOGY_LIST, params={"where": ECOLOGY_WHERE, "outFields": "*", "orderByFields": "OBJECTID",
                                        "resultOffset": offset, "resultRecordCount": 200, "returnGeometry": "false",
                                        "f": "json"}, timeout=120)
        records = [f.get("attributes") or {} for f in r.json().get("features", [])]
        rng.shuffle(records)
        for record in records[:25]:               # a few from each page: spread along the whole shoreline
            if len(seen) >= want:
                break
            rows = ecology_rows(record)
            name = f"ecology-{re.sub(r'[^A-Za-z0-9_-]', '', str(record.get('PHOTO_NR', '')))}.jpg"
            if not rows or name in seen:
                continue
            seen.add(name)
            items += [(name, record["FULLSIZE_URL"], row) for row in rows]
    return fetch_rows(items, os.path.join(data_dir, source.key))


# ----------------------------------------------------------------- the collections

STATE_WEB_SOURCES = [
    Source("tripcheck_cameras", "Oregon highway traffic camera pictures (ODOT TripCheck; downloaded by the kit)",
           "ODOT allows businesses, private citizens and organizations to use data and images found on TripCheck, "
           "with ODOT credited (TripCheck questions page); not re-shared: ODOT does not keep its camera pictures, "
           "partly for privacy",
           "Camera courtesy of ODOT (Oregon Department of Transportation, TripCheck), https://tripcheck.com",
           "permissive", 300, 10, prepare_tripcheck_cameras, "about 10 MB of pictures", terms=TRIPCHECK_TERMS,
           terms_summary="ODOT allows anyone to use TripCheck data and camera pictures, crediting ODOT."),
    Source("wa_ecology_shoreline_nc", "Washington shoreline aerial photos, 1990s to 2016 (Washington State Department "
                                      "of Ecology; non-commercial)",
           "Ecology's images: non-commercial use only, crediting Ecology, keeping its notices, and offering any copies "
           "under the same terms (Ecology's copyright page)",
           "Washington State Department of Ecology, shoreline photos, " + ECOLOGY_TERMS,
           "noncommercial", 600, 20, prepare_wa_ecology_shoreline_nc, "about 1.6 GB of photos", terms=ECOLOGY_TERMS,
           terms_summary="Non-commercial use only, with credit to the Washington State Department of Ecology; "
                         "copies must be offered on the same terms."),
]

# The collections a picture-making model may learn from: the shoreline aerial photos only (no people to be seen).
STATE_WEB_PICTURE_MAKING_OK = {"wa_ecology_shoreline_nc"}


# ----------------------------------------------------------------- the agency-by-agency record

BUILT = "built: packs/state_web_packs.py"
KIT = "kit entry (downloaded on the user's own computer)"
NOT_IN = "not included"
AI_TRAIN_NO = ("robots.txt: 'Content-Signal: search=yes,ai-train=no,use=reference' under 'User-agent: *', which it "
               "calls 'a condition of accessing this website' and an express reservation of rights; it also disallows "
               "AI crawlers (GPTBot, ClaudeBot, CCBot, Google-Extended and others)")


def entry(state, agency, site, offers, terms, terms_url, robots, result):
    """One line of the record: the state, the agency, its site, what it offers, its terms line and where it is
    written, what its robots.txt says, and what was done (built, kit entry, sign-up, permission or not included,
    with the reason)."""
    return {"state": state, "agency": agency, "site": site, "offers": offers, "terms": terms, "terms_url": terms_url,
            "robots": robots, "result": result}


STATE_WEB_RECORD = [
    entry("California", "Department of Transportation (Caltrans)", "https://cwwp2.dot.ca.gov (camera data feed; also "
          "behind QuickMap)", "about 3,400 highway traffic cameras, each with its current still and 12 earlier ones; "
          "camera list with route, place, county and direction",
          "'In general, information presented on this website, unless otherwise indicated, is considered in the public "
          "domain. It may be distributed or copied as permitted by law.' Feed page: 'available for integration into "
          "your application ... There is no charge for the use of this data.' Public record under County of Santa "
          "Clara v. Superior Court (2009); Caltrans is not among {{PD-CAGov}}'s agencies allowed copyright",
          "https://dot.ca.gov/conditions-of-use", "cwwp2.dot.ca.gov: none (the address answers 500); dot.ca.gov: "
          "none (404)", BUILT + " caltrans_cctv (open, public domain)"),
    entry("California", "Department of Transportation (Caltrans)", "https://dot.ca.gov", "photos on project and "
          "news pages; no photo library with captions on its own site (its photo stream is on Flickr)",
          "the same Conditions of Use, which add: 'the California Department of Transportation does make use of "
          "copyrighted data (e.g., photographs) which may require additional permissions prior to your use'",
          "https://dot.ca.gov/conditions-of-use", "none (404)",
          NOT_IN + ": no gallery with captions; page photos may be contractors' or others' (the terms' own caveat)"),
    entry("California", "Department of Forestry and Fire Protection (CAL FIRE)", "https://www.fire.ca.gov",
          "incident pages with photos", "not read: the site answers 'Access Denied' to the kit's client",
          "https://www.fire.ca.gov", "refused (403 Access Denied, even for robots.txt)",
          NOT_IN + ": the site refuses automated clients; CAL FIRE's own photos already on Commons are in "
                   "commons_state_response"),
    entry("California", "Department of Parks and Recreation (State Parks)", "https://www.parks.ca.gov",
          "park pages with photos; no photo library with captions", "the State's Conditions of Use: public domain "
          "'unless otherwise indicated' but 'the State does make use of copyrighted data (e.g., photographs) which may "
          "require additional permissions'", "https://www.ca.gov/legal/conditions-of-use/", "none (404)",
          NOT_IN + ": no gallery with captions to read; which photos are staff photos is not said"),
    entry("California", "Department of Fish and Wildlife (CDFW)", "https://wildlife.ca.gov and its open-data site "
          "(data-cdfw.opendata.arcgis.com)", "website photos; open-data layers 'Resource Assessment Program Photos "
          "[ds205]' (3,322 field photos, 2002-2007, CC BY) and camera-trap detection tables",
          "website: the State's Conditions of Use (as State Parks); open data: Creative Commons Attribution "
          "(data.ca.gov licence field)", "https://wildlife.ca.gov/Conditions-of-Use", "none (404)",
          NOT_IN + ": ds205's photo links ('/photoviewer/photos/viewer.asp?ID=...') lead nowhere (404 on "
                   "wildlife.ca.gov, apps.wildlife.ca.gov and nrm.dfg.ca.gov) and its description fields are empty; "
                   "camera-trap layers hold detections, not pictures; CDFW's Flickr photos are already in "
                   "commons_state_outdoors"),
    entry("California", "Department of Water Resources (DWR)", "https://pixel-ca-dwr.photoshelter.com (Pixel photo "
          "library) and https://water.ca.gov", "a large photo library of water projects, dams, rivers and the "
          "Delta, 'available for free download' (DWR's Library page)", "no licence statement found on Pixel "
          "(its pages need JavaScript); water.ca.gov's robots.txt reserves AI training", "https://water.ca.gov/Library",
          "water.ca.gov: " + AI_TRAIN_NO + "; Pixel (PhotoShelter): ordinary robots.txt",
          NOT_IN + ": the agency has said no to AI training on its site; ask DWR (see STATE_WEB_PERMISSION)"),
    entry("California", "Natural Resources Agency", "https://resources.ca.gov", "news photos", "-",
          "https://resources.ca.gov", AI_TRAIN_NO, NOT_IN + ": AI training reserved in robots.txt"),
    entry("California", "data.ca.gov (state CKAN portal)", "https://data.ca.gov", "searched for photo, photographs, "
          "images, camera: aerial photo indexes (DWR), CDFW photo layers (above), the State Controller's page "
          "banner images", "dataset licences mostly Creative Commons Attribution", "https://data.ca.gov",
          "not needed (catalogue API)", NOT_IN + ": no dataset of described photos (aerial indexes and page banners)"),
    entry("Florida", "Fish and Wildlife Conservation Commission (FWC)", "https://myfwc.com", "species and "
          "habitat photos on its pages; boat ramp and research pages", "public records under Florida law "
          "({{PD-FLGov}}; FWC is not among the agencies allowed copyright)", "https://myfwc.com/robots.txt",
          AI_TRAIN_NO, NOT_IN + ": AI training reserved in robots.txt; FWC research photos already on Commons are in "
                                "commons_state_outdoors"),
    entry("Florida", "Florida State Parks (Department of Environmental Protection)",
          "https://www.floridastateparks.org", "park photos; yearly photo contests", "public records under "
          "{{PD-FLGov}}, but contest photos stay their photographers' ('non-exclusive rights to use and publish')",
          "https://www.floridastateparks.org/robots.txt", AI_TRAIN_NO, NOT_IN + ": AI training reserved in robots.txt; "
                                                                               "contest photos are not the state's"),
    entry("Florida", "Department of Environmental Protection (DEP)", "https://floridadep.gov", "no photo gallery "
          "with captions found; photo-contest winners and a historic staff photo collection", "no general licence "
          "statement found; public records under {{PD-FLGov}}", "https://floridadep.gov",
          "ordinary robots.txt (no AI line)", NOT_IN + ": no gallery of the department's own captioned photos found "
                                                        "(contest photos belong to their photographers)"),
    entry("Florida", "Division of Emergency Management (FDEM)", "https://www.floridadisaster.org", "news pages; its "
          "photos are posted on social media and Flickr", "public records under {{PD-FLGov}}",
          "https://www.floridadisaster.org", "ordinary robots.txt (no AI line)",
          NOT_IN + ": no photo gallery on its own site found (unverified page by page); Flickr is not used"),
    entry("Florida", "State Library and Archives (Florida Memory, Department of State)",
          "https://www.floridamemory.com", "the Florida Photographic Collection, some modern photos",
          "{{PD-FLGov}} lists the Department of State among the agencies Florida law allows to claim copyright "
          "(§286.031): 'any works of these agencies should be assumed to be copyrighted'",
          "https://commons.wikimedia.org/wiki/Template:PD-FLGov", "refused (403, even for robots.txt)",
          NOT_IN + ": copyright may be claimed, and the site refuses automated clients"),
    entry("Florida", "Department of Transportation (FDOT) and FL511 cameras", "https://fl511.com",
          "traffic cameras", "{{PD-FLGov}}: FDOT may claim copyright (§334.049): 'should be assumed to be copyrighted'",
          "https://commons.wikimedia.org/wiki/Template:PD-FLGov", "fl511.com: ordinary robots.txt",
          NOT_IN + ": FDOT works are assumed copyrighted and no licence for its camera pictures was found"),
    entry("Oregon", "Department of Transportation (ODOT), TripCheck cameras", "https://tripcheck.com",
          "about 1,180 cameras listed (about 750 ODOT ones on state highways); a camera list in JSON",
          "'The Oregon Department of Transportation allows businesses, private citizens and organizations to use data "
          "and images found on TripCheck.' 'ODOT should be credited for use of the camera.' 'ODOT does not save camera "
          "images' (in part 'because of privacy concerns')", TRIPCHECK_TERMS, "none (404)",
          KIT + " tripcheck_cameras (permissive; not re-shared, out of respect for ODOT's privacy reason)"),
    entry("Oregon", "data.oregon.gov (Socrata)", "https://data.oregon.gov", "'AlertWest Oregon Cameras' (wildfire "
          "cameras run by a private network), aerial imagery", "no licence given in the catalogue",
          "https://data.oregon.gov", "not needed (catalogue API)",
          NOT_IN + ": the cameras are not the state's and no licence is given"),
    entry("Washington", "Department of Ecology, shoreline photos", "https://gis.ecology.wa.gov (Coastal Atlas map "
          "service) and fortress.wa.gov (the photos)", "about 97,500 oblique aerial shoreline photos (1976-77, "
          "1990s, 2000-01, 2006-07, 2016) with landmark, county and date",
          "'Use of images, audio and video from Ecology's websites — for non-commercial purposes only, provided: Users "
          "maintain all copyright notices ...; Users credit the Washington State Department of Ecology; and users "
          "offer the works freely and openly to others under the terms stated here.'", ECOLOGY_TERMS,
          "gis.ecology.wa.gov: none (404); fortress.wa.gov: no answer; ecology.wa.gov: ordinary (no AI line)",
          KIT + " wa_ecology_shoreline_nc (non-commercial; 1990 onwards only)"),
    entry("Washington", "Department of Transportation (WSDOT)", "https://wsdot.wa.gov and its traffic cameras",
          "camera stills, project photos; its Flickr stream (Creative Commons, per WSDOT's photo standards page)",
          "'This site contains text, artwork, photos or other content that is copyrighted by others ... Therefore, we "
          "recommend that you contact us for permission to use any content contained on this site.' Its traveller "
          "data API needs an access code", "https://wsdot.wa.gov/about/web-privacy-notice",
          "ordinary robots.txt (no AI line)", "permission (see STATE_WEB_PERMISSION); Flickr is not used"),
    entry("Washington", "data.wa.gov (Socrata)", "https://data.wa.gov", "'Washington's State Art Collection' (licence "
          "field: Public Domain), 'Imaged Documents and Reports'", "the licence field covers the catalogue data; "
          "the artworks are the artists' own", "https://data.wa.gov", "not needed (catalogue API)",
          NOT_IN + ": the public-domain mark is for the list, not the artworks' pictures; no photo datasets"),
    entry("New York", "Department of Transportation, 511NY cameras", "https://511ny.org", "statewide camera stills "
          "through a developer API", "the 511NY Developer's Access Agreement; a key is e-mailed 'once approved'",
          "https://511ny.org/developers/daa", "ordinary robots.txt", "sign-up (see STATE_WEB_SIGN_UP)"),
    entry("New York", "Department of Environmental Conservation (DEC)", "https://dec.ny.gov", "its photo terms "
          "cover photos the public SENDS to DEC ('Photos, videos, and audio files remain your property'); its own "
          "photos are on Flickr", "https://dec.ny.gov/about/website-usage-and-policies/photography-and-videography-"
          "terms-of-use", "https://dec.ny.gov", "not read", NOT_IN + ": no licence for DEC's own photos; Flickr is not "
                                                                     "used"),
    entry("New York", "data.ny.gov (Socrata)", "https://data.ny.gov", "statewide orthoimagery (aerial), no photo "
          "datasets", "-", "https://data.ny.gov", "not needed (catalogue API)", NOT_IN + ": no photo datasets"),
    entry("Minnesota", "Department of Transportation, 511mn cameras and plow cameras", "https://511mn.org",
          "camera and snowplow-camera stills", "no terms of use for the camera pictures were found (unverified)",
          "https://511mn.org", "ordinary robots.txt", NOT_IN + ": licence unknown; ask MnDOT (already in "
                                                                "state_sources.STATE_PERMISSION_CANDIDATES)"),
    entry("Arkansas", "IDrive Arkansas (ARDOT) cameras", "https://www.idrivearkansas.com", "traffic camera stills",
          "'are the property of and copyrighted by each camera owner. All rights are reserved.' 'Embedding live camera "
          "images ... in another web site or application (app) is prohibited.'",
          "https://site.idrivearkansas.com/index.php/policies/camera-terms-of-use/", "not read",
          NOT_IN + ": all rights reserved"),
    entry("Colorado, Connecticut, Maryland, Pennsylvania, Delaware, Michigan, New Jersey, Texas, Illinois, Missouri, "
          "Vermont", "state Socrata open-data portals", "data.colorado.gov, data.ct.gov, opendata.maryland.gov, "
          "data.pa.gov, data.delaware.gov, data.michigan.gov, data.nj.gov, data.texas.gov, data.illinois.gov, "
          "data.mo.gov, data.vermont.gov", "aerial and orthoimagery services (NAIP, county flights), sign-panel and "
          "road tables, page banner images; no datasets of ground photos", "licence fields mostly Public Domain or "
          "none", "https://api.us.socrata.com/api/catalog/v1", "not needed (catalogue API)",
          NOT_IN + ": aerial map tiles are not pictures to describe, and NAIP is a federal (USDA) programme"),
    entry("several states", "ArcGIS Hub survey layers (culverts, bridges, boat ramps, trails, parks)",
          "https://hub.arcgis.com", "field-survey layers with photo attachments (Texas DOT 'Culvert_Photos_JB', "
          "Alaska DOT&PF retaining walls, county and contractor inspection layers)", "licence 'none' on nearly every "
          "layer; many are by contractors or volunteers", "https://hub.arcgis.com/api/search/v1",
          "not needed (search API)", NOT_IN + ": no licence stated (would be research only) and no captions beyond "
                                              "inspection codes"),
]

STATE_WEB_SIGN_UP = {
    "511NY (New York State DOT) camera pictures": "https://511ny.org/developers/daa : the Developer's Access Agreement "
    "must be accepted and a key is sent 'once approved'. The owner can apply; a kit entry would read the key from an "
    "environment variable such as NY511_API_KEY. Its terms on keeping or re-sharing pictures were not read.",
    "WSDOT traveller information API (cameras)": "https://wsdot.wa.gov/traffic/api/ : needs an access code (free, by "
    "e-mail); the camera pictures themselves are under WSDOT's 'contact us for permission' notice (see "
    "STATE_WEB_PERMISSION).",
}

STATE_WEB_PERMISSION = {
    "California Department of Water Resources (Pixel photo library)": "Has: a large library of photos of dams, "
    "aqueducts, rivers, floods and the Delta, free to download. Public records under California law, but water.ca.gov's "
    "robots.txt says 'ai-train=no'. Ask (whether its photos may be used to teach a describer for blind people): "
    "https://water.ca.gov/Contact.",
    "Washington State Department of Transportation": "Its website says 'we recommend that you contact us for "
    "permission to use any content contained on this site' (https://wsdot.wa.gov/about/web-privacy-notice). Ask "
    "(already listed in state_sources.STATE_PERMISSION_CANDIDATES): https://wsdot.wa.gov/about/contacts.",
    "Florida Fish and Wildlife Conservation Commission and Florida State Parks": "Public records under Florida law, "
    "but their robots.txt says 'ai-train=no'. Ask their public information offices whether their photos may be used "
    "to teach a describer for blind people: https://myfwc.com/contact/ and https://www.floridastateparks.org/contact.",
}


def record_table():
    """The agency-by-agency record as Markdown: state, agency, what it offers, its terms line, robots.txt, result."""
    lines = ["| State | Agency and site | Offers | Terms line (URL) | robots.txt | Result |", "|---|---|---|---|---|---|"]
    for e in STATE_WEB_RECORD:
        cells = [e["state"], f"{e['agency']}: {e['site']}", e["offers"], f"{e['terms']} ({e['terms_url']})",
                 e["robots"], e["result"]]
        lines.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
    return "\n".join(lines)


def main(argv=None):
    """Print the record, or prepare one collection into an empty folder with a small cap and print a few rows (a quick
    check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try the state website collections.")
    parser.add_argument("key", nargs="?", choices=[s.key for s in STATE_WEB_SOURCES])
    parser.add_argument("--record", action="store_true", help="print the agency-by-agency record")
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=4)
    args = parser.parse_args(argv)
    if args.record or not args.key:
        print(record_table())
        return 0
    source = next(s for s in STATE_WEB_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="state-web-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:9]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
