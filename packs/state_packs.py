"""Pack builders for US STATE, COUNTY and CITY GOVERNMENT photos of modern everyday America (1990 onwards): state
transportation departments and transit authorities (roads, work zones, snowplows, bridges, buses and subways), state
parks, fish and wildlife and environment agencies, state National Guards and the state fire agency at floods, storms,
wildfires and other emergencies, and city, county, state-archive and state-university photo streams. Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" (the agency's state or city),
"child": true where the words of a picture name a child, and "content": "graphic" where they name the dead or
injured. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

WHERE THE PHOTOS COME FROM. Unlike federal works, state and local government works are often copyrighted, so a
photo is only taken here when its OWN licence is open: every photo is a Wikimedia Commons copy of an agency's photo
stream (mostly copied from Flickr by Commons' bots, with Commons' licence review), and each file's own Commons licence
is checked (public domain, CC0 or CC BY; never share-alike, non-commercial or no-derivatives: those files are noted
and left out). Flickr itself is never used (its API terms forbid storing photos; see us_modern_sources.py). The
share-alike files of the same streams (Knoxville Area Transit, City of Boston Archives ...) are a kit entry in
training-kit/kit/state_sources.py, with the state-by-state notes of what was searched, found and left out.

Every answer is the agency's own words or a fixed sentence: "Describe this picture." with the agency's own caption
(credit lines, "Photo:" lines, web addresses and programme notes taken out), and "Who took this photo?" with the
agency named by the Commons category the photo is filed in. A photo is only taken when the file's own author line
names that agency (a photo by a member of the public filed in an agency's category is left out). Nothing is written
by an AI model and nothing is guessed. A free photo whose caption is too short (under six English words, or only the
file name or a number) is set aside for a description (build_packs.needs_description), keeping its marks.

Safety (packs/SOURCE-RULES.md): no sexual content, swimwear or underwear (us_packs.NOT_SHOWN, home_packs.NUDE); no
crime, arrests, prisons, evidence photos or mugshots, and no photo whose words name a victim (CRIME); photos whose
words name the dead or injured are marked "content": "graphic"; every row whose words name a child is marked "child"
(children appear only in everyday scenes: park programmes, parades, sports); official events with politicians and
officials (governors, legislators, mayors, agency chiefs, ribbon cuttings, press events) are left out, as in
us_modern_packs.commons_us_agencies; only photos of 1990 or later (by the file's date and its words). The National
Guard and fire-agency pack keeps only photos whose words name an emergency (flood, storm, snow, wildfire, rescue,
shelter, the COVID-19 response ...), not military training. All four packs show people and are never used for
picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS).

The packs (all open; checked at the source in November 2026):
  commons_state_roads      State transportation departments and transit: Oregon DOT (Commons 'Photographs by the
                           Oregon Department of Transportation', about 12,500 files, CC BY 2.0), North Carolina DOT
                           (two streams, about 3,600 files, CC BY 2.0 and CC BY 4.0), Massachusetts DOT (about 2,400
                           files, marked public domain by MassDOT), Alaska DOT&PF (about 1,800 files, CC BY 2.0) and New
                           York's Metropolitan Transportation Authority (about 23,000 files, CC BY 2.0 and 4.0).
  commons_state_outdoors   State parks, wildlife and environment: Virginia State Parks (about 33,800 files, CC BY
                           2.0), the California Department of Fish and Wildlife (about 1,500, CC BY 2.0), Oregon
                           Department of Fish and Wildlife, Florida FWC's Fish and Wildlife Research Institute,
                           Washington DNR and the Massachusetts Department of Environmental Protection (about 7,500,
                           CC BY 2.0).
  commons_state_response   Emergencies: the Oregon, Arkansas, Minnesota and South Carolina National Guards, New Jersey's
                           Department of Military and Veterans Affairs (public domain or CC BY 2.0) and CAL FIRE
                           (public domain under California law, County of Santa Clara v. Superior Court, 2009; Commons
                           {{PD-CAGov}}), only photos whose words name an emergency.
  commons_state_community  Cities, counties, state archives and state universities: the City of Detroit, the City of
                           Greenville (North Carolina), Baltimore County Government (public domain marks), the
                           Montgomery County Planning Commission (Pennsylvania), Ohio's Development Services Agency
                           (redevelopment projects, CC BY 2.0), the City of Overland Park, the Seattle Municipal
                           Archives (CC BY 4.0), the City of Boston Archives (its CC BY files), the Washington and
                           Missouri State Archives, the Library of Virginia, the Texas State Library and Archives,
                           Texas Tech University student housing, Texas A&M University, the Colorado School of Mines
                           and Oregon State University; only photos of 1990 or later.

    python packs/state_packs.py commons_state_roads --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import math
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from food_packs import with_twins, count_pictures
from home_packs import commons_fetch, file_name, NUDE
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import NOT_A_PHOTO, OTHER_WORDS, in_english
from us_packs import NOT_SHOWN, DESCRIBE_Q
from us_modern_packs import (agency_caption, agency_entries, sample_members, only_the_name, NOT_MODERN, OFFICIAL,
                             GRAPHIC)

WHO_Q = "Who took this photo?"


def agency(category, who, place, pages, author, fire_agency=False):
    """One agency photo stream on Commons: its category, the agency as said in a sentence ("the Oregon Department of
    Transportation (ODOT), a state government agency"), the place it serves ("Oregon, USA"), how many random listing
    pages of 500 files to sample (1 for a small category), and a pattern its files' author line must match.
    fire_agency: a fire agency, whose photos are all about fires (the emergency pack takes them without an emergency
    word, still leaving out training)."""
    return {"category": category, "who": who, "place": place, "pages": pages,
            "author": re.compile(author, re.I), "fire_agency": fire_agency}


STATE_AGENCY = "a state government agency"
ROADS = [
    agency("Photographs by the Oregon Department of Transportation",
           f"the Oregon Department of Transportation (ODOT), {STATE_AGENCY}", "Oregon, USA", 4,
           r"Oregon Department of Transportation|OregonDOT"),
    agency("Photographs by the Oregon Department of Transportation with bad file names",
           f"the Oregon Department of Transportation (ODOT), {STATE_AGENCY}", "Oregon, USA", 1,
           r"Oregon Department of Transportation|OregonDOT"),
    agency("Files from North Carolina Department of Transportation Flickr stream",
           f"the North Carolina Department of Transportation (NCDOT), {STATE_AGENCY}", "North Carolina, USA", 2,
           r"NCDOT|North Carolina Department of Transportation"),
    agency("Files from NCDOTcommunications Flickr stream",
           f"the North Carolina Department of Transportation (NCDOT), {STATE_AGENCY}", "North Carolina, USA", 1,
           r"NCDOT|North Carolina Department of Transportation"),
    agency("Files from the MassDOT flickr stream",
           f"the Massachusetts Department of Transportation (MassDOT), {STATE_AGENCY}", "Massachusetts, USA", 1,
           r"MassDOT|Massachusetts Department of Transportation"),
    agency("Files from the MassDOT flickr stream needing curation",
           f"the Massachusetts Department of Transportation (MassDOT), {STATE_AGENCY}", "Massachusetts, USA", 2,
           r"MassDOT|Massachusetts Department of Transportation"),
    agency("Alaska Department of Transportation & Public Facilities",
           f"the Alaska Department of Transportation and Public Facilities (DOT&PF), {STATE_AGENCY}", "Alaska, USA", 2,
           r"Alaska DOT|akdotpf|Alaska Department of Transportation"),
    agency("Flickr images taken by the Metropolitan Transportation Authority (New York)",
           "the Metropolitan Transportation Authority (MTA), New York State's public transit authority",
           "New York, USA", 5, r"Metropolitan Transportation Authority|\bMTA\b"),
]
OUTDOORS = [
    agency("Photographs by Virginia State Parks",
           f"Virginia State Parks (Virginia Department of Conservation and Recreation), {STATE_AGENCY}",
           "Virginia, USA", 6, r"Virginia State Parks|vastateparks"),
    agency("Photographs by Virginia State Parks with bad file names",
           f"Virginia State Parks (Virginia Department of Conservation and Recreation), {STATE_AGENCY}",
           "Virginia, USA", 2, r"Virginia State Parks|vastateparks"),
    agency("Files from the California Department of Fish and Wildlife Flickr stream",
           f"the California Department of Fish and Wildlife (CDFW), {STATE_AGENCY}", "California, USA", 2,
           r"California Department of Fish and Wildlife|CDFW"),
    agency("Files from Oregon Department of Fish & Wildlife Flickr stream",
           f"the Oregon Department of Fish and Wildlife (ODFW), {STATE_AGENCY}", "Oregon, USA", 1,
           r"Oregon Department of Fish|ODFW"),
    agency("Files from FWC Fish and Wildlife Research Institute Flickr stream",
           "the Fish and Wildlife Research Institute of the Florida Fish and Wildlife Conservation Commission (FWC), "
           + STATE_AGENCY, "Florida, USA", 1, r"\bFWC\b|Fish and Wildlife Research Institute"),
    agency("Files from Washington DNR Flickr stream",
           f"the Washington State Department of Natural Resources (DNR), {STATE_AGENCY}", "Washington, USA", 1,
           r"Washington DNR|Natural Resources"),
    agency("Files from the Massachusetts Department of Environmental Protection needing curation",
           f"the Massachusetts Department of Environmental Protection (MassDEP), {STATE_AGENCY}",
           "Massachusetts, USA", 3, r"Environmental Protection|MassDEP"),
    agency("Files from the Massachusetts Department of Environmental Protection",
           f"the Massachusetts Department of Environmental Protection (MassDEP), {STATE_AGENCY}",
           "Massachusetts, USA", 1, r"Environmental Protection|MassDEP"),
]
GUARD = "the state's National Guard (its photos are US government works)"
RESPONSE = [
    agency("Files from Oregon National Guard Flickr stream", f"the Oregon National Guard, {GUARD}", "Oregon, USA", 3,
           r"Oregon National Guard|Oregon Military"),
    agency("Photographs from the Arkansas National Guard Flickr stream", f"the Arkansas National Guard, {GUARD}",
           "Arkansas, USA", 2, r"Arkansas National Guard"),
    agency("Photographs by the Minnesota National Guard", f"the Minnesota National Guard, {GUARD}", "Minnesota, USA",
           2, r"Minnesota National Guard"),
    agency("Files from the South Carolina National Guard Flickr stream", f"the South Carolina National Guard, {GUARD}",
           "South Carolina, USA", 1, r"South Carolina National Guard|\bSC National Guard|SCNG"),
    agency("Files from New Jersey Department of Military and Veterans Affairs Flickr stream",
           f"the New Jersey Department of Military and Veterans Affairs, {STATE_AGENCY}", "New Jersey, USA", 1,
           r"New Jersey|NJDMAVA"),
    agency("Photographs by the California Department of Forestry and Fire Protection",
           f"the California Department of Forestry and Fire Protection (CAL FIRE), {STATE_AGENCY}", "California, USA",
           1, r"Forestry and Fire|CAL ?FIRE", fire_agency=True),
]
CITY, COUNTY, UNIVERSITY = "a city government", "a county government", "a state public university"
COMMUNITY = [
    agency("Files from City of Detroit Flickr stream", f"the City of Detroit, {CITY}", "Detroit, Michigan, USA", 2,
           r"City of Detroit"),
    agency("Files from City of Detroit Flickr stream with bad file names", f"the City of Detroit, {CITY}",
           "Detroit, Michigan, USA", 2, r"City of Detroit"),
    agency("Files from City of Greenville, North Carolina Flickr stream", f"the City of Greenville, {CITY}",
           "Greenville, North Carolina, USA", 2, r"City of Greenville"),
    agency("Files from Baltimore County Government Flickr stream", f"Baltimore County Government, {COUNTY}",
           "Baltimore County, Maryland, USA", 2, r"Baltimore County"),
    agency("Files from the Montgomery County Planning Commission (Pennsylvania) Flickr stream",
           f"the Montgomery County Planning Commission, part of {COUNTY}", "Montgomery County, Pennsylvania, USA", 1,
           r"Montgomery County"),
    agency("Files from Ohio Redevelopment Projects - ODSA Flickr stream",
           f"the Ohio Development Services Agency (ODSA), {STATE_AGENCY}", "Ohio, USA", 3,
           r"Ohio Redevelopment|ODSA|Development Services"),
    agency("Files from the City of Overland Park Flickr stream", f"the City of Overland Park, {CITY}",
           "Overland Park, Kansas, USA", 1, r"Overland Park"),
    agency("Seattle Municipal Archives via Flickr", "the Seattle Municipal Archives (City of Seattle), a city archive",
           "Seattle, Washington, USA", 2, r"Seattle Municipal Archives"),
    agency("Files from City of Boston Archives Flickr stream", "the City of Boston Archives, a city archive",
           "Boston, Massachusetts, USA", 3, r"City of Boston"),
    agency("Files from Washington State Archives Flickr stream",
           f"the Washington State Archives, {STATE_AGENCY}", "Washington, USA", 1, r"Washington State Archives"),
    agency("Files from Missouri State Archives Flickr stream", f"the Missouri State Archives, {STATE_AGENCY}",
           "Missouri, USA", 1, r"Missouri State Archives"),
    agency("Files from The Library of Virginia Flickr stream", "the Library of Virginia, the state's library and "
                                                               "archives", "Virginia, USA", 1, r"Library of Virginia"),
    agency("Images from the Texas State Library and Archives Commission Flickr stream",
           f"the Texas State Library and Archives Commission, {STATE_AGENCY}", "Texas, USA", 2,
           r"Texas State Library|TSLAC"),
    agency("Files from the Texas Tech University student housing Flickr stream",
           f"Texas Tech University Student Housing, part of {UNIVERSITY}", "Lubbock, Texas, USA", 3, r"Texas Tech"),
    agency("Files from Memorial Student Center Texas A&M University Flickr stream",
           f"the Memorial Student Center of Texas A&M University, {UNIVERSITY}", "College Station, Texas, USA", 1,
           r"Texas A&M|Memorial Student Center|\bMSC\b"),
    agency("Flickr mass import from Texas A&M university pictures", f"Texas A&M University, {UNIVERSITY}",
           "College Station, Texas, USA", 1, r"Texas A&M|\bTAMU\b"),
    agency("Files from the Colorado School of Mines Flickr stream", f"the Colorado School of Mines, {UNIVERSITY}",
           "Golden, Colorado, USA", 2, r"Colorado School of Mines|\bMines\b"),
    agency("Files from Oregon State University Flickr stream", f"Oregon State University, {UNIVERSITY}",
           "Oregon, USA", 1, r"Oregon State University"),
]

# Crime, prisons and victims: never taken (no evidence photos, mugshots or identifiable victims).
CRIME = re.compile(r"\b(arrest\w*|suspects?|inmates?|prisons?|prisoners?|jail\w*|correctional|corrections officers?|"
                   r"crimes?|criminal|homicides?|murder\w*|shootings?|gunman|victims?|mug ?shots?|evidence|"
                   r"autops\w*|overdos\w*|sex offenders?)\b", re.I)
# Official events of state and local government (as us_modern_packs.OFFICIAL, plus the state and city words).
STATE_OFFICIAL = re.compile(r"\b(lieutenant governor|legislat\w*|lawmakers?|state rep\w*|"
                            r"council ?(member|man|woman|president)s?|city council|county executive|"
                            r"ribbon[- ]cutting|groundbreaking|ground[- ]breaking|press (event|release|availability)|"
                            r"news conference|media (event|availability)|board (meeting|of transportation|members?)|"
                            r"chair(man|woman|person)?|ceo|executive director|campaign|candidates?|inaugurat\w*|"
                            r"proclamation|bill signing|state of the (state|city|county)|rededicat\w*|luncheon|"
                            r"gala|banquet|retirement|promotion ceremony|change of command|commission(ing)? "
                            r"ceremony)\b", re.I)
# Words that say a photo shows an emergency or disaster response (the response pack keeps only these).
EMERGENCY = re.compile(r"\b(flood\w*|hurricanes?|tropical storms?|snowstorms?|snow ?(plow\w*|removal)|blizzards?|"
                       r"ice storms?|tornado\w*|wildfires?|forest fires?|brush fires?|grass fires?|house fires?|"
                       r"firefight\w*|blazes?|disasters?|emergenc\w*|sandbag\w*|evacuat\w*|rescue\w*|shelters?|"
                       r"covid\w*|pandemic|vaccin\w*|testing sites?|food banks?|water distribution|debris|levees?|"
                       r"droughts?|earthquakes?|landslides?|mudslides?|power outages?|relief|recovery efforts?|"
                       r"winter storms?|severe weather)\b", re.I)
# Military training and competitions (the emergency pack leaves them out even when a word above appears).
TRAINING = re.compile(r"\b(training|trains?|exercises?|drills?|competitions?|best warrior|qualif\w*|range|"
                      r"marksmanship|howitzers?|artillery|fire mission|live[- ]fire|deploy\w*|mobiliz\w*|"
                      r"annual training|field training|ceremon\w*)\b", re.I)
# Parts of a state or city caption that are not about the picture (added to us_modern_packs.agency_caption's).
STATE_NOISE = re.compile(r"(\bphoto(graph)?( credit)?\s*[:/]\s*[^.]*\.?|\b[A-Z][\w&.-]{1,20} photos? (by|courtesy)"
                         r"\b[^.]*\.?|\([^)]*/\s*(MTA|NYCT|MTA New York City Transit)[^)]*\)|"
                         r"\((low|high|full) resolution[^)]*\)|\bscientific name\s*:\s*|"
                         r"\b\d{6}-[A-Z]-[A-Z0-9]{5}-\d{2,4}\b)", re.I)
# An archive record's fields after its title ("Title: ... Creator: ... Date: ... Source: ... Copyright: ..."): cut off.
RECORD_FIELDS = re.compile(r"\s(Creator|Date|Source|Collection|Rights|Copyright|Photographer)\s*:", re.I)
# Officials' titles before a name ("Gov. Roy Cooper", "Rep. Smith"): official events.
TITLES = re.compile(r"\b(Gov|Lt\. Gov|Rep|Sen|Del|Sec|Supt|Comm)\.\s+[A-Z]")


def state_caption(text):
    """An agency's own caption, cleaned for a state or city photo: "Photo:" and credit lines, a Guard photo's ID
    number and an archive's record fields (Creator:, Source:, Copyright: ...) taken out, then us_modern_packs.
    agency_caption ("Snow removal at Hogg Rock. Photo: ODOT" -> "Snow removal at Hogg Rock."); "" when nothing
    is left."""
    text = re.sub(r"^\s*English\s*:\s*", "", clean(text))
    text = RECORD_FIELDS.split(re.sub(r"^\s*Title\s*:\s*", "", text))[0]
    text = agency_caption(STATE_NOISE.sub(" ", text))
    return re.sub(r"\s+([.,;:!?])", r"\1", text)


def english(text):
    """Whether a caption reads as English: mechanical_packs.in_english, or (a short caption with none of its common
    words, "Snowplow clears Highway 26 near Government Camp") Latin letters only and no common word of another
    language."""
    if in_english(text):
        return True
    return bool(text) and not re.search(r"[^\x00-\u024f\u2010-\u2027\u00b0]", text) and not OTHER_WORDS.search(text)


def author_of(credit):
    """The author part of a credit line made by us_modern_packs.agency_entries ("<title> by <author>, <licence>,
    <page>")."""
    head = credit.rsplit(", ", 2)[0]
    return head.split(" by ", 1)[1] if " by " in head else ""


def licence_of(credit):
    """The licence part of such a credit line."""
    parts = credit.rsplit(", ", 2)
    return parts[1] if len(parts) == 3 else ""


def why_not(words, year, emergency_only):
    """Why a photo is left out by its words and date ("" when it may be taken): nudity or swimwear, crime and victims,
    older than 1990, an official event, or (emergency_only) no emergency named."""
    if NUDE.search(words) or NOT_SHOWN.search(words):
        return "its words are about nudity, swimwear or evidence photos"
    if CRIME.search(words):
        return "its words are about crime, prison or a victim"
    if (year and year < 1990) or NOT_MODERN.search(words):
        return "older than 1990 (by its date or words): this pack is about 1990 onwards"
    if OFFICIAL.search(words) or STATE_OFFICIAL.search(words) or TITLES.search(words):
        return "an official event (officials, ceremonies, meetings), not everyday life"
    if emergency_only and (not EMERGENCY.search(words) or TRAINING.search(words)):
        return "its words name no emergency, or name training (this pack is about emergencies, not training)"
    return ""


def state_rows(caption, spec, credit, words):
    """The rows of one photo: its caption, and which agency took it; marked "child" and "content": "graphic" from
    its words."""
    where = {"place": spec["place"], "place_kind": "origin"}
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, **where},
            {"question": WHO_Q, "answer": f"It is a photo by {spec['who']}.", "credit": credit, **where}]
    rows = [mark_child(r, words) for r in rows]
    if GRAPHIC.search(words):
        rows = [dict(r, content="graphic") for r in rows]
    return rows


def agency_pack(specs, limit, key, prefix, emergency_only=False):
    """One pack from agency streams: each category sampled at random places of its listing (us_modern_packs.
    sample_members), its open-licence photos by that agency (us_modern_packs.agency_entries checks each file's
    licence), the ones that pass why_not with the agency's caption; a free photo whose caption is too short is set
    aside for a description. The categories share the limit."""
    s, rng, items, seen = session(), pass_random(key), [], set()
    share = math.ceil(limit * 1.25 / len(specs))
    for spec in specs:
        if listing_out_of_time():
            break
        category = spec["category"]
        titles = [t for t in sample_members(s, category, spec["pages"], rng)
                  if not NOT_A_PHOTO.search(t) and t not in seen]
        rng.shuffle(titles)
        say(f"Commons {category}: {len(titles)} files sampled")
        got = 0
        for start in range(0, len(titles), 100):
            if got >= share or listing_out_of_time():
                break
            for title, url, credit, raw, year in agency_entries(s, titles[start:start + 100]):
                if got >= share:
                    break
                seen.add(title)
                if not spec["author"].search(author_of(credit)):
                    considered(title, url, "its author line does not name the agency (not the agency's own photo)")
                    continue
                words = f"{title} {raw}"
                reason = why_not(words + (" wildfire" if spec["fire_agency"] else ""), year, emergency_only)
                if reason:
                    considered(title, url, reason)
                    continue
                caption = state_caption(raw)
                if only_the_name(caption, title):
                    caption = ""
                if not caption or len(caption.split()) < 6 or not english(caption):
                    needs_description(file_name(prefix, title), url, credit, licence_of(credit), text=caption,
                                      title=title, reason="its caption is under six English words",
                                      place=spec["place"], place_kind="origin",
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"agency": spec["who"], "commons_category": category, "year": year,
                                             "child": bool(CHILD.search(words)),
                                             "content": "graphic" if GRAPHIC.search(words) else "",
                                             "not_for_picture_making": True})
                    continue
                items.append((file_name(prefix, title), url, state_rows(caption, spec, credit, words)))
                got += 1
        say(f"  {got} photos from {spec['who']}")
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"{key}: {len(fetched)} pictures")
    return with_twins(fetched)


def build_commons_state_roads(limit):
    """State transportation departments and transit authorities."""
    return agency_pack(ROADS, limit, "commons_state_roads", "stroad")


def build_commons_state_outdoors(limit):
    """State parks, fish and wildlife, natural resources and environment agencies."""
    return agency_pack(OUTDOORS, limit, "commons_state_outdoors", "stout")


def build_commons_state_response(limit):
    """State National Guards and the state fire agency at emergencies (only photos whose words name one)."""
    return agency_pack(RESPONSE, limit, "commons_state_response", "stresp", emergency_only=True)


def build_commons_state_community(limit):
    """Cities, counties, state archives and state universities."""
    return agency_pack(COMMUNITY, limit, "commons_state_community", "stcomm")


# ----------------------------------------------------------------- the packs

STATE_CREDIT = ("Wikimedia Commons copies of {what}: each file's own licence checked (public domain, CC0 or CC BY; "
                "credited in CREDITS.txt with its author and file page); captions by the agencies. "
                "https://commons.wikimedia.org")
STATE_PACKS = {
    "commons_state_roads": (build_commons_state_roads, STATE_CREDIT.format(
        what="US state transportation departments' and transit authorities' photo streams (Oregon DOT, North "
             "Carolina DOT, MassDOT, Alaska DOT&PF, New York's MTA)")),
    "commons_state_outdoors": (build_commons_state_outdoors, STATE_CREDIT.format(
        what="US state parks, fish and wildlife and environment agencies' photo streams (Virginia State Parks, "
             "California and Oregon Fish and Wildlife, Florida FWC, Washington DNR, MassDEP)")),
    "commons_state_response": (build_commons_state_response, STATE_CREDIT.format(
        what="US state National Guards' and CAL FIRE's photo streams (emergencies only; Guard photos are US "
             "government works, CAL FIRE's are public domain under California law)")),
    "commons_state_community": (build_commons_state_community, STATE_CREDIT.format(
        what="US city, county, state-archive and state-university photo streams (Detroit, Greenville NC, Baltimore "
             "County, Ohio ODSA, Seattle and Boston archives, Texas, Washington and Missouri archives, Texas Tech, "
             "Texas A&M, Colorado School of Mines, Oregon State University)")),
}

# How many pictures a full build takes from each (each finishes well within about four hours on GitHub's machines).
STATE_LIMITS = {
    "commons_state_roads": 3500,        # 8 categories, about 43,000 files (MTA 23,000, ODOT 12,500), sampled
    "commons_state_outdoors": 3000,     # 8 categories, about 43,000 files (Virginia State Parks 33,800), sampled
    "commons_state_response": 800,      # 6 categories, about 7,800 files; only emergencies are kept
    "commons_state_community": 2500,    # 18 categories, about 40,000 files; much is pre-1990 or official
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one state-government pack builder.")
    parser.add_argument("key", choices=sorted(STATE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--only", default="", help="only the categories whose name contains this (a quick check)")
    args = parser.parse_args(argv)
    if args.only:
        for specs in (ROADS, OUTDOORS, RESPONSE, COMMUNITY):
            specs[:] = [spec for spec in specs if args.only.lower() in spec["category"].lower()] or specs
    entries = STATE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child, "
        f"{sum(1 for _, _, r in entries if r.get('content') == 'graphic')} graphic; places: "
        + ", ".join(f"{p} {n}" for p, n in places.most_common()))
    if build_packs.NEEDS:
        say(f"{len(build_packs.NEEDS)} pictures set aside for a description, e.g. "
            + json.dumps({k: build_packs.NEEDS[0][k] for k in ("name", "reason", "child", "content")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
