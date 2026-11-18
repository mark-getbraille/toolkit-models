"""Pack builders for CANADA: the Canadian equivalents of the United States packs (packs/us_packs.py and
packs/us_modern_packs.py). Canadian houses outside and inside, streets and what people on them wear, cars, wild
plants and animals by province and territory, Canadian money, Canadian road signs (bilingual ones too), shops and
packaged goods, Canadian holidays (Canada Day, Victoria Day, Thanksgiving in October, Remembrance Day, the Fête
nationale du Québec), eating out (coffee and doughnut shops, poutine, dépanneurs), getting around (the TTC, the
Montreal Metro, TransLink, GO Transit, VIA Rail, Canadian airports), public places (post offices, Service Canada,
pharmacies) and old photographs kept by Canadian archives (Library and Archives Canada, the City of Toronto
Archives, BAnQ) and Government of Canada photos under the Open Government Licence - Canada.

Used by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)], where a row is {"question", "answer", "credit"}, plus "place" ("Halifax,
Nova Scotia, Canada"; "place_kind" when the place is not where the photo was taken), "child": true where the words
of a picture name a child, "content": "graphic" where they name the dead or injured, and "facts" where the source
gives more than the answer says. A picture with more than one question comes once with its JPEG and then again as
(None, None, row) rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Every answer is a fixed sentence written here from the source's own records: the name of the Commons category a
photo sits in, the photo's own caption (for the archive photos, the caption the archive wrote), a road-sign drawing's
own description, an iNaturalist community identification. Nothing is written by an AI model, nobody is named, and
nothing is guessed about who a person is. Places come from the records only (the province or city a category names,
an iNaturalist observation's province, a caption that names a province, or a Commons photo's camera coordinates).
Bilingual signs and labels: the answer is in English; where a sign says it is in English and French, the answer says
so.

Safety (packs/SOURCE-RULES.md): no sexual content (us_packs.NOT_SHOWN: nudity, underwear, swimwear, and also
crime-scene and evidence photos and mugshots); children only in everyday clothed scenes, and every row whose words
name a child is marked "child"; graduations are adults only; hospital photos whose words name a patient are left
out; archive photos whose words name the dead or injured are marked "content": "graphic". The packs that show people
are never used for picture-making (wire them into the kit's PEOPLE_AND_BODILY_PACK_KEYS): commons_ca_streets,
commons_ca_cars, commons_ca_shops, commons_ca_holidays, commons_ca_eating_out, commons_ca_getting_around,
commons_ca_public_places, commons_ca_archives, commons_ca_provincial and commons_ca_daily_life. Indigenous life:
sacred and ceremonial scenes (powwows, regalia, smudging, sweat lodges, potlatches, prayers, burials) are left out
(SACRED), because no source used here says they may be shared; no Indigenous community's own archive with an open
licence was found (see canada_sources.CANADA_NOT_INCLUDED).

The packs (all open; checked at the source in November 2026):
  commons_ca_homes         Wikimedia Commons: "Houses in <province or territory>" for all 13, Canadian house kinds
                           (farmhouses, log houses, cottages, bungalows, row and semi-detached houses, sod houses,
                           stone and brick houses, Arts and Crafts and Carpenter Gothic houses, cabins, igloos) and
                           Canadian rooms (kitchens, living rooms, bedrooms, bathrooms, dining rooms). The US pack's
                           Historic American Buildings Survey has no open Canadian twin (see canada_sources.py).
  commons_ca_streets       Commons: "Streets in <city>" for 18 Canadian cities (the city as the place), pedestrians
                           and street photography in Canada, with "What is the person wearing?" from the clothing
                           categories a photo sits in.
  commons_ca_cars          Commons: "Automobiles in <province>" for the ten provinces, Toronto and Montreal; the model
                           from the model category each photo sits in, the colour from its colour category.
  inaturalist_ca           iNaturalist research-grade observations in each province and territory (photos CC0 or
                           CC BY, each photographer credited; https://www.inaturalist.org/pages/terms).
  commons_ca_money         Commons: Canadian banknotes by face value and coins by denomination. Commons keeps only
                           the files it may (Commons:Currency says the Bank of Canada owns the design of Canadian
                           notes and the Royal Canadian Mint its coins, so modern ones are not there: what is there is
                           mostly old Crown-copyright-expired money and photos whose own licence is free); each
                           file's own licence is checked (CC0, public domain or CC BY).
  ca_road_signs            Commons: drawings of Canadian road signs (Category:Diagrams of road signs of Canada, its
                           provinces and the Manual of Uniform Traffic Control Devices for Canada categories), each
                           with its sign number when its file name gives one and its meaning from its own English
                           description, set black on white; and photos of Canadian stop signs (STOP / ARRÊT), speed
                           limit signs (km/h), pedestrian and school signs, and bilingual signs.
  commons_ca_shops         Commons: Canadian supermarkets and grocery stores, dépanneurs and convenience stores, and
                           the big Canadian chains' shops (Sobeys, Loblaws, Canadian Tire). "What kind of place is
                           this?" (Packaging itself is not Canadian: the commons_packaging pack covers it.)
  commons_ca_holidays      Commons: Canada Day, Victoria Day, Thanksgiving (October), Remembrance Day, the Fête
                           nationale du Québec, Christmas and Christmas lights, Easter and Halloween in Canada,
                           Winterlude, the Calgary Stampede, the Carnaval de Québec, farmers' markets, parades,
                           fireworks, polling stations, curling, snow clearing and snowbanks. "What is happening
                           here?"
  commons_ca_eating_out    Commons: Tim Hortons shops, poutine, Canadian restaurants, coffee shops, fast-food
                           restaurants, food trucks, diners, bakeries, pizzerias, ice-cream parlours, food courts and
                           dépanneurs. "What kind of place is this?"
  commons_ca_getting_around Commons: the Toronto subway and TTC, the Montreal Metro and STM, TransLink (Vancouver),
                           GO Transit, VIA Rail stations, Calgary's CTrain and Ottawa's O-Train, buses and bus stops,
                           the Presto fare card, Toronto Pearson, Vancouver and Montréal-Trudeau airports, gas and
                           charging stations, BC Ferries, parking meters and pedestrian signals.
  commons_ca_public_places Commons: post offices, Service Canada and ServiceOntario offices,
                           pharmacies (Shoppers Drug Mart, Jean Coutu, Rexall, Uniprix), libraries, hospitals (no
                           patients), city halls, courthouses, fire stations, shopping malls, banks, laundromats,
                           hardware and department stores, church insides, hotels and vending machines.
  commons_ca_archives      Commons copies of Canadian archives' photographs: Library and Archives Canada (its own
                           Commons uploads and its Flickr stream), the City of Toronto Archives, the Toronto Public
                           Library and Bibliothèque et Archives nationales du Québec (BAnQ), and Government of Canada
                           photos under the Open Government Licence - Canada (Commons Category:OGL-C: "This file is
                           licensed under the Open Government Licence - Canada 2.0."). Most archive photos are public
                           domain in Canada (Crown copyright expired, or photos taken before 1949); each file's own
                           licence is checked (public domain, CC0, CC BY or OGL-Canada). "Describe this picture." with
                           the archive's caption (catalogue numbers taken out), "Where is this photo kept?". A free
                           photo whose caption is under six English words (BAnQ's are in French) is set aside for a
                           description (build_packs.needs_description). Library and Archives Canada's own search
                           (recherche-collection-search.bac-lac.gc.ca) refused this machine (403), so its photos come
                           from these Commons copies, as the US agencies' do.
  commons_ca_provincial    Commons files under a province's or territory's Open Government Licence (templates OGL-ON,
                           OGL-Alberta, OGL-BC, OGL-NB, OGL-YT: "You are free to: Copy, modify, publish, translate,
                           adapt, distribute or otherwise use the Information in any medium, mode or format for any
                           lawful purpose", with the attribution "Contains information licensed under the Open
                           Government Licence - Ontario" and so on; checked at ontario.ca, open.alberta.ca, gov.bc.ca
                           and the Commons templates for New Brunswick and Yukon). Nearly all are the Archives of
                           Ontario's own upload (its GLAM Wiki project, 1920s to 1960s Ontario life: farms, cottages,
                           tourist camps, fairs), whose titles are their captions. Ontario's open-data record of the
                           same archive says "the actual images are not published under the Open Government
                           Licence"; the Commons files are the ones the Archives itself released under OGL-ON. The
                           province is the place. Medical scenes (patients) are left out.
  commons_ca_daily_life    Commons: everyday life in Canada, 1990 onwards: winter and snow in Canada, Toronto and
                           Montreal, snow shovels, the Rideau Canal Skateway, ice skating, pond hockey and hockey in
                           Ontario, ice fishing, tobogganing, canoeing, camping, picnics, cycling, commuters, people in
                           Toronto, markets and festivals. (people_activity_packs.commons_daily_life takes no Canadian
                           category; work in Canada is work_farm_mech_packs'.)

The share-alike, non-commercial and research collections on the same subjects (Commons BY-SA files, Open Food,
Beauty and Products Facts sold in Canada, iNaturalist BY-SA and BY-NC photos in Canada, Health Canada recall photos,
blank CRA forms, the City of Montréal's archive photos), the sign-up collections, the ones looked at and left out and
the owners to ask for permission are in training-kit/kit/canada_sources.py.

    python packs/canada_packs.py commons_ca_homes --limit 8      (prints a few rows: a quick check)
"""

import collections
import io
import json
import math
import re
import sys
import time
import unicodedata

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, fetch_all, needs_description
from build_packs import INAT_GROUPS, article, pass_random
from food_packs import with_twins, count_pictures, commons_get, commons_members
from home_packs import commons_fetch, file_name, symbol_picture, NUDE, NOT_RESPECTFUL
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import mech_entries, in_english, MECH_FREE, NOT_A_PHOTO
from us_packs import (us_spec, us_commons, commons_pack, wearing_rows, car_rows, NOT_SHOWN, DESCRIBE_Q, WHAT_Q,
                      HOUSE_Q, ROOM_Q, PLACE_Q, WEAR_Q, CAR_Q, MONEY_Q, SIGN_Q, QUOTED)
from us_modern_packs import (commons_specs_pack, drop_items, sample_members, photo_year, agency_caption, only_the_name,
                             everyday_holidays, no_patients, GRAPHIC, HAPPENING_Q)
from places import where, place_name

CANADA = "Canada"
KEPT_Q = "Where is this photo kept?"
# The provinces and territories, with the name Commons and iNaturalist use when it differs ("Québec").
PROVINCES = ["Ontario", "Quebec", "British Columbia", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia",
             "New Brunswick", "Prince Edward Island", "Newfoundland and Labrador"]
TERRITORIES = ["Yukon", "Northwest Territories", "Nunavut"]
# A province or territory named in a caption ("Halifax, N.S.", "Moose Jaw, Sask."), as its full name.
PROVINCE_WORDS = [(r"\bOntario\b|\bOnt\.", "Ontario"), (r"\bQu[ée]bec\b|\bQue\.|\bP\.Q\.", "Quebec"),
                  (r"\bBritish Columbia\b|\bB\.C\.", "British Columbia"), (r"\bAlberta\b|\bAlta\.", "Alberta"),
                  (r"\bManitoba\b|\bMan\.", "Manitoba"), (r"\bSaskatchewan\b|\bSask\.", "Saskatchewan"),
                  (r"\bNova Scotia\b|\bN\.S\.", "Nova Scotia"), (r"\bNew Brunswick\b|\bN\.B\.", "New Brunswick"),
                  (r"\bPrince Edward Island\b|\bP\.E\.I\.", "Prince Edward Island"),
                  (r"\bNewfoundland\b|\bLabrador\b|\bNfld\.", "Newfoundland and Labrador"),
                  (r"\bYukon\b", "Yukon"), (r"\bNorthwest Territories\b|\bN\.W\.T\.", "Northwest Territories"),
                  (r"\bNunavut\b", "Nunavut")]


def ca(spec_place):
    """A place in Canada: "Ontario" -> "Ontario, Canada"; "" -> "Canada"."""
    return place_name(spec_place, CANADA) if spec_place else CANADA


def province_in(text):
    """The province or territory a caption names ("Halifax, N.S." -> "Nova Scotia"), or "" (none, or more than
    one)."""
    found = {name for pattern, name in PROVINCE_WORDS if re.search(pattern, text or "")}
    return found.pop() if len(found) == 1 else ""


def folded(text):
    """Text without accents, in lower case ("Québec" -> "quebec"), to compare names."""
    return "".join(c for c in unicodedata.normalize("NFD", text or "") if unicodedata.category(c) != "Mn").lower()


# ----------------------------------------------------------------- commons_ca_homes

HOUSE_KINDS = [
    ("Farmhouses in Canada", "It is a farmhouse."),
    ("Log houses in Canada", "It is a log house, built of logs."),
    ("Cabins in Canada", "It is a cabin, a small simple house, often in the country or the woods."),
    ("Cottages in Canada", "It is a cottage."),
    ("Bungalows in Canada", "It is a bungalow, a house of one storey."),
    ("Row houses in Canada", "It is a row house, joined to the houses on each side."),
    ("Semi-detached houses in Canada", "It is a semi-detached house: two homes side by side sharing one wall."),
    ("Sod houses of Canada", "It is a sod house, built of blocks of turf, as settlers built them on the prairies."),
    ("Stone houses in Canada", "It is a stone house."),
    ("Brick houses in Canada", "It is a brick house."),
    ("Arts and Crafts houses in Canada", "It is an Arts and Crafts house, with plain hand-made details, low roofs "
                                         "and wide porches."),
    ("Carpenter Gothic houses in Canada", "It is a Carpenter Gothic house: a wooden house with steep pointed gables "
                                          "and lacy carved trim."),
    ("Igloos", "It is an igloo, a dome-shaped shelter built of blocks of snow, as Inuit build them in the Arctic."),
]
ROOMS = [("Kitchens in Canada", "This is a kitchen."), ("Living rooms in Canada", "This is a living room."),
         ("Bedrooms in Canada", "This is a bedroom."), ("Bathrooms in Canada", "This is a bathroom."),
         ("Dining rooms in Canada", "This is a dining room."), ("Interiors of houses in Canada", None)]


def home_specs():
    """The commons_ca_homes categories: houses in each province and territory (and the three biggest cities), house
    kinds and rooms."""
    specs = [us_spec(f"Houses in {p}" if p != "Northwest Territories" else "Houses in the Northwest Territories",
                     WHAT_Q, f"This is a house in {p}, Canada.", ca(p), 1) for p in PROVINCES + TERRITORIES]
    specs += [us_spec(f"Houses in {city}", WHAT_Q, f"This is a house in {city}, {prov}, Canada.",
                      place_name(city, prov, CANADA), 1)
              for city, prov in (("Toronto", "Ontario"), ("Montreal", "Quebec"), ("Vancouver", "British Columbia"))]
    specs += [us_spec(c, HOUSE_Q, a, "" if c == "Igloos" else CANADA, 1) for c, a in HOUSE_KINDS]
    specs += [us_spec(c, ROOM_Q, a, CANADA, 1) for c, a in ROOMS]
    return specs


# Subcategories of the room and house categories that are about vehicles ("Dining cars of Canada" sits under
# "Dining rooms in Canada"): their photos are left out.
NOT_A_HOME = re.compile(r"\b(dining cars?|sleeping cars?|railway|railroad|trains?|ships?|boats?|ferr(y|ies)|"
                        r"aircraft|yachts?|buses|motorhomes?)\b", re.I)


def build_commons_ca_homes(limit):
    """The Commons Canadian houses and rooms pack (photos found in vehicle subcategories left out)."""
    items = drop_items(us_commons(home_specs(), limit, "cahome"), NOT_A_HOME, "found in a subcategory about "
                                                                             "vehicles, not homes")
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- commons_ca_streets

CITIES = [("Toronto", "Ontario"), ("Montreal", "Quebec"), ("Vancouver", "British Columbia"), ("Calgary", "Alberta"),
          ("Edmonton", "Alberta"), ("Ottawa", "Ontario"), ("Quebec City", "Quebec"),
          ("Halifax, Nova Scotia", "Nova Scotia"), ("Victoria, British Columbia", "British Columbia"),
          ("Hamilton, Ontario", "Ontario"), ("Regina, Saskatchewan", "Saskatchewan"), ("Saskatoon", "Saskatchewan"),
          ("Charlottetown", "Prince Edward Island"), ("London, Ontario", "Ontario"), ("Kitchener, Ontario", "Ontario"),
          ("Gatineau", "Quebec"), ("Sherbrooke", "Quebec"), ("Moncton", "New Brunswick")]
PEOPLE = [("Pedestrians in Canada", CANADA), ("Pedestrians in Toronto", "Toronto, Ontario, Canada"),
          ("Pedestrians in Montreal", "Montreal, Quebec, Canada"), ("Street photography in Canada", CANADA)]


def street_specs():
    """The commons_ca_streets categories: the streets of Canadian cities and people on Canadian streets."""
    specs = []
    for city, prov in CITIES:
        place = place_name(city.split(",")[0], prov, CANADA)
        specs.append(us_spec(f"Streets in {city}", PLACE_Q, f"This is a street in {place}.", place, 1))
    specs += [us_spec(c, WEAR_Q, None, place, 1) for c, place in PEOPLE]
    return specs


def build_commons_ca_streets(limit):
    """The Commons Canadian streets and street fashion pack."""
    return commons_pack(street_specs(), limit, "castreet", extra=wearing_rows)


# ----------------------------------------------------------------- commons_ca_cars

def car_specs():
    """The commons_ca_cars categories: automobiles in each province, Toronto and Montreal."""
    return [us_spec(f"Automobiles in {p}", CAR_Q, None, ca(p), 1) for p in PROVINCES] + \
        [us_spec("Automobiles in Toronto", CAR_Q, None, "Toronto, Ontario, Canada", 1),
         us_spec("Automobiles in Montreal", CAR_Q, None, "Montreal, Quebec, Canada", 1),
         us_spec("Automobiles in Canada", CAR_Q, None, CANADA, 1)]


def build_commons_ca_cars(limit):
    """The Commons Canadian cars pack: only photos whose categories name a model."""
    items = us_commons(car_specs(), int(limit * 1.3) + 4, "cacar", extra=car_rows)
    items = [(n, u, rows) for n, u, rows in items if any(r["question"] == CAR_Q for r in rows)]
    return with_twins(commons_fetch(items)[:limit])


# ----------------------------------------------------------------- inaturalist_ca

INAT = "https://api.inaturalist.org/v1/"
INAT_CANADA = 6712          # iNaturalist's place id of Canada (its provinces are admin level 10 below it)


def inat_provinces(s):
    """{province or territory: iNaturalist place id} for the 13, each looked up by name (one request a second); the
    names are compared without accents, as iNaturalist writes "Québec"."""
    out = {}
    for name in PROVINCES + TERRITORIES:
        if listing_out_of_time():
            break
        try:
            data = s.get(INAT + "places/autocomplete", params={"q": name, "per_page": 20}, timeout=60).json()
        except Exception:  # noqa: BLE001 - that province is left out
            continue
        out.update(inat_match(name, data.get("results") or []))
        time.sleep(1.1)
    return out


def inat_match(name, results):
    """{name: place id} for the iNaturalist place of a province or territory among autocomplete results (admin
    level 10, inside Canada, the same name without accents); {} when none."""
    for p in results:
        if p.get("admin_level") == 10 and INAT_CANADA in (p.get("ancestor_place_ids") or []) \
                and folded(clean(p.get("name"))) == folded(name):
            return {name: p["id"]}
    return {}


def build_inaturalist_ca(limit):
    """iNaturalist research-grade observations in each province and territory whose photo is CC0 or CC BY (credit
    kept): the provinces and the groups of living things take turns, one page of observations each."""
    s, items, seen = session(), [], set()
    provinces = inat_provinces(s)
    say(f"iNaturalist: {len(provinces)} provinces and territories found")
    rng = pass_random(1867)
    pairs = [(prov, group, question) for prov in provinces for group, question in INAT_GROUPS]
    rng.shuffle(pairs)
    per_pair = max(2, math.ceil(limit * 1.15 / max(1, len(pairs))))
    for prov, group, question in pairs:
        if len(items) >= limit * 1.15:
            break
        if listing_out_of_time():
            say("  iNaturalist: stopped looking at half the time limit")
            break
        try:
            data = s.get(INAT + "observations", timeout=60, params={
                "quality_grade": "research", "photo_license": "cc0,cc-by", "iconic_taxa": group,
                "place_id": provinces[prov], "per_page": 50, "page": rng.randint(1, 5), "order_by": "id"}).json()
        except Exception:  # noqa: BLE001 - next pair
            continue
        got = 0
        for o in data.get("results") or []:
            if got >= per_pair or o.get("id") in seen:
                continue
            item = inat_item(o, prov, question)
            if item:
                seen.add(o["id"])
                items.append(item)
                got += 1
        time.sleep(1.1)                    # iNaturalist asks for at most about one request a second
    rng.shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit]
    say(f"inaturalist_ca: {len(fetched)} pictures")
    return with_twins(fetched)


def inat_item(o, prov, question):
    """(file name, photo address, rows) for one iNaturalist observation whose photo is CC0 or CC BY, or None."""
    taxon, photos = o.get("taxon") or {}, o.get("photos") or []
    photo = next((ph for ph in photos if (ph.get("license_code") or "") in ("cc0", "cc-by")), None)
    if not photo or not taxon.get("name") or not photo.get("url"):
        return None
    latin, common = taxon["name"], clean(taxon.get("preferred_common_name"))
    answer = f"This is {article(common)} {common} ({latin})." if common else f"This is {latin}."
    login = (o.get("user") or {}).get("login", "an iNaturalist user")
    place = ca(prov)
    credit = (f"Photo by {login} on iNaturalist, {photo['license_code'].upper()}, "
              f"https://www.inaturalist.org/observations/{o['id']}")
    facts = {"taxon_id": taxon.get("id"), "rank": taxon.get("rank"), "observed_on": o.get("observed_on")}
    rows = [{"question": question, "answer": answer, "credit": credit, "facts": facts, **where(place)},
            {"question": "Where was this photo taken?", "answer": f"It was taken in {place}.", "credit": credit,
             **where(place)}]
    return f"inatca-{photo['id']}.jpg", photo["url"].replace("/square.", "/large."), rows


# ----------------------------------------------------------------- commons_ca_money

DOLLARS = {"1": "one-dollar", "2": "two-dollar", "5": "five-dollar", "10": "ten-dollar", "20": "twenty-dollar",
           "50": "fifty-dollar", "100": "hundred-dollar", "500": "five-hundred-dollar", "1000": "thousand-dollar"}
COINS = [("One cent coins of Canada", "a Canadian one-cent coin (a penny; Canada stopped making pennies in 2012)"),
         ("Nickel (Canadian coin)", "a Canadian five-cent coin (a nickel)"),
         ("Ten cent coins of Canada", "a Canadian ten-cent coin (a dime)"),
         ("Twenty five cent coins of Canada", "a Canadian 25-cent coin (a quarter)"),
         ("Fifty-cent coins of Canada", "a Canadian fifty-cent coin"),
         ("One dollar coins of Canada", "a Canadian one-dollar coin (the gold-coloured 'loonie' since 1987, which "
                                        "shows a loon)"),
         ("Two dollar coins of Canada", "a Canadian two-dollar coin (the two-coloured 'toonie')")]


def money_specs():
    """The commons_ca_money categories: banknotes by face value and coins by denomination."""
    specs = [us_spec(f"{n} Canadian dollar banknotes", MONEY_Q, f"This is a Canadian {word} bill (a {n}-dollar "
                     "banknote).", CANADA, 1, "origin") for n, word in DOLLARS.items()]
    specs += [us_spec(c, MONEY_Q, f"This is {name}.", CANADA, 1, "origin") for c, name in COINS]
    return specs


def build_commons_ca_money(limit):
    """The Commons Canadian banknotes and coins pack."""
    return commons_pack(money_specs(), limit, "camoney")


# ----------------------------------------------------------------- ca_road_signs

SIGN_DRAWINGS = ["Diagrams of road signs of Canada", "Diagrams of regulatory road signs of Canada",
                 "Diagrams of warning road signs of Canada", "Diagrams of guide and information road signs of Canada",
                 "Diagrams of school road signs of Canada", "Diagrams of speed limit signs of Canada",
                 "Diagrams of temporary road signs of Canada", "Diagrams of level crossing road signs of Canada",
                 "Manual of Uniform Traffic Control Devices for Canada - Regulatory road signs",
                 "Manual of Uniform Traffic Control Devices for Canada - Warning road signs",
                 "Manual of Uniform Traffic Control Devices for Canada - Informational road signs",
                 "Manual of Uniform Traffic Control Devices for Canada - Temporary road signs"] + \
                [f"Diagrams of road signs of {p}" for p in PROVINCES + ["Yukon", "the Northwest Territories"]]
# Canadian sign numbers: the national manual's ("RA-1", "WA-11", "IB-5", "TC-4") and Ontario's ("Rb-1", "Wa-33"),
# and Quebec's ("P-10", "D-50-P").
CA_SIGN_NUMBER = re.compile(r"(?<![A-Za-z0-9])((?:R|W|I|T|G)[A-Ea-e]-\d{1,3}[A-Za-z]{0,2}|"
                            r"[PDT]-\d{2,4}(?:-[A-Z0-9]{1,3})?)(?![A-Za-z0-9])")
CA_SIGN_NOISE = re.compile(r"\b(custom|hand-coded|svg|png|drawn|made|version|file|from the manual of uniform traffic "
                           r"control devices( for canada)?|in canada|of canada|canadian|canada|in ontario|of ontario|"
                           r"in quebec|of quebec|ontario|qu[eé]bec|british columbia|alberta|mutcdc|tac)\b", re.I)
SIGN_PHOTOS = [("Stop signs in Canada", "It is a stop sign: stop completely, then go on when it is safe. In Quebec it "
                                        "says ARRÊT, and some Canadian stop signs say both STOP and ARRÊT."),
               ("Stop signs in Quebec", "It is a stop sign in Quebec: stop completely, then go on when it is safe. "
                                        "Quebec's say ARRÊT (or ARRÊT and STOP)."),
               ("Speed limit signs in Canada", "It is a speed limit sign: the highest speed allowed, in kilometres "
                                               "per hour."),
               ("Pedestrian-related road signs in Canada", "It is a pedestrian sign: people may be crossing the "
                                                           "road here."),
               ("School-related road signs in Canada", "It is a school sign: a school or a school crossing is near, "
                                                       "so drive slowly and watch for children."),
               ("Yield signs in Ontario", "It is a yield sign: give way to traffic on the road you are joining."),
               ("Bilingual road signs in Canada", "It is a bilingual road sign, in English and French."),
               ("Warning road signs in Canada", "It is a warning sign (in Canada usually a yellow diamond): a hazard "
                                                "or a change in the road is ahead.")]


# Words that show a sign's description is in French (Quebec's drawings): not used for the English answer.
FRENCH = re.compile(r"\b(du|de|des|la|le|les|au|aux|et|panneau|interdiction|arr[eê]t|vitesse|chauss[eé]e|"
                    r"virage|obligatoire|d'\w+|l'\w+)\b", re.I)


# Sign photo subcategories that are not road signs ("Speed limit railway signs in Canada").
NOT_ROAD = re.compile(r"\b(railway|railroad|rail|train|trains|marine|boat|ship|navigation|ski)\b", re.I)


def ca_sign_meaning(title, text):
    """(sign number, what the sign means) of a Canadian sign drawing, from its file name and its own English
    description: "Ontario Rb-1.svg", "Stop sign" -> ("Rb-1", "Stop sign"); a quoted wording ('"NO STOPPING"') ->
    'it reads "NO STOPPING"'. The words are "" when the description gives neither (a French description is not
    used)."""
    name = title.split(":", 1)[-1].rsplit(".", 1)[0]
    m = CA_SIGN_NUMBER.search(name) or CA_SIGN_NUMBER.search(text or "")
    number = m.group(1) if m else ""
    text = clean(text or "")
    quoted = QUOTED.search(text)
    if quoted and in_english(quoted.group(1) + " of the"):
        return number, f'it reads "{quoted.group(1).strip()}"'
    first = re.split(r"[:.;(]|, (?:a|an|the|which|located)\b", text)[0]
    first = clean(CA_SIGN_NOISE.sub(" ", first)).strip(" ,-")
    if CA_SIGN_NUMBER.fullmatch(first or "") or FRENCH.search(first or ""):
        first = ""
    if not first or len(first.split()) > 10 or not in_english(first + " of the") or not re.search(r"[a-z]", first):
        return number, ""
    return number, first[:1].upper() + first[1:]


def sign_drawing_titles(s):
    """The titles of the Canadian sign drawings (SVG and PNG) of every drawing category, once each, shuffled."""
    titles = []
    for category in SIGN_DRAWINGS:
        if listing_out_of_time():
            break
        titles += commons_members(s, category, "file")
        time.sleep(1)
    titles = [t for t in dict.fromkeys(titles) if t.lower().endswith((".svg", ".png"))]
    pass_random(1867).shuffle(titles)
    return titles


def build_ca_road_signs(limit):
    """Canadian road sign drawings (about two thirds: each with its number and its own description, set black on
    white) and photos of common Canadian signs."""
    s = session()
    drawings = int(limit * 0.65) + 1
    titles = sign_drawing_titles(s)
    say(f"Canadian road sign drawings: {len(titles)} files")
    items = []
    for title, url, credit, text, _ in mech_entries(s, titles[:int(drawings * 1.8) + 10], drawings=True):
        if len(items) >= drawings * 1.1 or listing_out_of_time():
            break
        number, meaning = ca_sign_meaning(title, text)
        if not meaning:
            continue
        answer = (f"It is a Canadian road sign; {meaning}." if meaning.startswith("it reads") else
                  f"It is a Canadian road sign: {meaning}.") + (f" (Sign {number}.)" if number else "")
        items.append((file_name("casign", title), url,
                      [{"question": SIGN_Q, "answer": answer, "credit": credit, "place": CANADA,
                        "facts": {"sign_number": number} if number else {}}]))
    out = []
    for name, data, rows in commons_fetch(items, raw=True):
        try:
            picture = symbol_picture(data, side=320)
        except Exception:  # noqa: BLE001 - a drawing that cannot be read is left out
            continue
        jpeg = io.BytesIO()
        picture.save(jpeg, "JPEG", quality=92)
        out.append((name, jpeg.getvalue(), rows))
    out = with_twins(out[:drawings])
    photos = [us_spec(c, SIGN_Q, a, "Quebec, Canada" if "Quebec" in c else "Ontario, Canada" if "Ontario" in c
                      else CANADA, 1) for c, a in SIGN_PHOTOS]
    found = us_commons(photos, max(1, limit - count_pictures(out)), "casignphoto")
    found = drop_items(found, NOT_ROAD, "a railway or boat sign, not a road sign")
    out += with_twins(commons_fetch(found)[:max(1, limit - count_pictures(out))])
    return out


# ----------------------------------------------------------------- commons_ca_shops

def place_kind(category, answer, depth=1, place=CANADA):
    """A spec asking "What kind of place is this?"."""
    return us_spec(category, PLACE_Q, answer, place, depth)


def happening(category, answer, depth=1, place=CANADA):
    """A spec asking "What is happening here?"."""
    return us_spec(category, HAPPENING_Q, answer, place, depth)


SHOPS = [
    place_kind("Supermarkets in Canada", "This is a supermarket in Canada."),
    place_kind("Grocery stores in Canada", "This is a grocery store in Canada."),
    place_kind("Dépanneurs", "This is a dépanneur, a Quebec corner store selling snacks, drinks, milk, beer and "
                             "everyday things."),
    place_kind("Convenience stores in Canada", "This is a convenience store in Canada: snacks, drinks and everyday "
                                               "things, often open late."),
    place_kind("Sobeys", "This is a Sobeys, a Canadian supermarket chain."),
    place_kind("Loblaws", "This is a Loblaws, a Canadian supermarket chain."),
    place_kind("Canadian Tire stores", "This is a Canadian Tire store, a Canadian chain selling car parts, tools, "
                                       "household goods and sports gear.", 0),
    us_spec("Supermarket aisles", PLACE_Q, "This is a supermarket aisle, with shelves of products on both sides.",
            "", 1),
]


def build_commons_ca_shops(limit):
    """The Commons Canadian shops pack."""
    return commons_specs_pack(SHOPS, limit, "cashop")


# ----------------------------------------------------------------- commons_ca_holidays

HOLIDAYS = [
    happening("Canada Day", "This is Canada Day (1 July), Canada's national holiday: red and white, maple-leaf "
                            "flags, parades and fireworks."),
    happening("Canada Day in Toronto", "This is Canada Day (1 July) in Toronto.", 1, "Toronto, Ontario, Canada"),
    happening("Victoria Day", "This is Victoria Day, the Monday holiday in late May, often with fireworks; many "
                              "Canadians open their cottages and plant gardens that weekend."),
    happening("Thanksgiving in Canada", "This is Thanksgiving in Canada, on the second Monday of October: a harvest "
                                        "holiday with a family dinner, often turkey and pumpkin pie."),
    happening("Remembrance Day in Canada", "This is Remembrance Day in Canada (11 November): people wear red poppies "
                                           "and stand silent at 11 o'clock to remember those who died in wars."),
    happening("National Holiday (Quebec)", "This is the Fête nationale du Québec (24 June, Saint-Jean-Baptiste "
                                           "Day): blue and white fleur-de-lis flags, bonfires, concerts and parades.",
              1, "Quebec, Canada"),
    happening("Christmas in Canada", "This is Christmas in Canada."),
    happening("Christmas lights in Canada", "These are Christmas lights in Canada, on houses, trees or streets."),
    happening("Easter in Canada", "This is Easter in Canada."),
    happening("Halloween in Canada", "This is Halloween in Canada (31 October): costumes, trick-or-treating, pumpkins "
                                     "and spooky decorations."),
    happening("Winterlude", "This is Winterlude, Ottawa's February winter festival: ice sculptures and skating on "
                            "the frozen Rideau Canal.", 1, "Ottawa, Ontario, Canada"),
    happening("Calgary Stampede", "This is the Calgary Stampede, a July rodeo and fair: cowboy hats, rodeo events, "
                                  "a midway and pancake breakfasts.", 1, "Calgary, Alberta, Canada"),
    happening("Carnaval de Québec", "This is the Carnaval de Québec, Quebec City's winter carnival: snow sculptures, "
                                    "night parades and its snowman mascot Bonhomme.", 1,
              "Quebec City, Quebec, Canada"),
    happening("Farmers' markets in Canada", "This is a farmers' market in Canada."),
    happening("Parades in Canada", "This is a parade in Canada."),
    happening("Fireworks in Canada", "This is a fireworks display in Canada."),
    happening("Polling stations in Canada", "This is a polling station in Canada, where people vote in an election.",
              0),
    happening("Curling in Canada", "This is curling: players slide heavy granite stones along the ice toward a "
                                   "target, sweeping the ice in front of them."),
    happening("Snow removal in Canada", "This is snow being cleared in Canada, by ploughs, blowers or shovels."),
    us_spec("Snowbanks", WHAT_Q, "These are snowbanks: piles of snow pushed up beside a road or path.", "", 1),
]


def build_commons_ca_holidays(limit):
    """The Commons Canadian holidays, events and seasons pack (the US pack's filters: adult graduations only, no
    official speeches or military events)."""
    return commons_specs_pack(HOLIDAYS, limit, "caholiday", after=canadian_holidays)


# Party politics filed under holiday categories (a candidate's campaign office under "Easter eggs in Canada").
POLITICS = re.compile(r"\b((?i:campaign\w*|candidates?|riding|party leader|premier|prime minister)|MLA|MPP|MNA|"
                      r"M\.?P\.?|NDP|Liberal|Conservative|Bloc)\b")


def canadian_holidays(items):
    """The US pack's everyday filter (no official speeches or military events, adult graduations only), and no
    party politics."""
    return drop_items(everyday_holidays(items), POLITICS, "party politics, not an everyday holiday")


# ----------------------------------------------------------------- commons_ca_eating_out

EATING_OUT = [
    place_kind("Tim Hortons", "This is a Tim Hortons, Canada's best-known coffee and doughnut shop chain."),
    us_spec("Poutine", WHAT_Q, "This is poutine: French fries topped with cheese curds and gravy, a dish from "
                               "Quebec.", "", 1),
    place_kind("Restaurants in Canada", "This is a restaurant in Canada."),
    place_kind("Coffee shops in Canada", "This is a coffee shop in Canada."),
    place_kind("Fast food restaurants in Canada", "This is a fast-food restaurant in Canada: order at the counter, a "
                                                  "kiosk or the drive-through."),
    place_kind("Food trucks in Canada", "This is a food truck in Canada: food cooked and sold from a window in the "
                                        "side of a truck."),
    place_kind("Diners in Canada", "This is a diner in Canada: booths, a counter with stools, and breakfast all "
                                   "day."),
    place_kind("Bakeries in Canada", "This is a bakery in Canada."),
    place_kind("Pizzerias in Canada", "This is a pizzeria (a pizza restaurant) in Canada."),
    place_kind("Ice cream parlours in Canada", "This is an ice-cream parlour in Canada."),
    place_kind("Food courts in Canada", "This is a food court in Canada: counters of several restaurants around "
                                        "shared tables."),
]


def build_commons_ca_eating_out(limit):
    """The Commons eating out in Canada pack."""
    return commons_specs_pack(EATING_OUT, limit, "caeat")


# ----------------------------------------------------------------- commons_ca_getting_around

TORONTO, MONTREAL, VANCOUVER = "Toronto, Ontario, Canada", "Montreal, Quebec, Canada", "Vancouver, British Columbia, " \
                                                                                      "Canada"
GETTING_AROUND = [
    place_kind("Toronto subway", "This is the Toronto subway, run by the Toronto Transit Commission (TTC).", 1,
               TORONTO),
    place_kind("Toronto Transit Commission", "This is the Toronto Transit Commission (TTC): Toronto's subway, "
                                             "streetcars and buses.", 1, TORONTO),
    place_kind("Montreal Metro stations", "This is a station of the Montreal Metro, Montreal's underground trains "
                                          "on rubber tyres.", 1, MONTREAL),
    place_kind("Société de transport de Montréal", "This is the Société de transport de Montréal (STM), Montreal's "
                                                   "Metro and buses.", 1, MONTREAL),
    place_kind("TransLink (British Columbia)", "This is TransLink, the Vancouver area's public transit: SkyTrain, "
                                               "buses and the SeaBus.", 1, VANCOUVER),
    place_kind("GO Transit", "This is GO Transit, the green and white commuter trains and buses of the Toronto "
                             "region.", 1, "Ontario, Canada"),
    place_kind("Via Rail stations in Ontario", "This is a VIA Rail station, where Canada's intercity passenger "
                                               "trains stop.", 1, "Ontario, Canada"),
    place_kind("Via Rail stations in Quebec", "This is a VIA Rail station, where Canada's intercity passenger trains "
                                              "stop.", 1, "Quebec, Canada"),
    place_kind("CTrain stations", "This is a station of Calgary's CTrain, its light rail.", 1,
               "Calgary, Alberta, Canada"),
    place_kind("O-Train stations", "This is a station of Ottawa's O-Train, its light rail.", 1,
               "Ottawa, Ontario, Canada"),
    place_kind("Buses in Toronto", "This is a city bus in Toronto.", 1, TORONTO),
    place_kind("Buses in Montreal", "This is a city bus in Montreal.", 1, MONTREAL),
    place_kind("Bus stops in Canada", "This is a bus stop in Canada."),
    place_kind("Bus shelters in Canada", "This is a bus shelter in Canada."),
    us_spec("Presto card", WHAT_Q, "This is a PRESTO card, the tap-on fare card for transit in Toronto, Ottawa and "
                                   "the rest of Ontario, or one of its card readers.", "Ontario, Canada", 1),
    place_kind("Toronto Pearson International Airport", "This is Toronto Pearson International Airport, Canada's "
                                                        "busiest airport.", 1, "Mississauga, Ontario, Canada"),
    place_kind("Vancouver International Airport", "This is Vancouver International Airport.", 1,
               "Richmond, British Columbia, Canada"),
    place_kind("Interior of Montréal-Pierre Elliott Trudeau International Airport", "This is the inside of "
               "Montréal-Trudeau International Airport.", 1, "Dorval, Quebec, Canada"),
    place_kind("Interiors of airports in Canada", "This is the inside of an airport in Canada."),
    place_kind("Gas stations in Canada", "This is a gas station in Canada, where cars fill up with fuel (sold by the "
                                         "litre)."),
    place_kind("Electric vehicle charging stations in Canada", "This is a charging station for electric cars in "
                                                               "Canada."),
    place_kind("BC Ferries", "This is BC Ferries, the ferries between Vancouver Island, the islands and the British "
                             "Columbia mainland.", 1, "British Columbia, Canada"),
    us_spec("Parking meters in Canada", WHAT_Q, "This is a parking meter in Canada: pay here for street parking.",
            CANADA, 1),
    us_spec("Pedestrian signals in Canada", WHAT_Q, "This is a pedestrian signal in Canada: a walking person means "
                                                    "walk, a raised hand means don't walk (often with a countdown).",
            CANADA, 1),
]


def build_commons_ca_getting_around(limit):
    """The Commons getting around in Canada pack."""
    return commons_specs_pack(GETTING_AROUND, limit, "cago")


# ----------------------------------------------------------------- commons_ca_public_places

PUBLIC_PLACES = [
    place_kind("Post offices in Canada", "This is a post office in Canada."),
    place_kind("Service Canada", "This is a Service Canada office, where people apply for passports, pensions, "
                                 "employment insurance and social insurance numbers.", 0),
    place_kind("ServiceOntario", "This is a ServiceOntario office, where people renew driver's licences, health "
                                 "cards and licence plates in Ontario.", 0, "Ontario, Canada"),
    place_kind("Shoppers Drug Mart", "This is a Shoppers Drug Mart, a Canadian pharmacy chain: a pharmacy counter "
                                     "and aisles of health and everyday products."),
    place_kind("Jean Coutu", "This is a Jean Coutu pharmacy (a Quebec-based pharmacy chain)."),
    place_kind("Rexall (Canada)", "This is a Rexall pharmacy in Canada."),
    place_kind("Uniprix", "This is a Uniprix pharmacy (a Quebec-based pharmacy chain)."),
    place_kind("Pharmacies in Canada", "This is a pharmacy in Canada."),
    place_kind("Libraries in Canada", "This is a library in Canada."),
    place_kind("Public libraries in Canada", "This is a public library in Canada."),
    place_kind("Hospitals in Canada", "This is a hospital in Canada."),
    place_kind("City halls in Canada", "This is a city hall in Canada."),
    place_kind("Courthouses in Canada", "This is a courthouse in Canada."),
    place_kind("Fire stations in Canada", "This is a fire station in Canada."),
    place_kind("Shopping malls in Canada", "This is a shopping mall in Canada."),
    place_kind("Interiors of shopping malls in Canada", "This is the inside of a shopping mall in Canada."),
    place_kind("Banks in Canada", "This is a bank in Canada."),
    place_kind("Laundromats in Canada", "This is a laundromat in Canada: coin- or card-operated washers and dryers "
                                        "for anyone to use.", 0),
    place_kind("Hardware stores in Canada", "This is a hardware store in Canada."),
    place_kind("Department stores in Canada", "This is a department store in Canada."),
    place_kind("Interiors of churches in Canada", "This is the inside of a church in Canada."),
    place_kind("Hotels in Canada", "This is a hotel in Canada."),
    us_spec("Vending machines in Canada", WHAT_Q, "This is a vending machine in Canada: choose with the buttons, "
                                                  "then pay.", CANADA, 1),
]


def build_commons_ca_public_places(limit):
    """The Commons Canadian public places and services pack (hospital photos naming a patient are left out)."""
    return commons_specs_pack(PUBLIC_PLACES, limit, "capublic", after=no_patients)


# ----------------------------------------------------------------- commons_ca_archives

# (Commons category, the keeper as said in a sentence, how many listing pages of 500 to sample; 0: its subcategories)
ARCHIVES = [
    ("Images from Library and Archives Canada", "Library and Archives Canada", 4),
    ("Files from Library and Archives Canada / Bibliothèque et Archives Canada Flickr stream",
     "Library and Archives Canada", 2),
    ("Images from the City of Toronto Archives", "the City of Toronto Archives", 3),
    ("Images from Toronto Public Library", "the Toronto Public Library", 1),
    ("Images from Bibliothèque et Archives nationales du Québec", "Bibliothèque et Archives nationales du Québec "
                                                                  "(BAnQ)", 3),
    ("OGL-C", "the Government of Canada (Open Government Licence - Canada)", 2),
]
# The licences taken: public domain, CC0, CC BY, and the Open Government Licence - Canada (Commons writes "OGL-C" or
# the licence's name); never share-alike, non-commercial or no-derivatives.
OGL_CANADA = re.compile(r"^(ogl[- ]?(c|on|bc|alberta|ab|nb|yt|ns|pei|nl)\b|ogl[- ](canada|ontario|alberta|yukon)|"
                        r"open government licen[cs]e\s*[-–]\s*(canada|ontario|british columbia|alberta|new brunswick|"
                        r"yukon|nova scotia|prince edward island|newfoundland))", re.I)
NOT_FREE = re.compile(r"\b(SA|NC|ND)\b|-SA|-NC|-ND", re.I)
# Catalogue numbers and credit lines in archive captions: "MIKAN 3193234", "PA-012345", "e010861234",
# "Reference No. ...", "Fonds 1244, Item 1234", "Source: Library and Archives Canada", "Credit: ...".
ARCHIVE_NOISE = re.compile(
    r"(\b(MIKAN|Item ID number|Reference (No\.?|number)|Copy negative( number)?|Accession( number)?|Credit|Source|"
    r"Restrictions on use|Copyright|Archival reference no\.?)\s*[:#]?[^.;]*[.;]?"
    r"|\b(Fonds|Series|Item|File)\s+\d[\w,. -]*"
    r"|\b(PA|C|e|R)-?\d{5,9}\b|\b(Library and Archives Canada|Biblioth[eè]que et Archives (nationales du Qu[eé]bec|"
    r"Canada)|City of Toronto Archives|Toronto Public Library)\b[^.;]*[.;]?|\bTitle\s*:\s*)", re.I)


# Sentences about a dataset rather than the picture (Government of Canada survey photos: "This metadata covers ...").
DATA_NOTE = re.compile(r"\b(metadata|data ?sets?|this (record|collection) (covers|contains))\b", re.I)


def ca_free(licence):
    """True for a licence this pack takes: public domain, CC0, CC BY (MECH_FREE) or the Open Government Licence -
    Canada; never share-alike, non-commercial or no-derivatives."""
    licence = clean(licence)
    return bool(MECH_FREE.match(licence) or OGL_CANADA.match(licence)) and not NOT_FREE.search(licence)


def archive_caption(text):
    """An archive's caption without its catalogue numbers and credit lines (agency_caption takes out the rest):
    "Title: Main Street, Moose Jaw, Sask., 1912. MIKAN 3301234. Library and Archives Canada, PA-012345" ->
    "Main Street, Moose Jaw, Sask., 1912."; "" when nothing is left."""
    sentences = re.split(r"(?<=[.!?])\s+", clean(ARCHIVE_NOISE.sub(" ", clean(text))))
    return agency_caption(" ".join(s for s in sentences if not DATA_NOTE.search(s)))


def archive_entries(s, titles):
    """[(title, picture address, credit, raw description, year)] for Commons files whose licence ca_free takes
    (photos only), 50 at a time; the files left out are noted with the reason."""
    out = []
    for start in range(0, len(titles), 50):
        data = commons_get(s, {"action": "query", "titles": "|".join(titles[start:start + 50]), "prop": "imageinfo",
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
            if not ca_free(licence):
                considered(p["title"], page, f"its licence ({licence or 'none given'}) is not public domain, CC0, "
                                             "CC BY or the Open Government Licence - Canada")
                continue
            if info.get("mime") not in ("image/jpeg", "image/png", "image/tiff") or not info.get("thumburl"):
                considered(p["title"], page, f"not a photo ({info.get('mime') or 'no picture'})")
                continue
            artist = clean((meta.get("Artist") or {}).get("value")) or "unknown"
            out.append((p["title"], info["thumburl"], f"{p['title']} by {artist}, {licence}, {page}",
                        clean((meta.get("ImageDescription") or {}).get("value")), photo_year(meta)))
        time.sleep(1)
    return out


def archive_rows(caption, keeper, credit, words, home=""):
    """The rows of one archive photo: its caption (with the province it names, else the archive's own province
    home, as the place) and who keeps it; marked "child" and "content": "graphic" from its words."""
    prov = province_in(caption) or home
    place = where(ca(prov)) if prov else {}
    rows = [{"question": DESCRIBE_Q, "answer": caption, "credit": credit, **place},
            {"question": KEPT_Q, "answer": f"It is kept by {keeper}.", "credit": credit}]
    rows = [mark_child(r, words) for r in rows]
    if GRAPHIC.search(words):
        rows = [dict(r, content="graphic") for r in rows]
    return rows


# Medical scenes with people in archive photos ("A fresh air patient eating his dinner"): left out.
PATIENT = re.compile(r"\b(patients?|surgery|surgical|operating (room|theatre)|sanatori(um|a)|x-rays? of)\b", re.I)


def title_caption(title):
    """A file's title as a caption, for archives whose titles are their captions ("File:A cottage at Wasaga Beach
    (I0026362).jpg" -> "A cottage at Wasaga Beach."): the file type and the archive's image number taken out."""
    text = title.split(":", 1)[-1].rsplit(".", 1)[0]
    text = re.sub(r"\s*\((I|C|F|RG|PA|e)?\s?[\d-]{4,}\)\s*$", "", text).strip(" .")
    return text[:1].upper() + text[1:] + "." if text else ""


def archive_pack(sources, limit, prefix, seed, titles_are_captions=False):
    """A pack of archive photos from [(Commons category, keeper, listing pages, province or "")]: each category
    sampled at random places, its free photos with the archive's caption (or, with titles_are_captions, the file's
    title when it has no description of its own); a free photo whose caption is under six English words (or not
    respectful today) is set aside for a description; hospital photos naming a patient are left out."""
    s, rng, items, seen = session(), pass_random(seed), [], set()
    share = math.ceil(limit * 1.2 / len(sources))
    for category, keeper, pages, home in sources:
        if listing_out_of_time():
            break
        titles = [t for t in sample_members(s, category, pages, rng) if not NOT_A_PHOTO.search(t) and t not in seen]
        rng.shuffle(titles)
        say(f"Commons {category}: {len(titles)} files sampled")
        got = 0
        for start in range(0, len(titles), 100):
            if got >= share or listing_out_of_time():
                break
            for title, url, credit, raw, year in archive_entries(s, titles[start:start + 100]):
                if got >= share:
                    break
                seen.add(title)
                words = f"{title} {raw}"
                if NUDE.search(words) or NOT_SHOWN.search(words):
                    considered(title, url, "its words are about nudity, swimwear or evidence photos")
                    continue
                if PATIENT.search(words):
                    considered(title, url, "its words name a patient or an operation (no medical scenes here)")
                    continue
                caption = archive_caption(raw)
                if only_the_name(caption, title):
                    caption = title_caption(title) if titles_are_captions else ""
                if not caption and titles_are_captions:
                    caption = title_caption(title)
                poor = ("its caption is under six English words" if not caption or len(caption.split()) < 6
                        or not in_english(caption) else
                        "its caption uses words that are not respectful today" if NOT_RESPECTFUL.search(caption)
                        else "")
                prov = province_in(words) or home
                if poor:
                    needs_description(file_name(prefix, title), url, credit, "public domain, CC0, CC BY or an Open "
                                      "Government Licence of Canada or a province (each file's own licence)",
                                      text=caption or raw[:300], title=title, reason=poor,
                                      place=ca(prov) if prov else "", page_url=credit.rsplit(", ", 1)[-1],
                                      extra={"keeper": keeper, "commons_category": category, "year": year,
                                             "child": bool(CHILD.search(words)),
                                             "content": "graphic" if GRAPHIC.search(words) else "",
                                             "not_for_picture_making": True})
                    continue
                items.append((file_name(prefix, title), url, archive_rows(caption, keeper, credit, words, home)))
                got += 1
        say(f"  {got} photos from {keeper}")
    rng.shuffle(items)
    fetched = commons_fetch(items[:int(limit * 1.1) + 2])[:limit]
    say(f"{prefix}: {len(fetched)} pictures")
    return with_twins(fetched)


def build_commons_ca_archives(limit):
    """The Canadian archive photos pack (Library and Archives Canada, Toronto, BAnQ, OGL-Canada)."""
    return archive_pack([(c, k, n, "") for c, k, n in ARCHIVES], limit, "caarch", 1872)


# ----------------------------------------------------------------- commons_ca_provincial

# Commons files under a province's or territory's Open Government Licence (each tracking category of the Commons
# licence templates OGL-ON, OGL-Alberta, OGL-BC, OGL-NB and OGL-YT, checked in November 2026: 3,981, 8, 2, 8 and 2
# files). Nearly all of OGL-ON is the Archives of Ontario's own upload (its GLAM Wiki project: the Audio-Visual
# Education Branch photographs and others, titled like "A cottage at Wasaga Beach (I0026362)").
PROVINCIAL = [
    ("OGL-ON", "the Archives of Ontario (Open Government Licence - Ontario)", 6, "Ontario"),
    ("OGL-Alberta", "the Government of Alberta (Open Government Licence - Alberta)", 1, "Alberta"),
    ("OGL-BC", "the Government of British Columbia (Open Government Licence - British Columbia)", 1,
     "British Columbia"),
    ("OGL-NB", "the Government of New Brunswick (Open Government Licence - New Brunswick)", 1, "New Brunswick"),
    ("OGL-YT", "the Government of Yukon (Open Government Licence - Yukon)", 1, "Yukon"),
]


def build_commons_ca_provincial(limit):
    """The provincial and territorial government photos pack (their titles are their captions)."""
    return archive_pack(PROVINCIAL, limit, "caprov", 1791, titles_are_captions=True)


# ----------------------------------------------------------------- commons_ca_daily_life

DAILY = [
    happening("Winter in Canada", "This is winter in Canada: snow, cold and people dressed for it."),
    happening("Winter in Toronto", "This is winter in Toronto.", 1, TORONTO),
    happening("Winter in Montreal", "This is winter in Montreal.", 1, MONTREAL),
    happening("Snow in Toronto", "This is a snowy day in Toronto.", 1, TORONTO),
    happening("Snow in Montreal", "This is a snowy day in Montreal.", 1, MONTREAL),
    us_spec("Snow shovels", WHAT_Q, "This is a snow shovel, for clearing snow from driveways and paths.", "", 1),
    happening("Rideau Canal Skateway", "This is skating on the Rideau Canal Skateway in Ottawa: in winter the frozen "
                                       "canal becomes a skating path several kilometres long.", 0,
              "Ottawa, Ontario, Canada"),
    happening("Ice skating in Canada", "This is ice skating in Canada."),
    happening("Pond hockey", "This is pond hockey: a casual game of ice hockey outdoors on a frozen pond or rink.", 1,
              ""),
    happening("Ice hockey in Ontario", "This is ice hockey in Ontario.", 1, "Ontario, Canada"),
    happening("Ice fishing in Canada", "This is ice fishing in Canada: fishing through a hole cut in the ice of a "
                                       "frozen lake, often from a small hut."),
    happening("Tobogganing in Canada", "This is tobogganing in Canada: sliding down a snowy hill on a sled."),
    happening("Canoeing in Canada", "This is canoeing in Canada."),
    happening("Camping in Canada", "This is camping in Canada."),
    happening("Picnics in Canada", "This is a picnic in Canada."),
    happening("Cycling in Montreal", "This is cycling in Montreal.", 1, MONTREAL),
    happening("Cycling in Canada", "This is cycling in Canada."),
    happening("Commuters in Canada", "These are commuters in Canada, on their way to or from work or school."),
    us_spec("People in Toronto", DESCRIBE_Q, None, TORONTO, 1),
    happening("Markets in Canada", "This is a market in Canada."),
    happening("Festivals in Canada", "This is a festival in Canada."),
    us_spec("People of Canada", DESCRIBE_Q, None, CANADA, 0),
]
# Sacred and ceremonial life is left out (the owner's rule: only when its source says it may be shared, and Commons
# does not say so), and so are categories and files about named people.
SACRED = re.compile(r"\b(sacred|ceremon\w*|pow ?wows?|smudg\w*|sweat ?lodges?|potlatch\w*|sun ?dance|regalia|"
                    r"spirit\w*|prayers?|praying|funerals?|burials?|graves?|cemeter\w*)\b", re.I)


def daily_life(items):
    """The holiday filters (no official events, military events or party politics) and no sacred or ceremonial
    scenes."""
    return drop_items(canadian_holidays(items), SACRED, "a sacred or ceremonial scene (left out unless its source "
                                                          "says it may be shared)")


def build_commons_ca_daily_life(limit):
    """The Commons everyday life in Canada pack: winter, skating and hockey, cottage-country pastimes, cycling,
    commuting, markets and festivals (photos of 1990 or later)."""
    return commons_specs_pack(DAILY, limit, "cadaily", after=daily_life)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
CANADA_PACKS = {
    "commons_ca_homes": (build_commons_ca_homes, COMMONS_CREDIT.format(
        what="categories of Canadian houses (by province and territory), house kinds and rooms")),
    "commons_ca_streets": (build_commons_ca_streets, COMMONS_CREDIT.format(
        what="categories of streets in Canadian cities, pedestrians and street photography (what people wear from "
             "the clothing categories each photo sits in)")),
    "commons_ca_cars": (build_commons_ca_cars, COMMONS_CREDIT.format(
        what="categories of automobiles in each Canadian province (the model and colour from the categories each "
             "photo sits in)")),
    "inaturalist_ca": (build_inaturalist_ca,
                       "iNaturalist (https://www.inaturalist.org) research-grade observations in each Canadian "
                       "province and territory: photos CC0 or CC BY, each photographer credited below; names by the "
                       "iNaturalist community."),
    "commons_ca_money": (build_commons_ca_money, COMMONS_CREDIT.format(
        what="categories of Canadian banknotes by face value and coins by denomination (only files whose own licence "
             "is free: mostly old notes and coins whose Crown copyright has expired)")),
    "ca_road_signs": (build_ca_road_signs,
                      "Wikimedia Commons: Category:Diagrams of road signs of Canada, its provinces' and the Manual of "
                      "Uniform Traffic Control Devices for Canada categories (drawings public domain or CC0/CC BY, "
                      "each checked; set black on white) and photo categories of Canadian road signs (CC0, public "
                      "domain or CC BY), each with its author and file page below. Meanings from each drawing's own "
                      "description. https://commons.wikimedia.org"),
    "commons_ca_shops": (build_commons_ca_shops, COMMONS_CREDIT.format(
        what="categories of Canadian supermarkets, grocery stores, dépanneurs, convenience stores and chains")),
    "commons_ca_holidays": (build_commons_ca_holidays, COMMONS_CREDIT.format(
        what="categories of Canadian holidays, festivals and seasons (Canada Day, Victoria Day, Thanksgiving, "
             "Remembrance Day, the Fête nationale du Québec, Winterlude, the Calgary Stampede ...)")),
    "commons_ca_eating_out": (build_commons_ca_eating_out, COMMONS_CREDIT.format(
        what="categories of Tim Hortons shops, poutine, Canadian restaurants, coffee shops and food shops")),
    "commons_ca_getting_around": (build_commons_ca_getting_around, COMMONS_CREDIT.format(
        what="categories of the TTC, Montreal Metro, TransLink, GO Transit, VIA Rail, Canadian airports, buses, "
             "gas and charging stations")),
    "commons_ca_public_places": (build_commons_ca_public_places, COMMONS_CREDIT.format(
        what="categories of post offices, Service Canada, pharmacies, libraries, hospitals and other public places "
             "in Canada")),
    "commons_ca_provincial": (build_commons_ca_provincial,
                              "Wikimedia Commons files under the Open Government Licences of Ontario, Alberta, "
                              "British Columbia, New Brunswick and Yukon (Commons templates OGL-ON, OGL-Alberta, "
                              "OGL-BC, OGL-NB, OGL-YT), nearly all the Archives of Ontario's own upload. Each "
                              "licence: 'You are free to: Copy, modify, publish, translate, adapt, distribute or "
                              "otherwise use the Information in any medium, mode or format for any lawful purpose.' "
                              "Contains information licensed under the Open Government Licence - Ontario (and - "
                              "Alberta, - British Columbia, - New Brunswick, - Yukon). Each with its file page below."),
    "commons_ca_daily_life": (build_commons_ca_daily_life, COMMONS_CREDIT.format(
        what="categories of everyday life in Canada (winter and snow, skating, pond hockey, ice fishing, "
             "tobogganing, canoeing, camping, cycling, commuting, markets and festivals)")),
    "commons_ca_archives": (build_commons_ca_archives,
                            "Wikimedia Commons copies of photographs kept by Library and Archives Canada, the City of "
                            "Toronto Archives, the Toronto Public Library and Bibliothèque et Archives nationales du "
                            "Québec, and Government of Canada photos under the Open Government Licence - Canada 2.0 "
                            "(https://open.canada.ca/en/open-government-licence-canada). Each file's own licence is "
                            "checked: public domain (mostly Crown copyright expired, or photos taken before 1949), "
                            "CC0, CC BY or OGL-Canada; captions by the archives. Each with its file page below."),
}

# How many pictures a full build takes from each (each finishes well within about four hours on GitHub's machines;
# the Canadian Commons categories are smaller than the American ones).
CANADA_LIMITS = {
    "commons_ca_homes": 2500,           # 13 provinces and territories, 3 cities, 13 house kinds, 6 room categories
    "commons_ca_streets": 2000,         # 18 cities and 4 people categories
    "commons_ca_cars": 1200,            # 10 provinces and 3 more; only photos whose categories name a model
    "inaturalist_ca": 4000,             # 13 provinces and territories x 10 groups
    "commons_ca_money": 600,            # 9 banknote values and 7 coins (free files only)
    "ca_road_signs": 1500,              # about 25 drawing categories and 8 photo categories
    "commons_ca_shops": 800,            # 8 categories
    "commons_ca_holidays": 1500,        # 20 categories
    "commons_ca_eating_out": 1200,      # 11 categories
    "commons_ca_getting_around": 2000,  # 24 categories (station categories have one subcategory per station)
    "commons_ca_public_places": 2000,   # 24 categories
    "commons_ca_archives": 3000,        # 6 categories (about 16,000 files), sampled
    "commons_ca_provincial": 1500,      # 5 licence categories (about 4,000 files, nearly all Ontario's)
    "commons_ca_daily_life": 2000,      # 22 categories
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one Canada pack builder.")
    parser.add_argument("key", choices=sorted(CANADA_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = CANADA_PACKS[args.key][0](args.limit)
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
