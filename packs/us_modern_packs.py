"""Pack builders for MODERN AMERICA (roughly the 1990s to today): the everyday places, things, events, controls,
forms and photos a blind American meets. Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"}, plus "place" where the record names one, "child": true where the words of a picture name a child,
"content": "graphic" where they name the dead or injured, and "facts" where the source gives more than the answer
says. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose
"file" names the same picture (food_packs.with_twins). The limit counts pictures.

Every answer is a fixed sentence written here from the source's own records: the name of the Commons category a
photo sits in, the photo's own caption (for the agency photos, the caption the US government agency wrote), the
official form's own title and printed heading, or a person's description (ImageInWords). Nothing is written by an AI
model and nothing is guessed: a reading of a dial or display is given only where the photo's own description says
it ("the thermostat is set to 68 degrees").

Safety (packs/SOURCE-RULES.md): no sexual content (files whose words name nudity, underwear or swimwear are left
out, with us_packs.NOT_SHOWN, which also leaves out crime-scene and evidence photos and mugshots); children only in
everyday clothed scenes, and every row whose words name a child is marked "child"; graduations are adults only (files
of school, high-school and kindergarten graduations, or whose words name a child, are left out); school cafeterias
are not taken at all; hospital photos whose words name a patient, surgery or an injury are left out; agency photos
whose words name the dead or injured are marked "content": "graphic". The packs that show people are never used for
picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS): commons_us_agencies, commons_us_holidays,
commons_us_eating_out, commons_us_getting_around and commons_us_public_places. The controls, forms and ImageInWords
packs may be.

The packs (all open; checked at the source in November 2026):
  commons_us_agencies      Wikimedia Commons copies of US federal agencies' own photo streams: the US Department of
                           Agriculture (farms, food, school meals, farmers markets, rural life), FEMA (disasters and
                           recovery, shelters, rebuilt homes), Housing and Urban Development (homes, neighbourhoods,
                           housing programmes), and the Forest Service (official events, speeches and meetings
                           are left out). Public domain as works of the US government (17 U.S.C. 105; each file's own
                           Commons licence is checked: PD-USGov, CC0 or CC BY). "Describe this picture." with the
                           agency's own caption (credit lines and web addresses taken out); only photos taken in 1990
                           or later where the file gives a date. A free photo whose caption is too short is set aside
                           for a description (build_packs.needs_description).
  commons_us_controls      Commons: the controls and machines a blind person has to work: dishwashers, clothes
                           dryers, electric ovens and cooking stoves, TV remote controls and their buttons,
                           self-checkouts, card payment terminals, fuel pumps with a card reader, vending machines,
                           MetroCard and stamp machines, parcel lockers, keypads, light switches, smoke detectors,
                           fire-alarm pull stations, US pedestrian signals and their push buttons, parking meters,
                           drinking fountains and US curb cuts. "What is this?" with what it is and how it is used;
                           "What does the display or dial show?" ONLY when the file's own description gives a
                           reading or setting. (Thermostats, microwave ovens, washing machines, lift buttons, ATMs,
                           ticket and check-in machines are already home_packs.commons_appliances; gas cookers are
                           commons_kitchen; dashboards and warning lights mechanical_packs; tactile paving
                           disability_packs: none is repeated here.)
  commons_us_holidays      Commons: American holidays, events and seasons: Thanksgiving, Halloween, the Fourth of July
                           and fireworks, Christmas lights, Easter, Saint Patrick's Day, the Super Bowl, tailgate
                           parties, state fairs, rodeos, parades, farmers markets, garage sales, graduation ceremonies
                           (adults) and voting and polling stations. "What is happening here?"
  commons_us_eating_out    Commons: eating out and food shopping in America: diners, fast-food restaurants and their
                           insides, food trucks, barbecue and barbecue restaurants, coffee shops, pizzerias, hot-dog
                           stands, delicatessens, bakeries, ice-cream parlours, convenience stores, food courts and
                           supermarket aisles. "What kind of place is this?"
  commons_us_getting_around Commons: getting around: New York City Subway, Chicago 'L', Washington Metro, BART and
                           SEPTA stations, Amtrak stations, bus stops and shelters, light rail, airport terminals and
                           their insides, airport security and the TSA, parking garages, gas stations and fuel pumps,
                           electric-car charging stations. "What kind of place is this?"
  commons_us_public_places Commons: public places and services: post offices (and their insides), the DMV, bank
                           branches, pharmacies and drugstores, laundromats, gyms, hospital rooms and corridors (no
                           patients), waiting rooms, libraries, offices, church insides, stadium insides, shopping
                           malls, courthouses, city halls, fire stations, hotel lobbies, motels, hardware and
                           department stores, elevators and escalators. "What kind of place is this?"
  us_federal_forms         Blank official US government forms, each page drawn from the agency's own PDF (pypdfium2):
                           IRS tax forms (W-4, W-9, 1040 and its schedules, 1099s, 1095-A and others), Medicare's
                           CMS-1490S, OPM's SF-2809, the VA's 21-526EZ and the EEOC "Know Your Rights" poster.
                           "What is this form?" from the PDF's own title ("This is IRS Form W-4 for 2026, Employee's
                           Withholding Certificate."), "What does it say at the top?" from the words printed in the
                           top part of the page, and "Is this form filled in?" (no: these are the agencies' blank
                           forms). Never a filled-in form or anyone's own document. IRS: "Content on this website
                           that was created or maintained by federal employees in the course of their duties is not
                           subject to copyright and may be freely copied." (https://www.irs.gov/about-irs/use-of-
                           content-from-irsgov). The other forms are US government works (17 U.S.C. 105).
  imageinwords             ImageInWords (Garg et al., Google, 2024; https://google.github.io/imageinwords/): "IIW
                           human-authored descriptions (image and object level annotations) ... The datasets are
                           released under a CC-BY-4.0 license". The IIW-400 and DOCCI_Test sets, whose photos are
                           DOCCI's ("The annotations and images are licensed by Google LLC under CC BY 4.0 license",
                           https://google.github.io/docci/): "Describe this picture in detail." with the person's
                           hyper-detailed description, and "Describe the <thing> in this picture." with the
                           person's description of up to three objects. The machine-written IIW-P5B texts are never
                           used. (The DCI_Test set's photos are SA-1B's, which need Meta's research licence: a
                           sign-up item in training-kit/kit/us_modern_sources.py.)

The share-alike Commons files of the same categories, the C3PI pill photos (research use) and the sign-up,
permission and not-included collections (Flickr's API, DailyMed labels, USPS forms ...) are in
training-kit/kit/us_modern_sources.py.

    python packs/us_modern_packs.py commons_us_controls --limit 8      (prints a few rows: a quick check)
"""

import collections
import io
import json
import math
import re
import string
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, fetch_all, needs_description
from build_packs import pass_random, first_sentences, DETAILED
from food_packs import with_twins, count_pictures, commons_get, sentence
from home_packs import commons_fetch, file_name, NUDE
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import MECH_FREE, NOT_A_PHOTO, in_english
from us_packs import us_spec, us_commons, NOT_SHOWN, DESCRIBE_Q, WHAT_Q, PLACE_Q

HAPPENING_Q = "What is happening here?"
READING_Q = "What does the display or dial show?"
FORM_Q = "What is this form?"
TOP_Q = "What does it say at the top?"
FILLED_Q = "Is this form filled in?"
USA = "USA"


def drop_items(items, pattern, why):
    """The (name, address, rows) items whose rows' answers and facts do not match pattern; the others are noted
    with why (considered())."""
    kept = []
    for name, url, rows in items:
        words = " ".join(f"{r.get('answer', '')} {json.dumps(r.get('facts', {}))}" for r in rows)
        if pattern.search(words):
            considered(name, url, why)
            continue
        kept.append((name, url, rows))
    return kept


# Words that say a photo is not of modern America: a year before 1990, a decade before the 1990s, a museum piece.
NOT_MODERN = re.compile(r"\b(18\d\d|19[0-8]\d)s?\b|\b(19)?[2-8]0s\b|\b(museum|antique|vintage|historic(al)?|"
                        r"old enough|exhibit(ed)?|replica|restored|circa|c\. ?19)\b", re.I)


# Words that say a photo filed under a US category was taken abroad (US forces' holiday events overseas).
ABROAD = re.compile(r"\b(Japan|Okinawa|Germany|Korea|Iraq|Afghanistan|Kuwait|Italy|Spain|England|United Kingdom|"
                    r"Britain|Poland|Romania|Bahrain|Qatar|Djibouti|Philippines|Syria|Kosovo|Bosnia|Belgium|"
                    r"Netherlands|France|Turkey|Israel|Jordan|Saudi Arabia|Mexico|Canada|Cuba|Guantanamo|Greece|"
                    r"Hungary|Lithuania|Latvia|Estonia|Norway|Thailand|Australia|Honduras|Africa|Europe|"
                    r"overseas|deployed)\b")


def commons_specs_pack(specs, limit, prefix, after=None):
    """A Commons pack from us_packs category specs (us_packs.us_commons: the categories take turns), without the
    photos whose words say they are older than 1990 or museum pieces, and with after(items) to change or drop items
    before the pictures are downloaded."""
    items = us_commons(specs, int(limit * 1.4) + 4, prefix)
    items = drop_items(items, NOT_MODERN, "its words say it is older than 1990 or a museum piece (this pack is about "
                                          "modern America)")
    in_usa = [i for i in items if str(i[2][0].get("place", "")).endswith(USA)]
    abroad = {i[0] for i in in_usa} - {i[0] for i in drop_items(in_usa, ABROAD, "its words say it was taken outside "
                                                                               "the USA (US troops abroad are filed "
                                                                               "under US holidays too)")}
    items = [i for i in items if i[0] not in abroad]
    items = recent_only(items)
    if after:
        items = after(items)
    return with_twins(commons_fetch(items)[:limit])


def commons_title(credit):
    """The Commons file title from a credit line ending in its file page ("... https://commons.wikimedia.org/wiki/
    File:A_b.jpg" -> "File:A b.jpg"); ""."""
    import urllib.parse
    m = re.search(r"commons\.wikimedia\.org/wiki/(File:\S+)\s*$", credit or "")
    return urllib.parse.unquote(m.group(1)).replace("_", " ") if m else ""


def recent_only(items):
    """The items whose Commons file is dated 1990 or later, or not dated (the file page's "date", read 50 files a
    request); the others are noted as too old."""
    s, years = session(), {}
    titles = [commons_title(rows[0].get("credit")) for _, _, rows in items]
    wanted = [t for t in dict.fromkeys(titles) if t]
    for start in range(0, len(wanted), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(wanted[start:start + 50]), "prop": "imageinfo",
                               "iiprop": "extmetadata", "iiextmetadatafilter": "DateTimeOriginal"})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            years[p.get("title")] = photo_year(((p.get("imageinfo") or [{}])[0]).get("extmetadata") or {})
        time.sleep(1)
    kept = []
    for item, title in zip(items, titles):
        if 0 < years.get(title, 0) < 1990:
            considered(item[0], item[1], f"dated {years[title]}: this pack is about 1990 onwards")
            continue
        kept.append(item)
    return kept


# ----------------------------------------------------------------- commons_us_agencies

# (Commons category, the agency as said in a sentence, how many listing pages of 500 to sample)
AGENCIES = [
    ("Files from U.S. Department of Agriculture Flickr stream", "the US Department of Agriculture (USDA)", 6),
    ("Photographs by the U.S. Department of Agriculture", "the US Department of Agriculture (USDA)", 2),
    ("Photographs by the U.S. Department of Housing and Urban Development",
     "the US Department of Housing and Urban Development (HUD)", 4),
    ("Images from FEMA", "the Federal Emergency Management Agency (FEMA)", 0),      # 0: its subcategories (by event)
    ("FEMA News Photos", "the Federal Emergency Management Agency (FEMA)", 1),
    ("Files from Forest Service, USDA Flickr stream", "the US Forest Service", 3),
]
# Official events (officials' speeches, meetings, signings, award ceremonies): not everyday life, left out.
OFFICIAL = re.compile(r"\b(secretary|deputy secretary|administrator|under ?secretary|commissioner|senator|"
                      r"congress(man|woman)|governor|mayor|roundtable|round table|press conference|remarks|keynote|"
                      r"swearing|sworn|signing|award(s| ceremony)|town hall|summit|delegation|briefing|"
                      r"federalist society)\b", re.I)
# Parts of an agency caption that are not about the picture: credit lines, web addresses, hashtags, ID numbers.
CAPTION_NOISE = re.compile(r"(\(?\b(USDA|FEMA|HUD|U\.S\.|DOE|Forest Service)[\w ./-]{0,30}(photo|photograph|image)\b"
                           r"[^.]*\.?\)?|\bphotos? (by|courtesy( of)?)\b[^.]*\.?|https?://\S+|www\.\S+|#\w+|"
                           r"\bOriginal (image|public domain image) from\b[^.]*\.?|\bFEMA/\S+|"
                           r"\b(file|photo) (number|no\.?|id)\s*[:#]?\s*\S+)", re.I)
# Sentences that are about the agency's programmes or rules, not the picture.
CAPTION_NOT_PICTURE = re.compile(r"\b(for more information|visit|learn more|click|follow us|usda is an equal "
                                 r"opportunity|copyright|all rights reserved|in accordance with|this photo|"
                                 r"descriptive metadata|original digital file)\b", re.I)
GRAPHIC = re.compile(r"\b(dead|deaths?|died|bod(y|ies)|corpses?|killed|fatalit\w*|casualt\w*|injured|injur\w*|"
                     r"wounded|blood\w*|morgue)\b", re.I)


def agency_caption(text):
    """An agency's own caption without its credit line, web addresses and programme notes: "Beginning farmer Ana
    Lopez checks her tomatoes in Davis, Calif., July 12, 2016. USDA photo by Lance Cheung. For more information
    visit www.usda.gov" -> "Beginning farmer Ana Lopez checks her tomatoes in Davis, Calif., July 12, 2016."
    (at most about 70 words); "" when nothing is left."""
    text = re.sub(r"^\s*English\s*:\s*", "", clean(text))
    text = CAPTION_NOISE.sub(" ", text)
    kept = [s for s in re.split(r"(?<=[.!?])\s+", clean(text)) if s and not CAPTION_NOT_PICTURE.search(s)]
    text = first_sentences(" ".join(kept), 70)
    return sentence(clean(text).strip(" ,;-")) if text else ""


def only_the_name(caption, title):
    """True when a caption only repeats the file's name ("20161111-Veterans Memorial Assembly at War Memorial Plaza,
    New Castle, DE-1382." for "File:20161111-Veterans Memorial Assembly ... DE-1382 (31318799326).jpg"), or starts
    with a date code as file names do."""
    if re.match(r"^\d{6,8}\b", caption or ""):
        return True
    words = lambda text: set(re.findall(r"[a-z]{3,}", text.lower()))      # noqa: E731 - a one-line helper
    said = words(caption)
    return bool(said) and said <= words(title)


def photo_year(meta):
    """The year a Commons file was taken, from its DateTimeOriginal metadata (the file page's "date"); 0 when not
    given."""
    for key in ("DateTimeOriginal",):         # (DateTime is when the file was last changed: not used)
        m = re.search(r"\b(19[0-9]{2}|20[0-9]{2})\b", clean((meta.get(key) or {}).get("value")))
        if m:
            return int(m.group(1))
    return 0


def sample_members(s, category, pages, rng):
    """Up to pages x 500 file titles of a large Commons category, starting at random places of its sort order (so a
    category of 76,000 files is not listed whole); pages 0 lists its subcategories' files instead (a few each)."""
    titles = []
    if not pages:
        data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}",
                               "cmtype": "subcat", "cmlimit": 500})
        subs = [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]
        rng.shuffle(subs)
        for sub in subs[:30]:
            if listing_out_of_time():
                break
            data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": sub, "cmtype": "file",
                                   "cmlimit": 200})
            titles += [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]
            time.sleep(1)
        return titles
    for _ in range(pages):
        if listing_out_of_time():
            break
        params = {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{category}", "cmtype": "file",
                  "cmlimit": 500}
        if pages > 1:                  # a small category (one page) is read from its start
            params["cmstartsortkeyprefix"] = rng.choice(string.ascii_uppercase + string.digits)
        found = [m["title"] for m in (commons_get(s, params).get("query") or {}).get("categorymembers", [])]
        if not found and "cmstartsortkeyprefix" in params:      # past the last file: read from the start
            params.pop("cmstartsortkeyprefix")
            found = [m["title"] for m in (commons_get(s, params).get("query") or {}).get("categorymembers", [])]
        titles += found
        time.sleep(1)
    return list(dict.fromkeys(titles))


def agency_entries(s, titles):
    """[(title, picture address, credit, caption, year)] for Commons files whose licence is public domain, CC0 or
    CC BY (photos only), 50 at a time; the files left out are noted with the reason."""
    out = []
    for start in range(0, len(titles), 50):
        batch = titles[start:start + 50]
        data = commons_get(s, {"action": "query", "titles": "|".join(batch), "prop": "imageinfo",
                               "iiprop": "url|extmetadata|mime", "iiurlwidth": 1280,
                               "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|DateTimeOriginal",
                               "iiextmetadatalanguage": "en"})
        for p in ((data.get("query") or {}).get("pages") or {}).values():
            if not p.get("pageid"):
                continue
            info = (p.get("imageinfo") or [{}])[0]
            meta = info.get("extmetadata") or {}
            licence = clean((meta.get("LicenseShortName") or {}).get("value"))
            page = "https://commons.wikimedia.org/wiki/" + p["title"].replace(" ", "_")
            if not MECH_FREE.match(licence) or re.search(r"\b(SA|NC|ND)\b|-SA|-NC|-ND", licence.upper()):
                considered(p["title"], page, f"its licence ({licence or 'none given'}) is not public domain, CC0 or "
                                             "CC BY")
                continue
            if info.get("mime") not in ("image/jpeg", "image/png") or not info.get("thumburl"):
                considered(p["title"], page, f"not a photo ({info.get('mime') or 'no picture'})")
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "a US government photographer"
            raw = clean((meta.get("ImageDescription") or {}).get("value"))
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}",
                        raw, photo_year(meta)))
        time.sleep(1)
    return out


def agency_rows(caption, agency, credit, words):
    """The rows of one agency photo: its caption, and which agency took it; marked "child" and "content": "graphic"
    from its words."""
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, "place": USA, "place_kind": "origin"},
            {"question": "Who took this photo?", "answer": f"It is a photo by {agency}, a US government agency.",
             "credit": credit}]
    rows = [mark_child(r, words) for r in rows]
    if GRAPHIC.search(words):
        rows = [dict(r, content="graphic") for r in rows]
    return rows


def build_commons_us_agencies(limit):
    """The US agency photos pack: each agency's category sampled at random places, its free photos of 1990 or later
    with the agency's caption; a free photo with a caption under six words is set aside for a description."""
    s, rng, items, seen = session(), pass_random(1990), [], set()
    share = math.ceil(limit * 1.2 / len(AGENCIES))
    for category, agency, pages in AGENCIES:
        if listing_out_of_time():
            break
        titles = [t for t in sample_members(s, category, pages, rng) if not NOT_A_PHOTO.search(t) and t not in seen]
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
                words = f"{title} {raw}"
                if NUDE.search(words) or NOT_SHOWN.search(words):
                    considered(title, url, "its words are about nudity, swimwear or evidence photos")
                    continue
                if year and year < 1990:
                    considered(title, url, f"taken in {year}: this pack is about 1990 onwards")
                    continue
                caption = agency_caption(raw)
                if caption and OFFICIAL.search(caption):
                    considered(title, url, "an official event (speeches, meetings, ceremonies), not everyday life")
                    continue
                if only_the_name(caption, title):
                    caption = ""
                if not caption or len(caption.split()) < 6 or not in_english(caption):
                    needs_description(file_name("usgov", title), url, credit, "public domain (US government work)",
                                      text=caption, title=title, reason="its caption is under six English words",
                                      place=USA, place_kind="origin",
                                      page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"agency": agency, "commons_category": category, "year": year,
                                             "child": bool(CHILD.search(words)),
                                             "content": "graphic" if GRAPHIC.search(words) else "",
                                             "not_for_picture_making": True})
                    continue
                items.append((file_name("usgov", title), url, agency_rows(caption, agency, credit, words)))
                got += 1
        say(f"  {got} photos from {agency}")
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"commons_us_agencies: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- commons_us_controls

def thing(category, answer, depth=1, place=""):
    """A spec asking "What is this?"."""
    return us_spec(category, WHAT_Q, answer, place, depth)


CONTROLS = [
    thing("Dishwashers", "This is a dishwasher: a machine that washes dishes, with a control panel of buttons or a "
                         "dial to choose the wash cycle."),
    thing("Clothes dryers", "This is a clothes dryer (tumble dryer), with a dial or buttons to choose the drying "
                            "time, heat and cycle."),
    thing("Combo washer dryers", "This is a washer-dryer: one machine that washes and then dries clothes.", 0),
    thing("Electric ovens", "This is an electric oven, with knobs or buttons to set the temperature and the timer."),
    thing("Cooking stoves", "This is a cooking stove (range): burners on top, often an oven below, worked by knobs "
                            "or buttons."),
    thing("Television remote controls", "This is a TV remote control, with buttons for power, channels, volume and "
                                        "menus."),
    thing("Television remote control buttons", "These are the buttons of a TV remote control.", 0),
    thing("Supermarket self-checkouts", "This is a self-checkout in a supermarket: you scan your own items, bag "
                                        "them and pay at the screen.", 0),
    thing("Self checkouts", "This is a self-checkout machine: you scan and pay for your own items.", 1),
    thing("Payment terminals", "This is a card payment terminal (card reader): you insert, swipe or tap a bank "
                               "card or phone, and may type a PIN on its keypad."),
    thing("Fuel pumps with payment terminal", "This is a fuel pump with a card reader, so you pay at the pump.", 0),
    thing("Food and drink vending machines in the United States", "This is a food or drink vending machine in the "
                                                                  "USA: choose with the buttons, then pay.", 0, USA),
    thing("Vending machines in the United States", "This is a vending machine in the USA.", 1, USA),
    thing("MetroCard vending machines", "This is a MetroCard vending machine in the New York City Subway, for buying "
                                        "and refilling fare cards.", 0, "New York City, New York, USA"),
    thing("Parcel lockers in the United States", "These are parcel lockers in the USA: you collect a package with a "
                                                 "code.", 0, USA),
    thing("Keypads", "This is a keypad: number buttons for typing a code."),
    thing("Light switches", "This is a light switch."),
    thing("Smoke detectors", "This is a smoke detector (smoke alarm), usually on the ceiling."),
    thing("Fire alarm pull stations", "This is a fire alarm pull station: pull the handle to sound the fire alarm.",
          1),
    thing("Pedestrian signals in the United States", "This is a pedestrian signal in the USA: a walking person "
                                                     "means walk, a raised hand means don't walk (often with a "
                                                     "countdown).", 1, USA),
    thing("Pedestrian signal push buttons in the United States", "This is a pedestrian push button at a US "
                                                                 "crossing: press it to ask for the walk signal; "
                                                                 "accessible ones have a raised arrow and speak or "
                                                                 "vibrate.", 1, USA),
    thing("Parking meters in the United States", "This is a parking meter in the USA: pay here for street "
                                                 "parking.", 1, USA),
    thing("Drinking fountains", "This is a drinking fountain (water fountain)."),
    thing("Curb cuts in the United States", "This is a curb cut (curb ramp) in the USA: the curb slopes down to "
                                            "the street so wheelchairs and strollers can cross.", 1, USA),
    thing("Keurig", "This is a Keurig coffee maker: put in a coffee pod and press the brew button.", 0),
    thing("Garage door openers", "This is a garage door opener.", 0),
]
# A description that gives a reading or a setting ("set to 350 degrees", "shows 12:45", "the dial is on Normal").
READING = re.compile(r"\b(set (to|at)|showing|shows|displaying|displays|reads|reading|turned to|pointing to|dial "
                     r"(is )?(on|at)|display(ing)? (of|the)|\d+\s*(°|degrees|deg\b|minutes?|seconds?)|\d{1,2}:\d\d)\b",
                     re.I)


def with_readings(items):
    """Add "What does the display or dial show?" to the controls whose own description gives a reading or a
    setting (the answer is that description's sentence that says it)."""
    out = []
    for name, url, rows in items:
        text = next((r["answer"] for r in rows if r["question"] == DESCRIBE_Q), "")
        said = [x for x in re.split(r"(?<=[.!?])\s+", text) if READING.search(x)]
        if said:
            rows = rows + [dict(rows[0], question=READING_Q, answer=sentence(said[0]), facts={})]
        out.append((name, url, rows))
    return out


def build_commons_us_controls(limit):
    """The Commons controls and machines pack."""
    return commons_specs_pack(CONTROLS, limit, "usctrl", after=with_readings)


# ----------------------------------------------------------------- commons_us_holidays

def happening(category, answer, depth=1):
    """A spec asking "What is happening here?" in the USA."""
    return us_spec(category, HAPPENING_Q, answer, USA, depth)


HOLIDAYS = [
    happening("Thanksgiving in the United States", "This is Thanksgiving in the USA, the November holiday of family "
                                                   "dinners, often with turkey."),
    happening("Halloween in the United States", "This is Halloween in the USA (31 October): costumes, "
                                                "trick-or-treating, pumpkins and spooky decorations."),
    happening("Halloween decorations in the United States", "These are Halloween decorations in the USA."),
    happening("Independence Day (United States)", "This is the Fourth of July, Independence Day in the USA: "
                                                  "parades, flags, cookouts and fireworks."),
    happening("Fireworks in the United States", "This is a fireworks display in the USA."),
    happening("Christmas lights in the United States", "These are Christmas lights in the USA, on houses, trees or "
                                                       "streets."),
    happening("Christmas decorations in the United States", "These are Christmas decorations in the USA."),
    happening("Easter in the United States", "This is Easter in the USA."),
    happening("Saint Patrick's Day in the United States", "This is Saint Patrick's Day in the USA (17 March), with "
                                                          "green clothes and parades."),
    happening("Super Bowl", "This is the Super Bowl, the championship game of American professional football."),
    happening("Tailgate parties", "This is a tailgate party: people eating and drinking around their cars in a "
                                  "parking lot before a game."),
    happening("State fairs in the United States", "This is a state fair in the USA: rides, farm animals, food stalls "
                                                  "and shows."),
    happening("Rodeos in the United States", "This is a rodeo in the USA: riders roping calves and riding horses "
                                             "and bulls."),
    happening("Parades in the United States", "This is a parade in the USA."),
    happening("Farmers' markets in the United States", "This is a farmers market in the USA: stalls selling fresh "
                                                       "food straight from farms."),
    happening("Garage sales", "This is a garage sale (yard sale): people selling used things in front of their "
                              "home."),
    happening("Graduation ceremonies in the United States", "This is a graduation ceremony in the USA, with caps and "
                                                            "gowns."),
    happening("Voting in the United States", "This is voting in an election in the USA."),
    happening("Polling stations in the United States", "This is a polling place in the USA, where people vote."),
    happening("Voting booths", "These are voting booths, where people mark their ballots in private.", 0),
]
# Graduations of schoolchildren (adults only, the owner's rule).
SCHOOL_GRADUATION = re.compile(r"\b(high school|elementary|middle school|junior high|kindergarten|preschool|"
                               r"pre-k|grade school|eighth grade)\b", re.I)


def adult_graduations(items):
    """Drop graduation photos of schoolchildren: those filed under school graduations or whose words name a
    child."""
    kept = []
    for name, url, rows in items:
        category = json.dumps(rows[0].get("facts", {}))
        child = any(r.get("child") for r in rows)
        if re.search(r"graduat", category, re.I) and (SCHOOL_GRADUATION.search(category) or child):
            considered(name, url, "a school graduation or a child (graduations are adults only)")
            continue
        kept.append((name, url, rows))
    return kept


# Military holiday photos (US forces' Thanksgiving meals and Turkey Bowls, often on bases abroad, the place unsaid).
MILITARY = re.compile(r"\b(U\.?S\.? (Navy|Army|Air Force|Marines?|Marine Corps|Coast Guard)|service ?members?|"
                      r"airmen|sailors|soldiers|marines|expeditionary|squadron|battalion|brigade|regiment|"
                      r"\d+(st|nd|rd|th) [A-Z]\w+ (Wing|Division|Group)|dining facility|base|camp \w+|"
                      r"(Petty Officer|Sgt\.|Lance Cpl\.|Pfc\.|Capt\.|Lt\.)|DVIDS|Defense\.gov)\b")


def everyday_holidays(items):
    """Adult graduations only (adult_graduations), and no official speeches (OFFICIAL) or military holiday events
    (MILITARY): the pack is about everyday civilian holidays."""
    items = drop_items(items, OFFICIAL, "an official event or speech, not an everyday holiday")
    items = drop_items(items, MILITARY, "a military holiday event (often on a base abroad, the place not said)")
    return adult_graduations(items)


def build_commons_us_holidays(limit):
    """The Commons American holidays, events and seasons pack."""
    return commons_specs_pack(HOLIDAYS, limit, "usholiday", after=everyday_holidays)


# ----------------------------------------------------------------- commons_us_eating_out

def place_kind(category, answer, depth=1, place=USA):
    """A spec asking "What kind of place is this?"."""
    return us_spec(category, PLACE_Q, answer, place, depth)


EATING_OUT = [
    place_kind("Diners in the United States", "This is an American diner: booths, a counter with stools, and "
                                              "breakfast all day."),
    place_kind("Diners", "This is a diner.", 1, ""),
    place_kind("Fast food restaurants in the United States", "This is a fast-food restaurant in the USA: order at "
                                                             "the counter, a kiosk or the drive-through."),
    place_kind("Interiors of fast food restaurants", "This is the inside of a fast-food restaurant: an ordering "
                                                     "counter with menu boards above it, and tables.", 1, ""),
    place_kind("Interiors of McDonald's restaurants", "This is the inside of a McDonald's fast-food restaurant.", 1,
               ""),
    place_kind("Food trucks in the United States", "This is a food truck in the USA: food cooked and sold from a "
                                                   "window in the side of a truck."),
    place_kind("Food trucks in New York City", "This is a food truck in New York City.", 1,
               "New York City, New York, USA"),
    place_kind("Barbecue restaurants in the United States", "This is a barbecue restaurant in the USA, serving "
                                                            "smoked meats such as brisket, ribs and pulled pork."),
    us_spec("Barbecue in the United States", WHAT_Q, "This is American barbecue: meat slow-cooked over smoke.", USA,
            1),
    place_kind("Coffee shops in the United States", "This is a coffee shop in the USA."),
    place_kind("Pizzerias in the United States", "This is a pizzeria (a pizza restaurant) in the USA."),
    place_kind("Hot dog stands in the United States", "This is a hot-dog stand in the USA."),
    place_kind("Delicatessens in the United States", "This is a delicatessen (deli) in the USA: sandwiches, meats "
                                                     "and cheeses made to order."),
    place_kind("Bakeries in the United States", "This is a bakery in the USA."),
    place_kind("Ice cream parlors in the United States", "This is an ice-cream parlor in the USA."),
    place_kind("Convenience stores in the United States", "This is a convenience store in the USA: snacks, drinks "
                                                          "and everyday things, often open late."),
    place_kind("Food courts in the United States", "This is a food court in the USA: counters of several "
                                                   "restaurants around shared tables."),
    place_kind("Supermarket aisles", "This is a supermarket aisle, with shelves of products on both sides.", 1, ""),
]


def build_commons_us_eating_out(limit):
    """The Commons eating out and food shopping pack."""
    return commons_specs_pack(EATING_OUT, limit, "useat")


# ----------------------------------------------------------------- commons_us_getting_around

GETTING_AROUND = [
    place_kind("New York City Subway", "This is the New York City Subway.", 1, "New York City, New York, USA"),
    place_kind("Chicago 'L' stations", "This is a station of the Chicago 'L', Chicago's elevated and subway "
                                       "trains.", 1, "Chicago, Illinois, USA"),
    place_kind("Washington Metro stations", "This is a Washington Metro station, the subway of Washington, D.C.", 1,
               "Washington, D.C., USA"),
    place_kind("BART stations", "This is a BART station, the San Francisco Bay Area's rapid-transit trains.", 1,
               "San Francisco Bay Area, California, USA"),
    place_kind("SEPTA stations", "This is a SEPTA station, Philadelphia's public transit.", 1,
               "Philadelphia, Pennsylvania, USA"),
    place_kind("Amtrak stations in the United States", "This is an Amtrak station, where long-distance passenger "
                                                       "trains stop."),
    place_kind("Union Station (Washington, D.C.)", "This is Union Station in Washington, D.C., a big train station.",
               1, "Washington, D.C., USA"),
    place_kind("Bus stops in the United States", "This is a bus stop in the USA."),
    place_kind("Bus stops in New York City", "This is a bus stop in New York City.", 1, "New York City, New York, USA"),
    place_kind("Bus shelters in the United States", "This is a bus shelter in the USA."),
    place_kind("Light rail in the United States", "This is light rail in the USA: trams or light trains in the "
                                                  "street or on their own track."),
    place_kind("Airport terminals in the United States", "This is an airport terminal in the USA."),
    place_kind("Interiors of airports in the United States", "This is the inside of an airport in the USA."),
    place_kind("Transportation Security Administration", "This is airport security in the USA (the TSA): "
                                                         "travellers and their bags are screened before the "
                                                         "gates."),
    place_kind("Airport security", "This is airport security: screening of travellers and bags.", 1, ""),
    place_kind("Parking garages in the United States", "This is a parking garage in the USA."),
    place_kind("Gas stations in the United States", "This is a gas station in the USA, where cars fill up with "
                                                    "fuel."),
    us_spec("Fuel pumps", WHAT_Q, "This is a fuel pump (gas pump).", "", 1),
    place_kind("Electric vehicle charging stations in the United States", "This is a charging station for electric "
                                                                          "cars in the USA."),
]


def build_commons_us_getting_around(limit):
    """The Commons getting around pack."""
    return commons_specs_pack(GETTING_AROUND, limit, "usgo")


# ----------------------------------------------------------------- commons_us_public_places

PUBLIC_PLACES = [
    place_kind("Post offices in the United States", "This is a US post office."),
    place_kind("Interiors of post offices in the United States", "This is the inside of a US post office, with the "
                                                                 "counter and PO boxes."),
    place_kind("Department of Motor Vehicles", "This is a Department of Motor Vehicles (DMV) office, where people "
                                               "get driving licences and register cars."),
    place_kind("Bank branches in the United States", "This is a bank branch in the USA."),
    place_kind("Pharmacies in the United States", "This is a pharmacy in the USA."),
    place_kind("Drugstores in the United States", "This is a drugstore in the USA: a pharmacy counter and aisles of "
                                                  "health products and everyday things."),
    place_kind("Laundromats in the United States", "This is a laundromat in the USA: coin- or card-operated washers "
                                                   "and dryers for anyone to use."),
    place_kind("Gyms", "This is a gym, with exercise machines and weights.", 1, ""),
    place_kind("Hospital rooms", "This is a hospital room.", 1, ""),
    place_kind("Hospital corridors", "This is a hospital corridor.", 1, ""),
    place_kind("Interiors of hospitals in the United States", "This is the inside of a hospital in the USA."),
    place_kind("Waiting rooms in the United States", "This is a waiting room in the USA."),
    place_kind("Interiors of libraries in the United States", "This is the inside of a library in the USA."),
    place_kind("Public libraries in the United States", "This is a public library in the USA."),
    place_kind("Offices in the United States", "This is an office in the USA."),
    place_kind("Interiors of churches in the United States", "This is the inside of a church in the USA."),
    place_kind("Interiors of stadiums in the United States", "This is the inside of a stadium in the USA."),
    place_kind("Interiors of shopping malls in the United States", "This is the inside of a shopping mall in the "
                                                                   "USA."),
    place_kind("Courthouses in the United States", "This is a courthouse in the USA."),
    place_kind("City halls in the United States", "This is a city hall in the USA."),
    place_kind("Fire stations in the United States", "This is a fire station in the USA."),
    place_kind("Hotel lobbies in the United States", "This is a hotel lobby in the USA."),
    place_kind("Motels in the United States", "This is a motel in the USA: rooms whose doors open onto the parking "
                                              "lot."),
    place_kind("Hardware stores in the United States", "This is a hardware store in the USA."),
    place_kind("Department stores in the United States", "This is a department store in the USA."),
    place_kind("Escalators in the United States", "This is an escalator in the USA."),
    place_kind("Elevators in the United States", "This is an elevator (lift) in the USA."),
]
# Hospital photos with a patient, an operation or an injury: left out (no identifiable patients).
PATIENT = re.compile(r"\b(patients?|surgery|surgical|operating (room|theatre)|operation|wounds?|injur\w*|"
                     r"bed-?ridden|intensive care|icu|newborns?|maternity|birth)\b", re.I)


def no_patients(items):
    """Drop hospital photos whose words name a patient, surgery or an injury."""
    def hospital(item):
        """True for a photo found in a hospital category."""
        return bool(re.search(r"hospital", json.dumps(item[2][0].get("facts", {})), re.I))
    kept = {i[0] for i in drop_items([i for i in items if hospital(i)], PATIENT, "a hospital photo whose words name "
                                                                             "a patient, surgery or an injury")}
    return [i for i in items if not hospital(i) or i[0] in kept]


def build_commons_us_public_places(limit):
    """The Commons public places and services pack."""
    return commons_specs_pack(PUBLIC_PLACES, limit, "uspublic", after=no_patients)


# ----------------------------------------------------------------- us_federal_forms

IRS = "https://www.irs.gov/pub/irs-pdf/"
IRS_AGENCY = "the Department of the Treasury, Internal Revenue Service (IRS)"
# (PDF address, agency, the form's name when the PDF's own title does not give it)
FORMS = [(IRS + f + ".pdf", IRS_AGENCY, "") for f in (
    "fw4", "fw9", "fw4p", "fw4v", "fw7", "f1040", "f1040sr", "f1040x", "f1040es", "f1040v", "f1040s1", "f1040s2",
    "f1040s3", "f1040sa", "f1040sb", "f1040sc", "f1040sd", "f1040se", "f1040sse", "f1040s8", "f1099nec",
    "f1099int", "f1099div", "f1099g", "f1099r", "f1099k", "f1099msc", "f1098", "f1098e", "f1098t", "f1095a",
    "f1095b", "f1095c", "f8962", "f9465", "f4506t", "f4506c", "f8822", "fss4", "f8888", "f8379", "f2848", "f8821",
    "f4868", "f8863", "f8880", "f5695", "f8949", "f2441", "f8606", "f14039", "f911", "f843", "f1310", "f56",
    "fw2", "fw3", "f941", "f940", "fw4s", "f1040sh", "f8995", "f8867", "f1099s", "f1099b", "f1099c", "f8936")] + [
    ("https://www.cms.gov/medicare/cms-forms/cms-forms/downloads/cms1490s-english.pdf",
     "the Centers for Medicare & Medicaid Services (CMS)", "Form CMS-1490S, Patient's Request for Medical Payment "
                                                           "(Medicare)"),
    ("https://www.opm.gov/forms/pdf_fill/sf2809.pdf", "the US Office of Personnel Management (OPM)",
     "Standard Form 2809, Health Benefits Election Form"),
    ("https://www.vba.va.gov/pubs/forms/VBA-21-526EZ-ARE.pdf", "the US Department of Veterans Affairs (VA)",
     "VA Form 21-526EZ, Application for Disability Compensation and Related Compensation Benefits"),
    ("https://www.eeoc.gov/sites/default/files/2023-06/22-088_EEOC_KnowYourRights6.12ScreenRdr.pdf",
     "the US Equal Employment Opportunity Commission (EEOC)", "the EEOC poster \"Know Your Rights: Workplace "
                                                               "Discrimination is Illegal\""),
]
FORM_CREDITS = {IRS: "Internal Revenue Service, US Department of the Treasury, https://www.irs.gov (\"Content on "
                     "this website that was created or maintained by federal employees in the course of their duties "
                     "is not subject to copyright and may be freely copied.\")"}
PAGES_PER_FORM = 3
PAGE_SIDE = 1700


def form_name(title, subject, fallback):
    """The form's name from its PDF's own title and subject: ("2026 Form W-4", "Employee's Withholding
    Certificate") -> "IRS Form W-4 for 2026, Employee's Withholding Certificate"; ("Form 1099-NEC (Rev. December
    2026)", "Nonemployee Compensation") -> "IRS Form 1099-NEC, Nonemployee Compensation"; the fallback when the
    title does not name a form."""
    title, subject = clean(title), clean(subject)
    m = re.match(r"^(?:(?P<year>(?:19|20)\d\d)\s+)?(?P<kind>Form|Schedule)\s+(?P<number>[\w-]+(?:\s*\(Form [\w-]+\))?)"
                 r"(?P<rest>.*)$", title)
    if not m:
        return fallback
    name = f"IRS {m.group('kind')} {m.group('number')}"
    if m.group("year"):
        name += f" for {m.group('year')}"
    words = subject or re.sub(r"\(Rev\.[^)]*\)", "", m.group("rest")).strip(" -,:")
    return f"{name}, {words}" if words else name


COVER_SHEET = re.compile(r"^(Attention|Caution)\b", re.I)


def top_words(text, most=25):
    """The words printed at the top of a page, as one tidy sentence-like line: the first lines of text (each
    stripped), joined with " ", at most about most words; "" when fewer than three words."""
    lines = [clean(x) for x in re.split(r"[\r\n]+", text or "") if clean(x)]
    out = []
    for line in lines:
        if len(" ".join(out + [line]).split()) > most:
            break
        out.append(line)
    words = " ".join(out)
    return words if len(words.split()) >= 3 else ""


def form_pages(data, url, agency, fallback):
    """[(file name, JPEG bytes, rows)] for the first pages of one blank form PDF (pypdfium2): page 1 with "What is
    this form?", "What does it say at the top?" and "Is this form filled in?"; later pages with "What is this?" and
    the words at their top."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(data)
    meta = doc.get_metadata_dict()
    name = form_name(meta.get("Title"), meta.get("Subject"), fallback)
    if not name:
        considered(url, url, "the PDF's title names no form, and none is known for it")
        return []
    base = re.sub(r"\W+", "_", url.rsplit("/", 1)[-1].rsplit(".", 1)[0])[:60]
    credit = (f"{name}, {agency}, {url}; "
              + FORM_CREDITS.get(IRS if url.startswith(IRS) else "", "a US government work, not subject to "
                                                                     "copyright (17 U.S.C. 105)"))
    out = []
    pages = len(doc)
    first = None
    for n in range(pages):
        if len(out) >= PAGES_PER_FORM:
            break
        page = doc[n]
        w, h = page.get_size()
        raw = page.get_textpage().get_text_bounded(left=0, bottom=h * 0.85, right=w, top=h)
        top = top_words(raw)
        if COVER_SHEET.match(clean(raw)):      # the IRS "Attention:" sheet in front of every 1099 (the same page)
            continue
        bitmap = page.render(scale=PAGE_SIDE / max(w, h)).to_pil().convert("RGB")
        jpeg = io.BytesIO()
        bitmap.save(jpeg, "JPEG", quality=88)
        where = {"place": USA, "place_kind": "origin"}
        if first is None:
            first = n
            rows = [{"question": FORM_Q, "answer": f"This is {name}, from {agency}." + (
                f" It has {pages} pages." if pages > 1 else ""), "credit": credit, **where,
                     "facts": {"pdf_title": clean(meta.get("Title")), "pages": pages}},
                    {"question": FILLED_Q, "answer": "No: it is a blank form, with empty boxes and lines to fill in.",
                     "credit": credit, **where}]
        else:
            rows = [{"question": WHAT_Q, "answer": f"This is page {n + 1} of {pages} of {name}.", "credit": credit,
                     **where}]
        if top:
            rows.append({"question": TOP_Q, "answer": f"At the top it says: {top}", "credit": credit, **where})
        out.append((f"form-{base}-p{n + 1}.jpg", jpeg.getvalue(), rows))
    doc.close()
    return out


def build_us_federal_forms(limit):
    """The blank US government forms pack: each form's PDF from the agency's own site (gently, one at a time), its
    first pages drawn as pictures."""
    s, out, seen = session(), [], set()
    forms = list(FORMS)
    pass_random("forms").shuffle(forms)
    for url, agency, fallback in forms:
        if len(out) >= limit or listing_out_of_time():
            break
        try:
            r = s.get(url, timeout=90)
        except Exception as e:  # noqa: BLE001 - that form is left out
            considered(url, url, f"could not be downloaded ({type(e).__name__})")
            continue
        if r.status_code != 200 or not r.content.startswith(b"%PDF"):
            considered(url, url, f"could not be downloaded (the server answered {r.status_code})")
            continue
        try:
            for name, data, rows in form_pages(r.content, url, agency, fallback):
                mark = build_packs.fingerprint(data)
                if mark in seen:              # the same page in two forms (shared instruction pages): once
                    continue
                seen.add(mark)
                out.append((name, data, rows))
        except Exception as e:  # noqa: BLE001 - a PDF that cannot be read is left out
            considered(url, url, f"the PDF could not be read ({type(e).__name__})")
        time.sleep(1.5)
    say(f"us_federal_forms: {len(out)} pages")
    return with_twins(out[:limit])


# ----------------------------------------------------------------- imageinwords

IIW_DATA = "https://raw.githubusercontent.com/google/imageinwords/main/datasets/"
IIW_SETS = {"IIW-400": "https://storage.googleapis.com/docci/data/images_aar/{key}.jpg",
            "DOCCI_Test": "https://storage.googleapis.com/docci/thumbnails/{key}.jpg"}
IIW_CREDIT = ("ImageInWords (Garg et al., Google, 2024), human-authored description, CC BY 4.0, "
              "https://google.github.io/imageinwords/; photo from DOCCI (Onoe et al., Google, 2024), CC BY 4.0, "
              "https://google.github.io/docci/ ({key})")


def iiw_rows(record):
    """The rows of one ImageInWords record: the person's detailed description ("IIW", never the machine-written
    "IIW-P5B") and, where given, up to three objects' descriptions; [] when there is no human description."""
    text = clean(record.get("IIW"))
    if len(text.split()) < 20 or NUDE.search(text):
        return []
    key = record.get("image/key") or record.get("image") or ""
    credit = IIW_CREDIT.format(key=key)
    rows = [{"question": DETAILED, "answer": text, "credit": credit}]
    for obj in (record.get("objects") or [])[:3]:
        label, words = clean(obj.get("label")), clean(obj.get("description"))
        if label and len(words.split()) >= 5 and not NUDE.search(words):
            rows.append({"question": f"Describe the {label[:1].lower() + label[1:]} in this picture.",
                         "answer": sentence(words), "credit": credit})
    return [mark_child(r, text) for r in rows]


def build_imageinwords(limit):
    """The ImageInWords pack: the IIW-400 and DOCCI_Test records' human descriptions with their DOCCI photos."""
    s, items = session(), []
    for name, picture in IIW_SETS.items():
        r = s.get(IIW_DATA + name + "/data.jsonl", timeout=120)
        r.raise_for_status()
        for line in r.text.splitlines():
            record = json.loads(line) if line.strip() else {}
            key = record.get("image/key") or record.get("image")
            rows = iiw_rows(record)
            if key and rows:
                items.append((f"iiw-{key}.jpg", picture.format(key=key), rows))
    pass_random("imageinwords").shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.05) + 2], workers=4)[:limit]
    say(f"imageinwords: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
US_MODERN_PACKS = {
    "commons_us_agencies": (build_commons_us_agencies, COMMONS_CREDIT.format(
        what="copies of US federal agencies' photo streams (USDA, FEMA, HUD and the Forest Service): public domain "
             "as US government works; captions by the agencies")),
    "commons_us_controls": (build_commons_us_controls, COMMONS_CREDIT.format(
        what="categories of appliances, machines and controls (dishwashers, dryers, ovens, remote controls, "
             "self-checkouts, card readers, vending machines, US pedestrian signals and push buttons ...)")),
    "commons_us_holidays": (build_commons_us_holidays, COMMONS_CREDIT.format(
        what="categories of American holidays and events (Thanksgiving, Halloween, the Fourth of July, fairs, "
             "parades, farmers markets, graduations, voting)")),
    "commons_us_eating_out": (build_commons_us_eating_out, COMMONS_CREDIT.format(
        what="categories of American diners, fast-food restaurants, food trucks, coffee shops and food shops")),
    "commons_us_getting_around": (build_commons_us_getting_around, COMMONS_CREDIT.format(
        what="categories of US subway, train and bus stations, airports, parking, gas and charging stations")),
    "commons_us_public_places": (build_commons_us_public_places, COMMONS_CREDIT.format(
        what="categories of US post offices, the DMV, banks, pharmacies, laundromats, gyms, hospitals, libraries, "
             "offices and other public places")),
    "us_federal_forms": (build_us_federal_forms,
                         "Blank US government forms drawn from the agencies' own PDFs (IRS, CMS, OPM, VA, EEOC): US "
                         "government works, not subject to copyright (17 U.S.C. 105). IRS: \"Content on this website "
                         "that was created or maintained by federal employees in the course of their duties is not "
                         "subject to copyright and may be freely copied.\" "
                         "(https://www.irs.gov/about-irs/use-of-content-from-irsgov)"),
    "imageinwords": (build_imageinwords,
                     "ImageInWords (Garg et al., Google, 2024), human-authored descriptions, CC BY 4.0 "
                     "(https://google.github.io/imageinwords/); photos from DOCCI (Google), CC BY 4.0 "
                     "(https://google.github.io/docci/)."),
}

# How many pictures a full build takes from each (each finishes well within about four hours on GitHub's machines).
US_MODERN_LIMITS = {
    "commons_us_agencies": 4000,        # 6 agency categories (USDA's Flickr copy alone has 76,000 files), sampled
    "commons_us_controls": 2000,        # 26 categories, most of them 50 to 500 files
    "commons_us_holidays": 2500,        # 20 categories and their subcategories
    "commons_us_eating_out": 2500,      # 18 categories and their subcategories
    "commons_us_getting_around": 3000,  # 19 categories (station categories have one subcategory per station)
    "commons_us_public_places": 3000,   # 27 categories and their subcategories
    "us_federal_forms": 200,            # 71 forms, up to 3 pages each (about 170 pages come)
    "imageinwords": 500,                # 400 + 100 records with a human description
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one modern-America pack builder.")
    parser.add_argument("key", choices=sorted(US_MODERN_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = US_MODERN_PACKS[args.key][0](args.limit)
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
