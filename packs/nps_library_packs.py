"""Picture packs from the US National Park Service's NPGallery (https://npgallery.nps.gov), by theme (the owner's
request of 2026-11-22 for large, well-captioned public-domain photo collections). Used by build_packs.py in the same
way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a
row is {"question", "answer", "credit"}, with the park as the place ("Where was this photo taken?") and "child": True
when the words mention a child. The limit counts pictures.

These packs extend the repository's general NPGallery pack (documentary_packs.py "npgallery": 6,000 photos found
with 39 general words such as wildlife, canyon, trail and lighthouse) with five themes it does not cover, or covers
only thinly, and reuse its answer and credit (documentary_packs.npg_answer, npg_credit): the park's accessibility alt
text and the first sentences of its description, nothing added. NPGallery holds several hundred thousand photos
(November 2026), read through the search service its own pages use (api/search, 48 records a page; npgallery.nps.gov
has no robots.txt), politely, half a second between pages.

Copyright: only records whose constraint is "Public domain" (work of NPS staff) AND whose photo credit, when there
is one, names the Park Service ("NPS Photo", "NPS / Jane Doe", "National Park Service") are kept (nps_free).
Records crediting anyone else (a volunteer's or partner's photo, "courtesy of", a copyright sign) are left out, even
when marked public domain. Brochures, maps, logos, posters and drawings are left out (documentary_packs
NPG_NOT_A_PHOTO).

The packs (NPS_LIBRARY_PACKS); theme_of() gives each record one theme, in this order, so no photo is in two of them:
  npgallery_accessibility   accessibility features: accessible trails, ramps, lifts, wheelchair-accessible
                            facilities, tactile models and exhibits, braille and audio-described signs, assistive
                            listening, sign-language programmes, accessible campsites and restrooms.
  npgallery_facilities      visitor facilities and signs: visitor centres and their desks and exhibits, entrance
                            stations and park signs, wayside exhibits, trailheads, campgrounds, picnic areas,
                            restrooms, boardwalks, shuttles, amphitheatres, parking areas.
  npgallery_historic_buildings  historic buildings and structures: cabins, houses, barns, mills, churches and
                            missions, courthouses, schools, pueblos and cliff dwellings, ranches, depots, bridges'
                            and buildings' details.
  npgallery_wildlife_more   wildlife the general pack's words miss: deer, moose, wolves, foxes, coyotes,
                            pronghorn, bighorn sheep, mountain goats, sea lions, seals, whales, alligators,
                            turtles, snakes, frogs, salmon, butterflies, owls, eagles, herons, pelicans and others.
  npgallery_landscapes_more landscapes the general pack's words miss: arches, hoodoos, dunes, prairies, meadows,
                            wetlands, swamps, islands, valleys, cliffs, hot springs, tide pools, redwoods, cacti,
                            autumn colour, rock formations.
The wildlife and landscape packs skip any record whose title or keywords hold one of the general pack's words
(documentary_packs.NPG_WORDS), so they rarely take a photo the general pack takes. People in the photos (visitors,
rangers) are described as the park's alt text describes them; children only as the parks show them, in everyday
clothed scenes.

Looked at and not used (November 2026): the NPS Data API (developer.nps.gov, its multimedia galleries) needs a free
API key (sign-up: listed in the kit's nps_library_sources.py); www.nps.gov's own multimedia search pages are under
/search/, which its robots.txt disallows.

    python packs/nps_library_packs.py npgallery_accessibility --limit 8      (prints a few rows: a quick check)
"""

import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, pass_random, already_in_pack, listing_out_of_time
from build_packs import needs_description
from food_packs import count_pictures
from documentary_packs import (NPG, NPG_WORDS, NPG_NOT_A_PHOTO, NOT_SHOWN, npg_answer, npg_credit, picture_rows,
                               get_json, finish)
from places import place_name

# Photo credits that are the Park Service's own.
NPS_CREDIT = re.compile(r"^(NPS|N\.P\.S\.|National Park Service|U\.?S\.? National Park Service)\b", re.I)
NOT_FREE = re.compile(r"copyright|©|\(c\)\s*\d|\bcourtesy\b|creative ?commons|\bCC[- ]BY|all rights reserved|"
                      r"used with permission", re.I)

# The themes, in the order theme_of() tries them: (pack key, words of the theme).
THEMES = [
    ("npgallery_accessibility", re.compile(
        r"\b(accessib\w*|handicap\w*|wheelchairs?|(?-i:ADA)|ramps?|wheelchair lift|elevators?|tactile|braille|"
        r"audio[- ]described|audio description|assistive listening|sign language|(?-i:ASL)|large print|"
        r"mobility (device|aid)s?|all[- ]terrain wheelchair|beach wheelchair|blind visitors?|low vision|deaf|"
        r"hard of hearing)\b", re.I)),
    ("npgallery_facilities", re.compile(
        r"\b(visitor (center|centre|contact station)|information desk|entrance (station|sign)|park sign|"
        r"entrance sign|signs?|signage|wayside( exhibits?)?|exhibits?|trailheads?|campgrounds?|campsites?|"
        r"picnic (area|table|shelter)s?|restrooms?|comfort station|boardwalks?|shuttles?( bus)?|amphitheat(er|re)|"
        r"parking (lot|area)s?|bookstore|museum|kiosk|overlook)\b", re.I)),
    ("npgallery_historic_buildings", re.compile(
        r"\b(cabins?|historic (building|structure|home|district|site)s?|homestead|farmhouse|house|barns?|mills?|"
        r"church(es)?|chapel|missions?|courthouse|schoolhouse|school|pueblos?|cliff dwellings?|kiva|ranch( house)?|"
        r"depot|station house|blacksmith|smokehouse|hotel|lodge|mansion|plantation|architecture|porch|"
        r"chimney|log building|adobe)\b", re.I)),
    ("npgallery_wildlife_more", re.compile(
        r"\b(deer|moose|wol(f|ves)|fox(es)?|coyotes?|pronghorn|bighorn( sheep)?|mountain goats?|sea lions?|seals?|"
        r"whales?|dolphins?|manatees?|alligators?|crocodiles?|turtles?|tortoises?|snakes?|rattlesnakes?|lizards?|"
        r"frogs?|toads?|salamanders?|salmon|trout|fish|butterfl(y|ies)|moths?|bees?|dragonfl(y|ies)|owls?|"
        r"eagles?|hawks?|falcons?|herons?|egrets?|pelicans?|ospreys?|ravens?|woodpeckers?|hummingbirds?|"
        r"marmots?|squirrels?|chipmunks?|pikas?|bats?|beavers?|otters?|raccoons?|bobcats?|mountain lions?|"
        r"cougars?|horses?|burros?|caribou|musk ?ox(en)?)\b", re.I)),
    ("npgallery_landscapes_more", re.compile(
        r"\b(arch(es)?|hoodoos?|dunes?|sand dunes?|prairies?|grasslands?|meadows?|wetlands?|marsh(es)?|swamps?|"
        r"islands?|valleys?|cliffs?|bluffs?|mesas?|buttes?|hot springs?|tide ?pools?|redwoods?|sequoias?|"
        r"cact(us|i)|saguaros?|joshua trees?|fall colou?rs?|autumn|rock formations?|badlands|spires?|"
        r"sandstone|limestone|granite|scenic view|vista|panorama)\b", re.I)),
]
NPS_LIBRARY_KEYS = [key for key, _words in THEMES]
# The themes that repeat the general pack's subjects, and so skip records with its words (see the module docstring).
NEAR_GENERAL = {"npgallery_wildlife_more", "npgallery_landscapes_more"}
GENERAL_WORDS = re.compile(r"\b(" + "|".join(re.escape(w) for w in NPG_WORDS) + r")s?\b", re.I)

# The searches each pack reads; a record is kept only when theme_of() gives the pack's theme. None of these is one
# of the general pack's NPG_WORDS (packs/test_photo_libraries.py checks).
SEARCHES = {
    "npgallery_accessibility": ("accessible", "accessibility", "wheelchair", "accessible trail", "ramp", "tactile",
                                "braille", "audio description", "assistive listening", "sign language",
                                "accessible restroom", "accessible campsite", "large print", "all-terrain wheelchair"),
    "npgallery_facilities": ("visitor center", "entrance sign", "entrance station", "wayside exhibit", "trailhead",
                             "campground", "picnic area", "restroom", "boardwalk", "shuttle", "amphitheater",
                             "parking", "exhibit", "information desk", "sign", "overlook"),
    "npgallery_historic_buildings": ("cabin", "historic building", "homestead", "barn", "mill", "church", "mission",
                                     "courthouse", "schoolhouse", "pueblo", "cliff dwelling", "ranch", "depot",
                                     "adobe", "mansion", "historic structure"),
    "npgallery_wildlife_more": ("deer", "moose", "wolf", "fox", "coyote", "pronghorn", "bighorn sheep",
                                "mountain goat", "sea lion", "seal", "whale", "alligator", "turtle", "snake", "frog",
                                "salmon", "butterfly", "owl", "eagle", "heron", "pelican", "marmot", "squirrel",
                                "bat", "beaver", "otter", "bobcat", "mountain lion", "wild horses", "caribou"),
    "npgallery_landscapes_more": ("arch", "hoodoo", "sand dunes", "prairie", "meadow", "wetland", "swamp", "island",
                                  "valley", "cliff", "hot spring", "tide pool", "redwood", "cactus", "saguaro",
                                  "fall colors", "rock formation", "badlands", "mesa", "vista"),
}


def nps_free(asset):
    """True when an NPGallery record is public domain and credited to the Park Service only (see the docstring)."""
    constraint = clean((asset.get("ConstraintsInformation") or {}).get("Constraint")).lower()
    if constraint != "public domain":
        return False
    credit = clean(asset.get("PhotoCredit"))
    words = " ".join(clean(asset.get(k)) for k in ("Title", "AltText", "Description", "PhotoCredit", "Copyright"))
    if NOT_FREE.search(words):
        return False
    return not credit or bool(NPS_CREDIT.match(credit))


def asset_words(asset):
    """A record's title and keywords as one text (NPGallery gives keywords as a list or a string)."""
    keywords = asset.get("Keywords") or []
    keywords = " ".join(clean(k) for k in keywords) if isinstance(keywords, list) else clean(keywords)
    return f"{clean(asset.get('Title'))} {keywords}"


def theme_of(asset):
    """The one theme (pack key) of an NPGallery record, from its title and keywords first and then with its alt
    text (accessibility only from the title and keywords: project notes in alt text often mention an accessible
    path the photo does not show), or "" when it has none or is not a photo. A wildlife or landscape record whose title or keywords hold one
    of the general pack's words gets no theme (the general pack's subject)."""
    words = asset_words(asset)
    if NPG_NOT_A_PHOTO.search(clean(asset.get("Title"))):
        return ""
    for text in (words, f"{words} {clean(asset.get('AltText'))}"):
        for key, theme in THEMES:
            if key == "npgallery_accessibility" and text != words:
                continue                    # only a title or keyword says a photo is about accessibility
            if theme.search(text):
                return "" if key in NEAR_GENERAL and GENERAL_WORDS.search(words) else key
    return ""


def park_of(asset):
    """The park as a place ("Dinosaur National Monument, USA") when the record names exactly one park, else ""."""
    units = [clean(u.get("Name")) for u in asset.get("NPSUnits") or [] if clean(u.get("Name"))]
    return place_name(units[0], "USA") if len(units) == 1 else ""


def gallery_items(key, limit, s=None):
    """[(file name, picture address, rows)] for one pack: pages of each of its SEARCHES (from a random page within
    the first ten, then onwards), keeping the free photos of its own theme with alt text of six words or more (each
    answer once); free photos of the theme without such alt text are set aside for a description."""
    s, rng = s or session(), pass_random(sum(map(ord, key)) * 17)
    searches = list(SEARCHES[key])
    want = int(limit * 1.3) + 4
    per_search = want // len(searches) + 2
    items, seen, answers = [], set(), set()
    for word in searches:
        if listing_out_of_time():
            say(f"  {key}: stopped looking at half the time limit")
            break
        found, start = 0, rng.randint(1, 10)
        for page in list(range(start, start + 40)) + list(range(1, start)):
            time.sleep(0.5)
            data = get_json(s, NPG + "api/search", {"keyword": word, "page": page})
            results = (data or {}).get("Results") or []
            for result in results:
                asset = result.get("Asset") or {}
                asset_id = asset.get("AssetID")
                if not asset_id or asset_id in seen or asset.get("PrimaryType") != "image":
                    continue
                seen.add(asset_id)
                name, picture = f"npgallery-{asset_id}.jpg", f"{NPG}GetAsset/{asset_id}/proxyhires.jpg"
                if theme_of(asset) != key or not nps_free(asset) or already_in_pack(name, picture):
                    continue
                answer = npg_answer(asset)
                if not answer:
                    if not NOT_SHOWN.search(clean(asset.get("AltText"))):
                        needs_description(name, picture, npg_credit(asset), "public domain",
                                          text=clean(asset.get("AltText")), title=clean(asset.get("Title")),
                                          place=park_of(asset), page_url=f"{NPG}AssetDetail/{asset_id}",
                                          reason="no accessibility alt text of six words or more",
                                          extra={"description": clean(asset.get("Description"))[:600],
                                                 "keywords": asset_words(asset)[:300]})
                    continue
                if answer in answers:
                    continue
                answers.add(answer)
                items.append((name, picture, picture_rows(answer, npg_credit(asset), park_of(asset),
                                                          [clean(asset.get("Title"))])))
                found += 1
            if found >= per_search or len(results) < 48:
                break
        if len(items) >= want:
            break
    say(f"  {key}: {len(items)} usable photos")
    return items


def build_nps(key, limit):
    """One themed NPGallery pack (see the module docstring)."""
    return finish(key, gallery_items(key, limit), limit, workers=4, pause=0.3)


NPS_TERMS = ("U.S. National Park Service, NPGallery, https://npgallery.nps.gov : photos marked 'Public domain' and "
             "credited to the Park Service (records crediting anyone else are left out), each with the credit the "
             "park asks for, below. Alt text and descriptions by the parks.")
NPS_LIBRARY_PACKS = {key: ((lambda limit, key=key: build_nps(key, limit)), NPS_TERMS) for key in NPS_LIBRARY_KEYS}

# How many pictures a full build takes from each pack (NPGallery holds several hundred thousand records in all).
NPS_LIBRARY_LIMITS = {
    "npgallery_accessibility": 1500,        # NPGallery has a few thousand accessibility photos
    "npgallery_facilities": 3000,           # of tens of thousands of visitor centre, sign and campground photos
    "npgallery_historic_buildings": 3000,   # of tens of thousands (NPGallery also holds the National Register files)
    "npgallery_wildlife_more": 3000,        # of tens of thousands of animal photos
    "npgallery_landscapes_more": 3000,      # of tens of thousands of landscape photos
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one themed NPGallery pack builder.")
    parser.add_argument("key", choices=sorted(NPS_LIBRARY_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = NPS_LIBRARY_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
