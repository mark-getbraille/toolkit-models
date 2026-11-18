"""US STATE, COUNTY and CITY GOVERNMENT photo collections for the Picture Model Training Kit that cannot be
ready-made packs because of their licence, and the state-by-state record of what was searched, found and left out.
The open ones (state transportation, parks and wildlife, National Guard and fire-agency emergencies, and city,
county, state-archive and state-university streams, all Wikimedia Commons copies with each file's own licence
checked) are packs in packs/state_packs.py.

WHY STATE PHOTOS NEED CARE. Federal works are public domain (17 U.S.C. 105), but that law does not cover states: most
state and local governments may hold copyright in their photos. Two states are different, by their own courts:
  Florida     Microdecisions, Inc. v. Skinner, 889 So. 2d 871 (Fla. 2d DCA 2004): a county officer had no authority
              to claim copyright in public records, because the legislature never allowed it. Wikimedia Commons'
              tag {{PD-FLGov}} (https://commons.wikimedia.org/wiki/Template:PD-FLGov) says a work of a Florida
              government unit "is a public record that was not created by an agency which state law has allowed to
              claim copyright", but lists the agencies that may claim it (among them the Florida Department of
              Transportation, the lottery, water management districts and the state universities and colleges): "any
              works of these agencies should be assumed to be copyrighted". A photo a private person made and gave
              to an agency stays theirs.
  California  County of Santa Clara v. Superior Court, 170 Cal. App. 4th 1301 (2009): without an express law allowing
              it, an agency cannot claim copyright in a public record. Commons' tag {{PD-CAGov}}
              (https://commons.wikimedia.org/wiki/Template:PD-CAGov) covers works "created by a government unit
              (including state, county, city, and municipal government agencies)" subject to the Public Records Act,
              except agencies a law allows to claim copyright (school and community-college districts, county boards
              of education, the Department of Toxic Substances Control ...), software, and works by non-government
              authors.
Elsewhere a state photo is used only when the agency itself licensed it openly; in practice that is the licence an
agency chose on its Flickr stream, copied with that licence to Wikimedia Commons (Commons' FlickreviewR bot confirms
it, e.g. "reviewed on 18 August 2021 by FlickreviewR 2 and was confirmed to be licensed under the terms of the
cc-by-2.0", https://commons.wikimedia.org/wiki/File:2020_Oregon_Wildfires_(50768771473).jpg). Flickr itself is never
used: its API terms (https://www.flickr.com/services/api/tos/) say you shall not "Cache or store any Flickr user
photos other than for reasonable periods in order to provide the service you are providing to Flickr users". Commons
does not keep non-commercial (CC BY-NC) files, so a state stream under a non-commercial licence has no copy that may
be downloaded here; none was found elsewhere either (see STATE_NOT_INCLUDED).

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from Wikimedia Commons, only when the user ticks the matching choice. Every licence was
checked at its source in November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"  CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia).

The collections (STATE_SOURCES):
  share-alike
    commons_state_sa   Wikimedia Commons files under CC BY-SA or GFDL from state and city government streams: Knoxville
                       Area Transit (Tennessee; 166 files, its Flickr stream is CC BY-SA 2.0: "This file is licensed
                       under the Creative Commons Attribution-Share Alike 2.0 Generic license", e.g.
                       https://commons.wikimedia.org/wiki/File:Hybrid_buses_(24834828658).jpg), the Montgomery
                       County Planning Commission (Pennsylvania; 159 files of stations, bridges, parks, farms and
                       fairs, CC BY-SA 2.0, e.g. https://commons.wikimedia.org/wiki/File:Ambler_station_at_night,
                       _January_2017.jpg) and the share-alike files of the City of Boston Archives (its Flickr stream
                       mixes CC BY 2.0 and CC BY-SA 2.0).
                       "Who took this photo?" with the agency, and "Describe this picture." with the file's own
                       caption. Files whose words say they are older than 1990, an official event, crime or a victim,
                       nudity or swimwear are left out; rows naming a child are marked "child".

STATE_SUMMARY is the state-by-state table (50 states, DC and Puerto Rico; one column per kind of agency that mirrors a
federal agency the kit already uses); STATE_SIGN_UP, STATE_NOT_INCLUDED and STATE_PERMISSION_CANDIDATES give the
links, reasons and terms lines. STATE_PICTURE_MAKING_OK is empty: these photos show people.

    python kit/state_sources.py --table          (prints the state-by-state table)
    python kit/state_sources.py commons_state_sa --cap 8      (a quick check; prints a few rows)
"""

import json
import os
import re

from extra_sources import say
from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source

WHO_Q = "Who took this photo?"
# As in packs/state_packs.py: files left out by their words.
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|nude|naked|topless|sexy|sexual\w*|"
                       r"erotic\w*|mug ?shots?|evidence)\b", re.I)
CRIME = re.compile(r"\b(arrest\w*|suspects?|inmates?|prisons?|prisoners?|jail\w*|correctional|crimes?|criminal|"
                   r"homicides?|murder\w*|shootings?|victims?|autops\w*)\b", re.I)
NOT_MODERN = re.compile(r"\b(18\d\d|19[0-8]\d)s?\b|\b(19)?[2-8]0s\b|\b(museum|antique|vintage|historic(al)?|"
                        r"restored|replica|circa|c\. ?19)\b", re.I)
OFFICIAL = re.compile(r"\b(governor|lieutenant governor|mayor|senator|congress\w*|legislat\w*|council ?(member|man|"
                      r"woman)|commissioner|secretary|ribbon[- ]cutting|groundbreaking|press (conference|event)|"
                      r"remarks|ceremony|swearing|sworn|signing|award\w*|campaign|candidates?|inaugurat\w*)\b|"
                      r"\b(Gov|Rep|Sen|Lt)\.\s+[A-Z]", re.I)

# (category, question, answer, also its subcategories): the state and city streams with share-alike files.
STATE_SA = [
    ("Files from Knoxville Area Transit Flickr stream", WHO_Q,
     "It is a photo by Knoxville Area Transit, the city of Knoxville's public transit agency in Tennessee.", False),
    ("Files from the Montgomery County Planning Commission (Pennsylvania) Flickr stream", WHO_Q,
     "It is a photo by the Montgomery County Planning Commission, part of the county government of Montgomery County, "
     "Pennsylvania.", False),
    ("Files from City of Boston Archives Flickr stream", WHO_Q,
     "It is a photo from the City of Boston Archives, a city archive in Massachusetts.", False),
]


def left_out(words):
    """True when a share-alike file's words say it is older than 1990, an official event, crime or a victim, or
    nudity or swimwear (every row of that file goes)."""
    return bool(NOT_SHOWN.search(words) or CRIME.search(words) or NOT_MODERN.search(words)
                or OFFICIAL.search(words))


def prepare_commons_state_sa(source, data_dir, work, cap):
    """Commons state and city government streams, files under CC BY-SA or GFDL (home_sources.commons_sa_items: the
    categories share the cap; rows whose words name a child are marked "child"), without the files left_out."""
    items = commons_sa_items(STATE_SA, cap, source.test, "state-sa")
    bad = {name for name, _, row in items if left_out(f"{name} {row['answer']}")}
    if bad:
        say(f"  {len(bad)} files left out by their words (older than 1990, official events, crime, nudity)")
    items = [i for i in items if i[0] not in bad]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


SA_TERMS = "https://creativecommons.org/licenses/by-sa/2.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
STATE_SOURCES = [
    Source("commons_state_sa", "US city and county government photos: Knoxville Area Transit buses, Montgomery "
                               "County (Pennsylvania) planning photos and the City of Boston Archives, files under "
                               "CC BY-SA (Wikimedia Commons, share-alike)",
           "Each file CC BY-SA 2.0 (or GFDL), as its agency licensed it on Flickr and Commons' review confirmed; "
           "captions by the agencies",
           "Knoxville Area Transit, the Montgomery County Planning Commission and the City of Boston Archives via "
           "Wikimedia Commons, CC BY-SA, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 300, 10, prepare_commons_state_sa, "about 80 MB of pictures", terms=SA_TERMS,
           terms_summary=SA_SUMMARY),
]

# The collections a picture-making model may learn from: none (these photos show people at work and at events).
STATE_PICTURE_MAKING_OK = set()


# ----------------------------------------------------------------- the state-by-state record

# The kinds of state agency searched, each the state counterpart of a federal agency the kit already uses or checked.
AGENCY_KINDS = {
    "archives": "state archives and state libraries (Library of Congress, NARA)",
    "parks": "state parks (National Park Service)",
    "geology": "state geological surveys (USGS)",
    "farm": "state agriculture and forestry departments, conservation districts, extension services (USDA ARS, NRCS, "
            "Forest Service)",
    "emergency": "state emergency management and fire agencies (FEMA)",
    "housing": "state housing finance agencies (HUD)",
    "health": "state health departments (NIH, CDC)",
    "environment": "state environment departments (EPA)",
    "wildlife": "state fish and wildlife and natural resources departments (NOAA, USFWS)",
    "transport": "state transportation departments and transit authorities (DOT, FHWA)",
    "consumer": "state consumer protection (CPSC)",
    "museums": "state museums and historical societies (Smithsonian)",
    "guard": "state National Guards (the military services)",
    "universities": "state universities' image collections (NASA- and ESO-style science)",
    "local": "large cities and counties",
}
HOW_SEARCHED = (
    "Searched in November 2026 on Wikimedia Commons (the only place state photos can be copied from here, see the "
    "module notes), by category titles: 'Flickr stream' with Department, DOT, Authority, Commission, Agency, State, "
    "Parks, Wildlife, Natural Resources, Conservation, Emergency, Fire, Health, Agriculture, Extension, Forest, "
    "Environment, Fair, Highway, Port, City, County, Metro, Transit, Guard, University, Archives and Governor, and "
    "with "
    "each state's name; 'Photographs by the' with Department, State, County, City, Authority, Guard and Parks; 'Files "
    "from' and 'Images from' with Emergency Management, Geological Survey, Extension, Housing Finance, Department of "
    "Health, Department of Agriculture, Department of Environmental, Historical Society, State Museum and State Fair; "
    "the agency abbreviations GovPics, PennDOT, TxDOT, Caltrans, MnDOT, UDOT, CDOT, VDOT, WSDOT and IDOT; the Commons "
    "category 'State departments of transportation of the United States' (all 52 subcategories); and the "
    "public-domain categories 'PD Florida' and 'PD California'. A blank cell means no Commons copy of that kind of "
    "agency's photos was found for the state: its photos, if any, are only on the agency's own site (whose terms "
    "would have to be read one by one, and most reserve copyright) or on Flickr (not used). Each found stream's "
    "licence was read from its files' own Commons pages.")
BUILT = "built: packs/state_packs.py"
SA_ENTRY = "share-alike kit entry commons_state_sa"
NOT_IN = "not included"

# {state: {agency kind: what was found, where, its licence, and whether it is used}}; states not listed: none found.
STATE_SUMMARY = {
    "Alabama": {}, "Arizona": {}, "Connecticut": {}, "Delaware": {}, "Georgia": {}, "Hawaii": {}, "Idaho": {},
    "Illinois": {}, "Iowa": {}, "Kentucky": {}, "Louisiana": {}, "Maine": {}, "Mississippi": {}, "Montana": {},
    "Nebraska": {}, "Nevada": {}, "New Hampshire": {}, "New Mexico": {}, "North Dakota": {}, "Oklahoma": {},
    "Rhode Island": {}, "South Dakota": {}, "Vermont": {}, "Wisconsin": {}, "Wyoming": {},
    "District of Columbia": {}, "Puerto Rico": {},
    "Alaska": {"transport": "Alaska DOT&PF, Commons 'Alaska Department of Transportation & Public Facilities' (1,769 "
                            f"files), CC BY 2.0; {BUILT} commons_state_roads"},
    "Arkansas": {"guard": "Arkansas National Guard, Commons 'Photographs from the Arkansas National Guard Flickr "
                          f"stream' (1,970), public domain; {BUILT} commons_state_response (emergencies only)"},
    "California": {
        "wildlife": "Department of Fish and Wildlife, Commons 'Files from the California Department of Fish and "
                    f"Wildlife Flickr stream' (1,528), CC BY 2.0; {BUILT} commons_state_outdoors",
        "emergency": "CAL FIRE, Commons 'Photographs by the California Department of Forestry and Fire Protection' "
                     f"(187), public domain ({{{{PD-CAGov}}}}); {BUILT} commons_state_response (most are from 1988: "
                     "only 1990 onwards is kept)",
        "transport": f"SFMTA (16 files, many from 1917) and LA Metro ('PD LACMTA', 50 system-map PDFs): {NOT_IN} "
                     "(too few photos; maps)",
        "local": f"'PD California' (9,483 files): LAPD (297) and 'Mug shots by California' (419): {NOT_IN} (police "
                 "and mugshots are never taken); LAFD and LA County Fire (17 files): too few",
    },
    "Colorado": {"universities": "Colorado School of Mines, Commons 'Files from the Colorado School of Mines Flickr "
                                 f"stream' (2,067), each file's licence checked; {BUILT} commons_state_community",
                 "local": f"Colorado Senate GOP and City of Greeley streams: {NOT_IN} (party politics; 2 files)"},
    "Florida": {
        "wildlife": "FWC Fish and Wildlife Research Institute, Commons 'Files from FWC Fish and Wildlife Research "
                    f"Institute Flickr stream' (325), CC BY 2.0; {BUILT} commons_state_outdoors",
        "archives": "State Library and Archives (Florida Memory), Commons 'PD Florida Photographic Collection' "
                    f"(6,545), public domain ({{{{PD-FLGov}}}}); {NOT_IN}: historic photos and postcards (circa 1900 "
                    "to the 1960s in the files read), many by private photographers whose copyright PD-FLGov does "
                    "not cover",
        "transport": f"Florida DOT: {NOT_IN}; PD-FLGov lists FDOT as an agency that may claim copyright, and no open "
                     "Commons copy of its photos was found",
        "local": f"City of Orlando ('Files from the City of Orlando'): {NOT_IN} (videos); 'Mug shots by Florida': "
                 "never",
    },
    "Indiana": {"local": f"Governor Eric Holcomb and Indianapolis Mayor's Office streams: {NOT_IN} (politicians)"},
    "Kansas": {"local": "City of Overland Park, Commons 'Files from the City of Overland Park Flickr stream' (8); "
                        f"{BUILT} commons_state_community"},
    "Maryland": {"local": "Baltimore County Government, Commons 'Files from Baltimore County Government Flickr stream' "
                          f"(2,977), public domain; {BUILT} commons_state_community (most captions are camera "
                          "numbers: set aside for a description)",
                 "archives": "Maryland GovPics (the governor's office stream): no Commons stream category was found by "
                             "title (unverified); it is mostly official events anyway"},
    "Massachusetts": {
        "transport": "MassDOT, Commons 'Files from the MassDOT flickr stream' and '... needing curation' (2,418), "
                     f"public domain as marked by MassDOT; {BUILT} commons_state_roads",
        "environment": "Department of Environmental Protection, Commons 'Files from the Massachusetts Department of "
                       f"Environmental Protection' and '... needing curation' (7,505), CC BY 2.0; {BUILT} "
                       "commons_state_outdoors",
        "local": "City of Boston Archives, Commons 'Files from City of Boston Archives Flickr stream' (5,283), CC BY "
                 f"2.0 and CC BY-SA 2.0 files; {BUILT} commons_state_community (CC BY, 1990 onwards) and {SA_ENTRY}",
    },
    "Michigan": {"local": "City of Detroit, Commons 'Files from City of Detroit Flickr stream' (+ 'with bad file "
                          f"names', 2,878), public domain; {BUILT} commons_state_community; Michigan Lt. Governor "
                          f"stream: {NOT_IN} (politicians)",
                 "universities": f"University of Michigan SEAS stream (10 subcategories): {NOT_IN} (too few)"},
    "Minnesota": {"guard": "Minnesota National Guard, Commons 'Photographs by the Minnesota National Guard' (803), CC "
                           f"BY 2.0; {BUILT} commons_state_response (emergencies only)",
                  "local": f"Governor Walz and Senate DFL streams: {NOT_IN} (politicians)",
                  "museums": f"Minnesota Historical Society (438): {NOT_IN} here (a private nonprofit, not the state; "
                             "mostly historic)"},
    "Missouri": {"archives": "Missouri State Archives, Commons 'Files from Missouri State Archives Flickr stream' "
                             f"(24); {BUILT} commons_state_community (1990 onwards only)"},
    "New Jersey": {"guard": "Department of Military and Veterans Affairs, Commons 'Files from New Jersey Department of "
                            f"Military and Veterans Affairs Flickr stream' (69); {BUILT} commons_state_response"},
    "New York": {"transport": "Metropolitan Transportation Authority, Commons 'Flickr images taken by the Metropolitan "
                              f"Transportation Authority (New York)' (22,953), CC BY 2.0 and 4.0; {BUILT} "
                              "commons_state_roads"},
    "North Carolina": {
        "transport": "NCDOT, Commons 'Files from North Carolina Department of Transportation Flickr stream' (2,715) "
                     "and "
                     f"'Files from NCDOTcommunications Flickr stream' (913), CC BY 2.0 and 4.0; {BUILT} "
                     "commons_state_roads",
        "local": "City of Greenville, Commons 'Files from City of Greenville, North Carolina Flickr stream' (2,858), "
                 f"public domain; {BUILT} commons_state_community",
    },
    "Ohio": {"local": "Development Services Agency, Commons 'Files from Ohio Redevelopment Projects - ODSA Flickr "
                      f"stream' (7,785), CC BY 2.0; {BUILT} commons_state_community; Ohio Attorney General stream: "
                      f"{NOT_IN} (6 files, officials)"},
    "Oregon": {
        "transport": "ODOT, Commons 'Photographs by the Oregon Department of Transportation' (12,485 + 65), CC BY 2.0; "
                     f"{BUILT} commons_state_roads",
        "wildlife": "ODFW, Commons 'Files from Oregon Department of Fish & Wildlife Flickr stream' (122), each file's "
                    f"licence checked; {BUILT} commons_state_outdoors",
        "guard": "Oregon National Guard, Commons 'Files from Oregon National Guard Flickr stream' (4,233), CC BY 2.0; "
                 f"{BUILT} commons_state_response (emergencies only)",
        "universities": "Oregon State University, Commons 'Files from Oregon State University Flickr stream' (835, "
                        f"mostly historic); {BUILT} commons_state_community (1990 onwards only)",
    },
    "Pennsylvania": {"local": "Montgomery County Planning Commission, Commons 'Files from the Montgomery County "
                              "Planning Commission (Pennsylvania) Flickr stream' (159), CC BY-SA 2.0; {sa}; Governor "
                              "Tom Wolf (5,922) and Philadelphia City Council streams: {not_in} "
                              "(politicians)".format(sa=SA_ENTRY, not_in=NOT_IN),
                     "universities": f"Penn State Frost Entomological Museum (54, insect specimens): {NOT_IN}"},
    "South Carolina": {"guard": "South Carolina National Guard, Commons 'Files from the South Carolina National Guard "
                                f"Flickr stream' (213); {BUILT} commons_state_response (emergencies only)"},
    "Tennessee": {"transport": "Knoxville Area Transit, Commons 'Files from Knoxville Area Transit Flickr stream' "
                               f"(166), CC BY-SA 2.0; {SA_ENTRY}",
                  "museums": f"Tennessee State Museum (2 files): {NOT_IN} (too few)"},
    "Texas": {
        "archives": "Texas State Library and Archives Commission, Commons 'Images from the Texas State Library and "
                    f"Archives Commission Flickr stream' (2,229 + 1,250); {BUILT} commons_state_community (1990 "
                    "onwards only: few)",
        "universities": "Texas Tech University student housing (6,588), Texas A&M Memorial Student Center (1,443) "
                        f"and Texas A&M mass import (1,794), each file's licence checked; {BUILT} "
                        f"commons_state_community; Texas State University 'Flickr Commons' (2,855) and Texas Sea "
                        f"Grant (104): {NOT_IN} (not sampled: historic Flickr Commons photos; marine-science "
                        "outreach)",
    },
    "Utah": {"local": f"Utah House Republicans stream (171): {NOT_IN} (party politics)"},
    "Virginia": {
        "parks": "Virginia State Parks, Commons 'Photographs by Virginia State Parks' (25,178) and '... with bad file "
                 f"names' (8,649), CC BY 2.0; {BUILT} commons_state_outdoors",
        "archives": "Library of Virginia, Commons 'Files from The Library of Virginia Flickr stream' (951); "
                    f"{BUILT} commons_state_community (1990 onwards only)",
        "local": f"state Department of Education stream (287; schoolchildren): {NOT_IN}",
    },
    "Washington": {
        "wildlife": "Department of Natural Resources, Commons 'Files from Washington DNR Flickr stream' (15); "
                    f"{BUILT} commons_state_outdoors",
        "archives": "Washington State Archives, Commons 'Files from Washington State Archives Flickr stream' (246); "
                    f"{BUILT} commons_state_community (1990 onwards only)",
        "local": "Seattle Municipal Archives, Commons 'Seattle Municipal Archives via Flickr' (3,195), CC BY 4.0; "
                 f"{BUILT} commons_state_community (mostly before 1990: few kept); Seattle City Council (5,068): "
                 f"{NOT_IN} (politicians)",
        "transport": "WSDOT: the Commons category holds 7 loose files and no copy of its Flickr stream; not used",
    },
    "West Virginia": {"local": f"Governor Jim Justice stream (440): {NOT_IN} (politicians)"},
}


def summary_table():
    """The state-by-state table as Markdown: one row per state (50 states, DC, Puerto Rico), one column per kind of
    agency (AGENCY_KINDS) with what was found (blank: none found on Commons)."""
    kinds = list(AGENCY_KINDS)
    lines = ["| State | " + " | ".join(kinds) + " |", "|" + "---|" * (len(kinds) + 1)]
    for state in sorted(STATE_SUMMARY):
        cells = [STATE_SUMMARY[state].get(k, "").replace("|", "/") for k in kinds]
        lines.append(f"| {state} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


STATE_SIGN_UP = {
    "Flickr API: state agencies' own photostreams (state DOTs such as WSDOT, MnDOT, PennDOT, TxDOT, Caltrans; state "
    "parks, wildlife, health and emergency management offices; state National Guards; state universities)":
        "https://www.flickr.com/services/apps/create/ : a free API key exists (it would come from a GitHub secret "
        "such as FLICKR_API_KEY), but Flickr's API terms (https://www.flickr.com/services/api/tos/) forbid storing "
        "the photos ('Cache or store any Flickr user photos other than for reasonable periods ...'). Only the streams "
        "Commons has copied (with each file's licence reviewed) are used: packs/state_packs.py. A stream under CC BY "
        "or public domain that Commons has not copied can be added by a Commons volunteer (Flickr2Commons) and then "
        "appear here; licences of streams not on Commons were not read.",
    "DVIDS (Defense Visual Information Distribution Service): state National Guard photos":
        "https://www.dvidshub.net : Guard photos taken by members on federal status are US government works, but "
        "DVIDS' bulk API needs a free key (https://api.dvidshub.net, it would come from a GitHub secret such as "
        "DVIDS_API_KEY) and each item's own credit must be checked (some are by state employees or contractors). "
        "Not built here: the Guard streams already on Commons are used; a DVIDS builder could follow.",
}

STATE_NOT_INCLUDED = {
    "Governors', lieutenant governors', legislators', party caucuses' and city councils' Flickr streams (Pennsylvania "
    "Governor Tom Wolf, Indiana Governor Eric Holcomb, West Virginia Governor Jim Justice, Minnesota Governor Walz, "
    "Michigan Lt. Governor, Utah House Republicans, Colorado Senate GOP, Minnesota Senate DFL, Seattle and "
    "Philadelphia City Councils, Indianapolis Mayor's Office, Ohio Attorney General)":
        "on Commons, mostly under CC BY or public domain, but nearly every photo is an official event with named "
        "politicians, which the owner's rule leaves out (as commons_us_agencies does for federal officials).",
    "Mug shots by Florida and California, LAPD (Commons 'PD Florida' and 'PD California')":
        "public domain under those states' laws, but police photos and mugshots are never taken (no crime, evidence "
        "or mugshots).",
    "Florida Memory (State Library and Archives of Florida), Commons 'PD Florida Photographic Collection'":
        "historic photos and postcards (the files read date from about 1900 to the 1960s), and many are by private "
        "photographers, whose copyright Florida's public-records law does not remove (PD-FLGov's own caveat).",
    "Florida Department of Transportation and Florida's state universities":
        "PD-FLGov lists them as agencies Florida law allows to claim copyright ('any works of these agencies should "
        "be assumed to be copyrighted'); no open Commons copy of their photos was found.",
    "Virginia Department of Education Flickr stream (Commons, 287 files)":
        "schoolchildren in classrooms; left out by the owner's rule on children's faces (as school classrooms are in "
        "us_modern_sources.py).",
    "Washington State DOT, Minnesota DOT, PennDOT, TxDOT, Caltrans, Utah DOT, Colorado DOT, Virginia DOT, Illinois DOT":
        "their Commons categories hold only a few loose files (the 52 state DOT categories were read: only Oregon "
        "and Alaska hold thousands, and NCDOT and MassDOT have stream categories of their own); their Flickr streams "
        "are not used (Flickr's API terms) and their licences were not read.",
    "State geological surveys, state agriculture and forestry departments, conservation districts, extension "
    "services, state emergency management agencies, housing finance agencies, health departments and consumer "
    "protection offices":
        "no Commons copy of their photos was found by title (see HOW_SEARCHED). Their own websites were not read "
        "agency by agency (state web pages are copyrighted unless they say otherwise); FEMA's, USDA's and the Forest "
        "Service's own photos of the same work are already in commons_us_agencies.",
    "State fairs": "no state fair photo stream of a state agency was found on Commons; state fairs are already a "
                   "category of us_modern_packs.commons_us_holidays (photos by Commons contributors).",
    "Calisphere (University of California), Digital Commonwealth, state digital libraries (DPLA hubs)":
        "per-item rights statements, mostly 'copyrighted' or 'contact the holder', and mostly historic; Digital "
        "Commonwealth is already archive_packs.digital_commonwealth. Not repeated.",
    "Texas State University 'Flickr Commons' (Commons, 2,855) and other Flickr Commons archive streams":
        "historic photos ('no known copyright restrictions' is how Flickr Commons marks old archive photos); not "
        "sampled for this modern collection.",
    "Non-commercial (CC BY-NC) state streams": "Commons does not keep non-commercial files, and the only other copies "
                                               "are on Flickr (not used), so no non-commercial state entry could be "
                                               "made.",
}

STATE_PERMISSION_CANDIDATES = {
    "Washington State Department of Transportation":
        "Has: thousands of photos of roads, ferries, work zones, snowplows, bridges and rest areas on its Flickr "
        "stream (https://www.flickr.com/photos/wsdot/). Its licence there was not read from this machine; Flickr "
        "cannot be used. Ask (whether its photos may be copied to Wikimedia Commons, or downloaded once, to teach a "
        "describer for blind people): https://wsdot.wa.gov/about/contacts (Communications).",
    "Minnesota Department of Transportation and Minnesota DNR":
        "Has: snowplows, road work, state parks and wildlife photos on Flickr. Ask: "
        "https://www.dot.state.mn.us/contacts/ "
        "and https://www.dnr.state.mn.us/contact/ (licence not read from this machine).",
    "State emergency management agencies (for example Texas, Florida, North Carolina, California Cal OES)":
        "Have: shelters, flooding, storm and wildfire response photos, mostly on Flickr or X. Ask each agency's "
        "public information office whether its photos may be put under CC BY or into the public domain.",
}


def main(argv=None):
    """Print the state-by-state table, or prepare one collection into an empty folder with a small cap and print a
    few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try the state-government collections.")
    parser.add_argument("key", nargs="?", choices=[s.key for s in STATE_SOURCES])
    parser.add_argument("--table", action="store_true", help="print the state-by-state table")
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    if args.table or not args.key:
        print(HOW_SEARCHED + "\n\n" + summary_table())
        return 0
    source = next(s for s in STATE_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="state-")
    work = os.path.join(data, "work")
    os.makedirs(work, exist_ok=True)
    rows = source.prepare(source, data, work, args.cap)
    for row in rows[:8]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
