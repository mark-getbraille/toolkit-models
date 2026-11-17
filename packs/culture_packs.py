"""Pack builders for sports, musical instruments, places of worship and religious life, architecture and landmarks,
civilian vehicles, and toys, games and playing cards, used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "place" where the record says where the photo was taken (see places.py) and "child": True
where the picture's own words or labels name a child (expression_packs.CHILD; picture-making leaves those rows out).
A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file"
names the same picture (food_packs.with_twins), so the zip holds each picture only once. The limit counts pictures.
No row here has a "content" tag: nothing is graphic, medical or nude.

Why: a describer for blind people should be able to say "This is kabaddi, a sport from India", "This is a saron, a
metallophone from Indonesia", "This is Harmandir Sahib, a gurdwara in Amritsar, India, a place of worship of
Sikhism", "This is the Eiffel Tower, a tower in Paris, France", "This is a Ford Model T, a car made by Ford" or "This is
the queen of hearts". Every fact in an answer comes from the source's own record: Wikidata (CC0) for names, kinds,
faiths (P140 religion), places (P131 located in, P17 country), architectural styles (P149), makers (P176), countries
of origin (P495) and years; the museum's record (the Met); the dataset's labels (Open Images, Roboflow, the playing
card folders, FEN positions, Google Landmarks); or a Commons category's own subject, said in a fixed plain sentence.
Nothing is written by an AI model. Faiths are named as Wikidata names them for each place (or, where Wikidata gives
none, by the kind of building: a mosque of Islam, a synagogue of Judaism, a gurdwara of Sikhism), never guessed from
the picture; festivals and objects of every faith are described plainly and respectfully.

The packs (all open: CC0, public domain, CC BY or MIT, checked at the source in November 2026):
  open_images_culture  Google Open Images V7 (validation and test sets): photos where people checked by hand that a
                       sport, sports equipment, a sports place, a musical instrument, a vehicle, a toy or game, or a
                       kind of building (church, mosque, temple, castle, lighthouse ...) is there. Labels CC BY 4.0;
                       each photo CC BY 2.0 (checked photo by photo), its photographer named. "What sport is this?",
                       "What musical instrument is in this picture?", "What vehicles are in this picture?" ...
                       (disability sports are in disability_packs, household toys also in open_images_objects).
  wikidata_sports      Sports, sports equipment and kinds of sports ground, from Wikidata (CC0: the sport's name, what
                       kind of sport it is, the country it comes from), each with free pictures from its Commons
                       category (CC0, public domain or CC BY, author credited): traditional sports around the world
                       (kabaddi, sepak takraw, buzkashi, hurling, sumo ...), Paralympic sports not already in
                       disability_packs (boccia, sitting volleyball, para ice hockey ...), and Commons scoreboards
                       (the score only where the file's own caption says it). "What sport is this?"
  wikidata_instruments Musical instruments of every culture (about 1,700 kinds on Wikidata with a Commons category: the
                       name, its kind, such as "metallophone" or "plucked string instrument", and the country it comes
                       from), with free Commons pictures. "What instrument is this?"
  met_instruments      The Metropolitan Museum of Art, Department of Musical Instruments (about 4,000 objects with
                       pictures; only those the Met marks public domain, CC0 Open Access): the object's name, its
                       Hornbostel-Sachs class, culture, country and date. "What instrument is this?" and "Tell me about
                       this museum object."
  wikidata_worship     Places of worship of every faith from Wikidata: churches, cathedrals, chapels, basilicas,
                       Eastern Orthodox churches, mosques, synagogues, Hindu, Buddhist, Jain, Taoist and Bahá'í temples,
                       gurdwaras, Shinto shrines, wats, stupas, pagodas, temples of Confucius, Zoroastrian fire temples,
                       Kingdom Halls and meeting houses: the name, the kind, the faith (P140, else the kind's own
                       faith), the place and country, and the architectural style; the Wikidata picture and more from
                       the place's Commons category (free licences only). "What place of worship is this, and of which
                       faith?", "Where was this photo taken?", "What architectural style is this building?"
  commons_religious_life  Wikimedia Commons categories of festivals and ceremonies (Diwali, Holi, Eid al-Fitr, Eid
                       al-Adha, Ramadan and iftar, Christmas nativity scenes, Hanukkah, Passover Seder, Sukkot, Purim,
                       Vesak, Vaisakhi, Navaratri, Durga Puja, Ganesh Chaturthi, Thaipusam, Losar, Obon, Timkat, Corpus
                       Christi and Holy Week processions), pilgrimages (Hajj, Kumbh Mela), places inside places of
                       worship (altars, mihrabs, minbars, iconostases, Torah arks, butsudan, kamidana, pulpits, fonts),
                       religious objects and symbols (rosaries, misbaha, tefillin, tallit, mezuzot, prayer rugs, Torah
                       scrolls, crucifixes, the khanda, prayer wheels and flags, omamori, ema, torii) and clergy dress
                       (cassocks, chasubles, mitres, Buddhist monks' robes). The category's fixed plain sentence, and
                       the file's caption.
  wikidata_landmarks   Famous buildings and monuments from Wikidata: World Heritage Sites and towers, castles, palaces,
                       bridges, skyscrapers, monuments, lighthouses, statues, mausoleums, opera houses, stadiums, forts
                       and archaeological sites with many Wikipedia articles (places of worship are in
                       wikidata_worship): the name, kind, place, country, year, architect and style. "What landmark is
                       this?", "Where was this photo taken?"
  wikidata_architecture  Architectural styles (Gothic, Art Deco, Brutalist, Mughal ...) and building parts (domes,
                       arches, columns, spiral staircases, gargoyles, minarets, roofs, doors, windows ...) from
                       Wikidata, with free pictures from their Commons categories. "What architectural style is
                       this?" and "What part of a building is this?"
  gldv2_landmarks      Google Landmarks Dataset v2 (Google, labels CC BY 4.0): its "clean" training images (about 1.6
                       million, verified to show their landmark), only those whose Commons licence (the dataset's own
                       attribution list) is CC0, public domain or CC BY; the landmark's name from its Commons category.
                       "What landmark or place is this?"
  wikidata_vehicle_models  Car models (make, model, kind of car, years where Wikidata gives them), motorcycle models,
                       bus models, truck models, tram types, locomotive classes and ferries, from Wikidata, with free
                       pictures from each model's Commons category. "What car is this?", "What motorcycle is this?" ...
                       (civil aircraft are in service_packs commons_airplanes; police cars, fire engines and
                       ambulances in service_packs commons_uniformed.)
  commons_vehicle_kinds  Wikimedia Commons categories of taxis of different cities (London black cabs, New York yellow
                       cabs ...), auto rickshaws and tuk-tuks, jeepneys, matatus, dolmuş, cycle rickshaws, school
                       buses, the Shinkansen, Melbourne trams, ferries, narrowboats, dhows, tandem and cargo bicycles,
                       scooters, mopeds, tractors, trucks, ice cream vans, food trucks, motorhomes, horse-drawn
                       carriages and snowmobiles, with a fixed plain sentence and the file's caption.
  wikidata_toys_games  Playing cards (each card of the deck, on Wikidata: "This is the ace of spades."), board games and
                       card games (with the country they come from), toys, and Commons categories of dice, LEGO, chess
                       sets, Rubik's Cubes, dominoes, mahjong tiles, jigsaw puzzles, dolls, teddy bears, kites, spinning
                       tops, yo-yos, wooden toys and video-game controllers. "Which playing card is this?" ...
  playing_cards        French Playing Cards (drFarid on Hugging Face, MIT licence): photos of real cards, every card of
                       the deck in its own folder. "Which playing card is this?"
  chess_pieces         Chess Pieces (Roboflow 100, made by Joseph Nelson and Brad Dwyer of Roboflow, CC BY 4.0; the
                       LibreYOLO copy on Hugging Face): real photos of a chessboard with every piece boxed by colour and
                       kind. "What chess pieces are on the board?"
  chess_positions      Chessboard renders (Peter A. Massih, CC BY 4.0; positions from the Lichess database, CC0):
                       rendered boards from real games, each with its position (FEN), said square by square in plain
                       words. "What is the position on this chessboard?"
  deepscores_sheet_music  DeepScoresV2 (Tuggener et al., ZHAW, CC BY 4.0, Zenodo 4012193; the zzsi copy on Hugging
                       Face): computer-engraved pages of sheet music with every symbol named, said as the clefs, the
                       time and key signatures, how many notes and rests, and the dynamics. Reading the actual notes
                       is beyond this; "What can you tell me about this sheet music?"

Share-alike, non-commercial and research collections on the same subjects, and the ones needing sign-up, are kit
download entries in training-kit/kit/culture_sources.py.

    python packs/culture_packs.py chess_pieces --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import json
import random
import re
import sys
import time
import urllib.parse

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, MUSEUM
from food_packs import (sentence, listed, with_twins, count_pictures, oi_lines, oi_licence_name,  # noqa: F401
                        commons_get, commons_entries, commons_place, OI_LABELS, OI_CLASSES, OI_IMAGES, OI_PICTURE)
from everyday_packs import a_or_an, number_word
from expression_packs import CHILD, OI_CHILD
from documentary_packs import finish, place_words, usable, tidy, ASK_DESCRIBE, ASK_WHERE
from places import where, country_named, place_name

ASK_SPORT = "What sport is this?"
ASK_EQUIPMENT = "What sports equipment is this?"
ASK_GROUND = "What kind of sports ground is this?"
ASK_INSTRUMENT = "What instrument is this?"
ASK_WORSHIP = "What place of worship is this, and of which faith?"
ASK_STYLE = "What architectural style is this building?"
ASK_LANDMARK = "What landmark is this?"
ASK_CAR = "What car is this?"
ASK_CARD = "Which playing card is this?"
ASK_GAME = "What game is this?"
ASK_TOY = "What toy is this?"
# Words that mark a file as not a photograph of the thing (drawings, maps, logos, stamps, models), or as a picture
# that may show a child where the file's words do not say so (novice monks are often children).
NOT_A_PHOTO = re.compile(r"\b(drawings?|diagrams?|maps?|plans?|logos?|icons?|emblems?|coats? of arms|flags? of|"
                         r"stamps?|postcards?|posters?|banknotes?|coins?|svg|clip ?art|illustrations?|engravings?|"
                         r"lithographs?|paintings?|sketch\w*|cartoons?|charts?|scans? of|screenshots?|"
                         r"blueprints?|elevations?|sections? of|schematics?)\b|\.(svg|gif|tiff?|pdf|djvu)$", re.I)
NOT_A_MODEL = re.compile(r"\b(scale models?|toy models?|die-?cast|models? of|miniatures?|lego|matchbox|hot wheels|"
                         r"replicas?|dioramas?)\b", re.I)
# The same, in a file's caption (a photo of a coin or a stamp showing a church is not a photo of the church).
NOT_SHOWN_TEXT = re.compile(r"\b(coins?|stamps?|banknotes?|postcards?|drawings?|paintings?|engravings?|"
                            r"lithographs?|illustrations?|logos?|maps?|diagrams?|floor plans?)\b", re.I)
YOUNG = re.compile(r"\b(novices?|samanera|schools? children|youth|junior|u-?1[0-9]|under-1[0-9])\b", re.I)
INSIDE = re.compile(r"\b(interior|inside|innen\w*|intérieur|interieur|nave|choir stalls?|prayer hall|sanctuary|"
                    r"altar|iconostas\w*|mihrab|ceiling|vault\w*)\b", re.I)


def safe_name(prefix, text):
    """A short file name from a title or label: "worship-Harmandir_Sahib_2014.jpg"."""
    stem = re.sub(r"[^\w.-]+", "_", str(text).split(":", 1)[-1].rsplit(".", 1)[0])[:80].strip("_")
    return f"{prefix}-{stem or 'picture'}.jpg"


def is_child(*texts):
    """True when any of texts names a child (expression_packs.CHILD) or a young person (YOUNG)."""
    return any(CHILD.search(t or "") or YOUNG.search(t or "") for t in texts)


def caption_row(text, title):
    """ "Describe this picture." with the file's own caption (6 words or more, nothing sexual), or None."""
    answer = tidy(text)
    if not usable(answer) or answer.lower().startswith(("file:", "dsc", "img")):
        return None
    return {"question": ASK_DESCRIBE, "answer": answer}


# ----------------------------------------------------------------- Wikidata

WDQS = "https://query.wikidata.org/sparql"
ENTITY = "http://www.wikidata.org/entity/"


def sparql(s, query, tries=5):
    """The result rows of a Wikidata query ([{name: value}], entity addresses shortened to Q-ids), waiting and
    trying again when the query service is busy (429, 5xx or a time-out); [] when it never answered."""
    wait = 10
    for _ in range(tries):
        try:
            r = s.get(WDQS, params={"query": query, "format": "json"}, timeout=180,
                      headers={"Accept": "application/sparql-results+json"})
            if r.status_code == 200:
                return [{k: v["value"].replace(ENTITY, "") for k, v in b.items()}
                        for b in r.json()["results"]["bindings"]]
            after = r.headers.get("Retry-After", "")
            pause = int(after) if after.isdigit() else wait
        except Exception:  # noqa: BLE001 - network trouble or a time-out: wait and try again
            pause = wait
        say(f"  Wikidata is busy: waiting {min(pause, 120)} seconds")
        time.sleep(min(pause, 120))
        wait = min(wait * 2, 120)
    say("  Wikidata did not answer this query; it is left out")
    return []


def subjects(rows):
    """Query rows grouped by ?item: [{"id", "label", <name>: [values in order] ...}], leaving out items with no
    English label (the label service then gives the Q-id)."""
    out = {}
    for b in rows:
        item, label = b.get("item", ""), clean(b.get("itemLabel"))
        if not item or not label or re.fullmatch(r"Q\d+", label):
            continue
        d = out.setdefault(item, {"id": item, "label": label})
        for k, value in b.items():
            if k in ("item", "itemLabel") or not value or re.fullmatch(r"Q\d+", value):
                continue
            values = d.setdefault(k, [])
            if value not in values:
                values.append(value)
    return list(out.values())


def first(d, key):
    """The first value of a subject's field, or ""."""
    return (d.get(key) or [""])[0]


def file_of(address):
    """A Commons file title from a Wikidata picture address (".../Special:FilePath/Harmandir%20Patna.jpg")."""
    return "File:" + urllib.parse.unquote(address.rsplit("/", 1)[-1]) if address else ""


def year_of(value):
    """ "1887" from "1887-01-01T00:00:00Z", "300 BC" from "-0300-...", or ""."""
    m = re.match(r"^(-?)0*(\d{1,4})-", value or "")
    if not m or m.group(2) == "0":
        return ""
    return f"{m.group(2)} BC" if m.group(1) else m.group(2)


ADMIN_WORDS = re.compile(r"\b(district|municipality|prefecture|county|province|region|governorate|oblast|raion|"
                         r"commune|department|arrondissement|borough|parish|ward|tehsil|taluka|mandal)$", re.I)


def wd_place(d):
    """ "Amritsar, India" from a subject's located-in (P131) and country (P17) labels; administrative areas
    ("Patna district") are left out, keeping the country; "" when Wikidata gives no country."""
    country = first(d, "countryLabel")
    country = country_named(country) or country
    if not country or len(d.get("countryLabel") or []) > 1:
        return ""
    town = first(d, "placeLabel")
    return place_name("" if ADMIN_WORDS.search(town) else town, country)


THE_BEFORE = re.compile(r"\b(of|de la|del)\b|(Tower|Bridge|Palace|Gate|Wall|Monument|Memorial|Pyramids?|Colosseum|"
                        r"Pantheon|Parthenon|Kremlin|Acropolis|Alhambra|Opera House|Museum|Building|Mosque|Temple|"
                        r"Stadium|Lighthouse|Fountain|Arch|Statue|Shrine|Pagoda|Stupa|Synagogue|Fort|Fortress)$")


def named(label):
    """A place's name as said after "This is": "the Eiffel Tower", "the Temple of Heaven", "Harmandir Sahib"."""
    if label.lower().startswith("the ") or "'s " in label or label[:1].islower():
        return label
    return "the " + label if THE_BEFORE.search(label) else label


THE_FAITH = re.compile(r"\b(Church|Communion|Patriarchate|Federation|Union|Assembly|Fellowship|Congregation|"
                       r"Orthodoxy|Bahá'í Faith)\b")


def faith_words(faith):
    """A faith as said after "of": "Sikhism", "the Catholic Church", "the Bahá'í Faith"."""
    return ("the " + faith) if THE_FAITH.search(faith) and not faith.lower().startswith("the ") else faith


# ----------------------------------------------------------------- Wikimedia Commons: pictures of a subject

def category_titles(s, category, most=200, deeper=0, rng=None, models_ok=False):
    """Up to most file titles directly in a Commons category (one request) and, with deeper, in that many of its
    subcategories; drawings, maps, logos and scale models are left out (by their titles)."""
    def members(name, kind, count):
        data = commons_get(s, {"action": "query", "list": "categorymembers", "cmtitle": f"Category:{name}",
                               "cmtype": kind, "cmlimit": min(500, count)})
        return [m["title"] for m in (data.get("query") or {}).get("categorymembers", [])]

    category = category.split(":", 1)[-1] if category.lower().startswith("category:") else category
    titles = members(category, "file", most)
    if deeper and len(titles) < most:
        subs = [c for c in members(category, "subcat", 100) if not NOT_A_PHOTO.search(c)
                and (models_ok or not NOT_A_MODEL.search(c))]
        (rng or random.Random(category)).shuffle(subs)
        for sub in subs[:deeper]:
            titles += members(sub.split(":", 1)[-1], "file", max(20, most // deeper))
    return [t for t in dict.fromkeys(titles) if not NOT_A_PHOTO.search(t) and (models_ok or not NOT_A_MODEL.search(t))]


def from_subjects(key, s, chosen, limit, rows_of, per_subject=3, rng=None, deeper=0, models_ok=False):
    """The pack entries of a list of subjects (Wikidata items or Commons categories), each a dict with "label", an
    optional Wikidata "image" (a picture address) and "cat" (Commons category names). For each subject in turn: its
    Wikidata picture first, then a random pick from its category, the free ones only (commons_entries: CC0, public
    domain or CC BY), at most per_subject pictures. rows_of(subject, title, text) gives the rows of one picture
    ([] to leave it out); the file's caption is added as "Describe this picture." and the camera's country as the
    place where the rows give none; rows naming a child are marked. Titles are checked 50 at a time."""
    rng = rng or random.Random(sum(map(ord, key)))
    items, seen, queue = [], set(), []

    def flush():
        """Check the queued titles' licences and turn the free ones into items."""
        got = {}
        for title, url, credit, text in commons_entries(s, [t for t, _ in queue]):
            got[title] = (url, credit, text)
        counts = {}
        for title, subject in queue:
            if title not in got or title in seen or counts.get(subject["label"], 0) >= per_subject:
                continue
            url, credit, text = got[title]
            if NOT_SHOWN_TEXT.search(text) or (not models_ok and NOT_A_MODEL.search(text)):
                continue                           # its caption says it is a coin, stamp, drawing or model
            rows = rows_of(subject, title, text)
            if not rows:
                continue
            seen.add(title)
            counts[subject["label"]] = counts.get(subject["label"], 0) + 1
            extra = caption_row(text, title)
            rows = rows + ([extra] if extra else [])
            place = commons_place(title)
            rows = [dict(r, credit=credit, **({} if r.get("place") else place)) for r in rows]
            if is_child(title, text, subject["label"]):
                rows = [dict(r, child=True) for r in rows]
            items.append((safe_name(key.split("_")[-1], title), url, rows))
        queue.clear()

    for subject in chosen:
        if len(items) >= limit * 1.25:
            break
        titles = [file_of(first(subject, "image"))] if first(subject, "image") else []
        for category in subject.get("cat") or []:
            found = category_titles(s, category, 150, deeper, rng, models_ok)
            rng.shuffle(found)
            titles += found[:per_subject * 3]
        for title in dict.fromkeys(t for t in titles if t and t not in seen):
            queue.append((title, subject))
        if len(queue) >= 45:
            flush()
    if queue:
        flush()
    say(f"{key}: {len(items)} free pictures of {len({r[0]['answer'] for _, _, r in items})} subjects")
    return finish(key, items, limit, workers=3, pause=0.3)


def round_robin(groups, rng):
    """The subjects of several groups taken in turn (each group shuffled), so every group gets in."""
    queues = [list(g) for g in groups]
    for q in queues:
        rng.shuffle(q)
    out = []
    while any(queues):
        for q in queues:
            if q:
                out.append(q.pop())
    return out


# ----------------------------------------------------------------- Open Images V7: sports, music, vehicles, toys

OI_ASK = {"sport": ASK_SPORT, "equipment": "What sports equipment is in this picture?",
          "ground": "What kind of place is this?", "instrument": "What musical instrument is in this picture?",
          "vehicle": "What vehicles are in this picture?", "toy": "What toys or games are in this picture?",
          "building": "What kind of building or structure is this?", "worship": "What kind of place of worship is this?"}
# Each label with its group and the words used in the answer.
OI_CULTURE = {
    # sports (the activity people checked is happening)
    "Boxing": ("sport", "boxing"), "Fencing": ("sport", "fencing"), "Swimming": ("sport", "swimming"),
    "Cricket (Sport)": ("sport", "cricket"), "Basketball (Sport)": ("sport", "basketball"),
    "Badminton": ("sport", "badminton"), "Volleyball (Sport)": ("sport", "volleyball"),
    "Track and field athletics": ("sport", "track and field athletics"), "Arm wrestling": ("sport", "arm wrestling"),
    "Diving": ("sport", "diving"), "Kitesurfing": ("sport", "kitesurfing"), "Archery": ("sport", "archery"),
    "Bowling": ("sport", "bowling"), "Billiards": ("sport", "billiards"), "Curling": ("sport", "curling"),
    "Figure skating": ("sport", "figure skating"), "Alpine skiing": ("sport", "alpine skiing"),
    "Rowing": ("sport", "rowing"), "Surfing": ("sport", "surfing"), "Skateboarding": ("sport", "skateboarding"),
    "Golf": ("sport", "golf"), "Tennis": ("sport", "tennis"), "Rugby": ("sport", "rugby"),
    "American football": ("sport", "American football"), "Ice hockey": ("sport", "ice hockey"),
    "Baseball (sport)": ("sport", "baseball"), "Climbing": ("sport", "climbing"), "Cycling": ("sport", "cycling"),
    "Equestrianism": ("sport", "equestrian sport (horse riding)"), "Horse racing": ("sport", "horse racing"),
    "Sumo": ("sport", "sumo wrestling"), "Judo": ("sport", "judo"), "Karate": ("sport", "karate"),
    "Taekwondo": ("sport", "taekwondo"), "Gymnastics": ("sport", "gymnastics"), "Darts": ("sport", "darts"),
    # sports equipment
    "Tennis racket": ("equipment", "a tennis racket"), "Table tennis racket": ("equipment", "a table tennis bat"),
    "Baseball bat": ("equipment", "a baseball bat"), "Baseball glove": ("equipment", "a baseball glove"),
    "Rugby ball": ("equipment", "a rugby ball"), "Golf ball": ("equipment", "a golf ball"),
    "Tennis ball": ("equipment", "a tennis ball"), "Volleyball (Ball)": ("equipment", "a volleyball"),
    "Football": ("equipment", "a football"), "Hockey stick": ("equipment", "a hockey stick"),
    "Ski": ("equipment", "skis"), "Snowboard": ("equipment", "a snowboard"), "Surfboard": ("equipment", "a surfboard"),
    "Skateboard": ("equipment", "a skateboard"), "Roller skates": ("equipment", "roller skates"),
    "Ice skate": ("equipment", "ice skates"), "Bowling pin": ("equipment", "bowling pins"),
    "Bowling ball": ("equipment", "a bowling ball"), "Billiard ball": ("equipment", "billiard balls"),
    "Paddle": ("equipment", "a paddle"), "Swim cap": ("equipment", "a swimming cap"),
    "Ski pole": ("equipment", "ski poles"), "Cricket ball": ("equipment", "a cricket ball"),
    "Boxing glove": ("equipment", "boxing gloves"), "Dartboard": ("equipment", "a dartboard"),
    # sports places
    "Stadium": ("ground", "a stadium"), "Boxing ring": ("ground", "a boxing ring"), "Race track": ("ground", "a race track"),
    "Skatepark": ("ground", "a skatepark"), "Billiard table": ("ground", "a billiard table"),
    "Scoreboard": ("ground", "a scoreboard"), "Basketball court": ("ground", "a basketball court"),
    "Baseball field": ("ground", "a baseball field"), "Golf course": ("ground", "a golf course"),
    # musical instruments
    "Grand piano": ("instrument", "a grand piano"), "Piano": ("instrument", "a piano"),
    "Musical keyboard": ("instrument", "an electronic keyboard"), "Guitar": ("instrument", "a guitar"),
    "Saxophone": ("instrument", "a saxophone"), "Violin": ("instrument", "a violin"),
    "Drums (Music)": ("instrument", "a drum kit"), "Harpsichord": ("instrument", "a harpsichord"),
    "Cello": ("instrument", "a cello"), "Flute": ("instrument", "a flute"), "Oboe": ("instrument", "an oboe"),
    "Banjo": ("instrument", "a banjo"), "Accordion": ("instrument", "an accordion"), "Snare drum": ("instrument", "a snare drum"),
    "Drum": ("instrument", "a drum"), "Trumpet": ("instrument", "a trumpet"), "Cymbal": ("instrument", "a cymbal"),
    "Harp": ("instrument", "a harp"), "Bagpipes": ("instrument", "bagpipes"), "Trombone": ("instrument", "a trombone"),
    "Clarinet": ("instrument", "a clarinet"), "Xylophone": ("instrument", "a xylophone"),
    "Harmonica": ("instrument", "a harmonica"), "Sheet music": ("instrument", "sheet music"),
    "French horn": ("instrument", "a French horn"), "Tuba": ("instrument", "a tuba"),
    # vehicles
    "Sports car": ("vehicle", "a sports car"), "Limousine": ("vehicle", "a limousine"), "Taxi": ("vehicle", "a taxi"),
    "Convertible": ("vehicle", "a convertible"), "Jeep": ("vehicle", "a jeep"), "Pickup truck": ("vehicle", "a pickup truck"),
    "Ambulance": ("vehicle", "an ambulance"), "Police car": ("vehicle", "a police car"),
    "Fire apparatus": ("vehicle", "a fire engine"), "Car": ("vehicle", "a car"), "Van": ("vehicle", "a van"),
    "Truck": ("vehicle", "a lorry (truck)"), "Bus": ("vehicle", "a bus"), "Tram": ("vehicle", "a tram"),
    "Locomotive": ("vehicle", "a locomotive"), "Train": ("vehicle", "a train"), "Motorcycle": ("vehicle", "a motorbike"),
    "Scooter": ("vehicle", "a scooter"), "Kick scooter": ("vehicle", "a kick scooter"), "Bicycle": ("vehicle", "a bicycle"),
    "Tricycle": ("vehicle", "a tricycle"), "Unicycle": ("vehicle", "a unicycle"), "Rickshaw": ("vehicle", "a rickshaw"),
    "Segway": ("vehicle", "a Segway"), "Tractor": ("vehicle", "a tractor"), "Snowmobile": ("vehicle", "a snowmobile"),
    "Sailboat": ("vehicle", "a sailing boat"), "Canoe": ("vehicle", "a canoe"), "Kayak": ("vehicle", "a kayak"),
    "Gondola": ("vehicle", "a gondola"), "Jet ski": ("vehicle", "a jet ski"), "Ship": ("vehicle", "a ship"),
    "Boat": ("vehicle", "a boat"), "Helicopter": ("vehicle", "a helicopter"), "Airplane": ("vehicle", "an airplane"),
    "Hot air balloon": ("vehicle", "a hot-air balloon"),
    # toys and games
    "Chess": ("toy", "a game of chess"), "Chessboard": ("toy", "a chessboard"), "Dice": ("toy", "dice"),
    "Playing card": ("toy", "playing cards"), "Rubik's cube": ("toy", "a Rubik's Cube"), "Doll": ("toy", "a doll"),
    "Teddy bear": ("toy", "a teddy bear"), "Stuffed toy": ("toy", "a soft toy"), "Kite": ("toy", "a kite"),
    "Top (Toy)": ("toy", "a spinning top"), "Toy block": ("toy", "toy building blocks"),
    "Game controller": ("toy", "a game controller"), "Joystick": ("toy", "a joystick"),
    "Video game console": ("toy", "a games console"), "Board game": ("toy", "a board game"),
    "Puzzle": ("toy", "a puzzle"), "Flying disc": ("toy", "a flying disc (frisbee)"), "Balloon": ("toy", "balloons"),
    "Toy": ("toy", "a toy"),
    # buildings and places of worship
    "Cathedral": ("worship", "a cathedral, a Christian church"), "Church": ("worship", "a church, a Christian place "
                                                                          "of worship"),
    "Mosque": ("worship", "a mosque, an Islamic place of worship"), "Temple": ("worship", "a temple"),
    "Shrine": ("worship", "a shrine"), "Synagogue": ("worship", "a synagogue, a Jewish place of worship"),
    "Castle": ("building", "a castle"), "Lighthouse": ("building", "a lighthouse"), "Skyscraper": ("building", "a skyscraper"),
    "Tower": ("building", "a tower"), "Bridge (structure)": ("building", "a bridge"), "Monument": ("building", "a monument"),
    "Statue": ("building", "a statue"), "Fortification": ("building", "a fortification"),
    "Fountain": ("building", "a fountain"), "Arch": ("building", "an arch"), "Dome (Architecture)": ("building", "a dome"),
    "Hut": ("building", "a hut"), "Palace": ("building", "a palace"), "Pyramid": ("building", "a pyramid"),
}
# A general label left out when a more specific one is there ("a sports car", not "a sports car and a car").
OI_COVERED = {"Car": {"Sports car", "Limousine", "Taxi", "Convertible", "Jeep", "Police car", "Ambulance"},
              "Piano": {"Grand piano"}, "Drum": {"Snare drum", "Drums (Music)"}, "Train": {"Locomotive"},
              "Boat": {"Sailboat", "Canoe", "Kayak", "Gondola", "Jet ski"}, "Truck": {"Pickup truck", "Fire apparatus"},
              "Chessboard": {"Chess"}, "Toy": {"Doll", "Teddy bear", "Stuffed toy", "Kite", "Top (Toy)", "Toy block",
                                               "Rubik's cube", "Dice"},
              "Church": {"Cathedral"}, "Stuffed toy": {"Teddy bear"}, "Scooter": {"Kick scooter"}}
# Labels too common to choose a picture by on their own (they come into an answer only beside a rarer label).
OI_COMMON = {"Car", "Boat", "Bicycle", "Van", "Truck", "Ship", "Airplane", "Toy", "Balloon", "Statue", "Fountain",
             "Tower", "Bridge (structure)", "Arch"}
OI_ROW_ORDER = ("sport", "equipment", "ground", "instrument", "worship", "building", "vehicle", "toy")


def oi_culture_rows(present):
    """The rows of one picture from its verified-present labels: one row per group present, naming every label of
    that group (general ones left out where a specific one is there)."""
    rows = []
    for group in OI_ROW_ORDER:
        names = [n for n in OI_CULTURE if n in present and OI_CULTURE[n][0] == group
                 and not (OI_COVERED.get(n, set()) & present)]
        words = list(dict.fromkeys(OI_CULTURE[n][1] for n in names))
        if not words:
            continue
        if group == "sport":
            answer = f"This is {listed(words)}."
        elif group in ("ground", "building", "worship"):
            answer = f"This is {words[0]}." if len(words) == 1 else f"It shows {listed(words)}."
        else:
            answer = f"It shows {listed(words[:6])}{' and more' if len(words) > 6 else ''}."
        rows.append({"question": OI_ASK[group], "answer": answer})
    return rows


def build_open_images_culture(limit):
    """The Open Images culture pack: reads the labels people checked on the validation and test sets, keeps photos
    whose own licence is free, that need no turning and that have a verified label of OI_CULTURE (not only a
    common one), takes the labels in turn (rarest first, so every sport, instrument and vehicle gets in) and
    fetches the photos."""
    s, rng = session(), random.Random(81)
    mids = {}
    for line in csv.reader(oi_lines(s, OI_CLASSES)):
        if len(line) == 2:
            mids.setdefault(line[1], line[0])
    wanted = set(OI_CULTURE) | set(OI_CHILD)
    names = {mids[n]: n for n in wanted if n in mids}
    say(f"Open Images: {len(names)} of {len(wanted)} labels found in the class list")
    labels = {}
    for url in OI_LABELS:
        for cells in csv.reader(oi_lines(s, url)):
            if len(cells) == 4 and cells[2] in names:
                try:
                    confidence = round(float(cells[3]))
                except ValueError:
                    continue
                picture = labels.setdefault(cells[0], {})
                name = names[cells[2]]
                picture[name] = confidence if picture.get(name, confidence) == confidence else None
    keep = {k for k, v in labels.items() if any(c == 1 and n in OI_CULTURE and n not in OI_COMMON
                                                 for n, c in v.items())}
    say(f"Open Images: {len(keep)} pictures with a sport, instrument, vehicle, toy or building label verified")
    photos = {}
    for url in OI_IMAGES:
        for r in csv.DictReader(oi_lines(s, url)):
            licence = oi_licence_name(r.get("License") or "")
            if r["ImageID"] in keep and licence and (r.get("Rotation") or "0") in ("0", "0.0", ""):
                photos[r["ImageID"]] = (r["Subset"], licence, clean(r.get("Author")) or "an unnamed photographer",
                                        r.get("OriginalLandingURL") or "")
    mains = {}
    for image_id in sorted(photos):
        present = {n for n, c in labels[image_id].items() if c == 1}
        mains[image_id] = [n for n in OI_CULTURE if n in present and n not in OI_COMMON]
    totals = {}
    for main in mains.values():
        for n in main:
            totals[n] = totals.get(n, 0) + 1
    by_label = {}
    for image_id, main in mains.items():
        if main:                                   # each photo under its rarest label
            by_label.setdefault(min(main, key=lambda n: totals[n]), []).append(image_id)
    counts = {n: len(v) for n, v in by_label.items()}
    order = sorted(by_label, key=lambda n: counts[n])          # the rarest labels first
    for ids in by_label.values():
        rng.shuffle(ids)
    chosen, want = [], int(limit * 1.1) + 2
    while len(chosen) < want and any(by_label.values()):
        for n in order:
            if by_label[n] and len(chosen) < want:
                chosen.append(by_label[n].pop())
    items = []
    for image_id in chosen:
        present = {n for n, c in labels[image_id].items() if c == 1}
        rows = oi_culture_rows(present)
        subset, licence, author, page = photos[image_id]
        credit = (f"Photo by {author}" + (f" ({page})" if page else "") + f", {licence}; labels from Open Images V7 "
                  "(Google), CC BY 4.0")
        child = bool(present & set(OI_CHILD))
        items.append((f"oi-culture-{image_id}.jpg", OI_PICTURE.format(subset=subset, image_id=image_id),
                      [dict(r, credit=credit, **({"child": True} if child else {})) for r in rows]))
    say(f"Open Images: {len(items)} photos chosen from {len(photos)} free ones ({len(order)} labels)")
    fetched = fetch_all(items, workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Wikidata: sports

DISABILITY_PACK_SPORTS = {"wheelchair basketball", "wheelchair rugby", "wheelchair racing", "wheelchair tennis",
                          "goalball", "blind football", "football 5-a-side"}      # already in disability_packs
GENERIC_KINDS = {"sport", "type of sport", "sports", "physical activity", "activity", "game", "competition",
                 "musical instrument", "artificial object", "object", "instrument", "toy", "vehicle", "class",
                 "concept", "entity", "artificial physical object", "physical object", "product", "item",
                 "sports equipment", "equipment", "architectural element", "architectural style", "style",
                 "first-order class", "second-order class", "type", "musical instrument type"}


def kind_of(d, key="parentLabel"):
    """The most useful kind of a subject from its "subclass of" (or "instance of") labels: the first that is not a
    general word ("a metallophone", not "a musical instrument"), or ""."""
    kinds = [k for k in d.get(key) or [] if k.lower() not in GENERIC_KINDS and not re.match(r"^\d", k)
             and k.lower() != d["label"].lower()]
    return sorted(kinds, key=lambda k: (len(k.split()) > 3, k))[0] if kinds else ""


def origin_words(d):
    """ " from Japan" from a subject's country of origin (P495), or "" (none, or several)."""
    origins = d.get("originLabel") or []
    if len(origins) != 1:
        return ""
    country = country_named(origins[0]) or origins[0]
    return f" from {place_words(country)}"


SPORT_QUERY = """SELECT ?item ?itemLabel ?cat ?parentLabel ?originLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT DISTINCT ?item WHERE { %s ?item wdt:P373 ?c ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) } }
  ?item wdt:P373 ?cat .
  OPTIONAL { ?item wdt:P279 ?parent } OPTIONAL { ?item wdt:P495 ?origin }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


def build_wikidata_sports(limit):
    """The sports pack: sports (instances of sport, type of sport or team sport, and sports that are subclasses of
    those), sports equipment and kinds of sports ground (subclasses of sports venue) with their Commons categories,
    and the Commons scoreboard category, taken in turn."""
    s, rng = session(), random.Random(82)
    sports = subjects(sparql(s, SPORT_QUERY % ("VALUES ?t { wd:Q349 wd:Q31629 wd:Q216048 } "
                                               "{ ?item wdt:P31 ?t } UNION { ?item wdt:P279 ?t }", 2)))
    sports = [d for d in sports if d["label"].lower() not in DISABILITY_PACK_SPORTS]
    for d in sports:
        d["ask"] = ASK_SPORT
    equipment = subjects(sparql(s, SPORT_QUERY % ("?item wdt:P279 wd:Q768186 .", 2)))
    for d in equipment:
        d["ask"] = ASK_EQUIPMENT
    grounds = subjects(sparql(s, SPORT_QUERY % ("?item wdt:P279 wd:Q1076486 .", 2)))
    for d in grounds:
        d["ask"] = ASK_GROUND
    boards = [{"label": "scoreboard", "cat": ["Scoreboards"], "ask": "What is this?"}]
    say(f"Wikidata: {len(sports)} sports, {len(equipment)} kinds of equipment, {len(grounds)} kinds of ground")

    def rows_of(d, title, text):
        """The sport's (equipment's, ground's) row: its name, kind and country of origin."""
        if d["ask"] == ASK_SPORT:
            kind = kind_of(d)
            answer = f"This is {d['label']}" + (f", {a_or_an(kind)} {kind}" if kind else "") + origin_words(d) + "."
        else:
            answer = f"This is {a_or_an(d['label'])} {d['label']}" + origin_words(d) + "."
        return [{"question": d["ask"], "answer": sentence(answer)}]
    chosen = boards + round_robin([sports, equipment, grounds], rng)
    return from_subjects("wikidata_sports", s, chosen, limit, rows_of, per_subject=4, rng=rng, deeper=2)


# ----------------------------------------------------------------- Wikidata: musical instruments

INSTRUMENT_QUERY = """SELECT ?item ?itemLabel ?cat ?parentLabel ?originLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT DISTINCT ?item WHERE { ?item wdt:P279+ wd:Q34379 ; wdt:P373 ?c ; wikibase:sitelinks ?sl .
                                  FILTER(?sl >= 2) } }
  ?item wdt:P373 ?cat .
  OPTIONAL { ?item wdt:P279 ?parent } OPTIONAL { ?item wdt:P495 ?origin }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


# Sound equipment that Wikidata files under "musical instrument" but a describer should not call one.
NOT_INSTRUMENT = re.compile(r"\b(microphones?|loudspeakers?|amplifiers?|headphones?|pickups?|effects? units?|"
                            r"cables?|software|plug-ins?|apps?|mixing consoles?|turntables?|DJ controllers?)\b", re.I)


def build_wikidata_instruments(limit):
    """The instruments pack: every kind of musical instrument on Wikidata with a Commons category (about 1,700),
    shuffled, a few free pictures of each: "This is a saron, a metallophone from Indonesia." """
    s, rng = session(), random.Random(83)
    found = [d for d in subjects(sparql(s, INSTRUMENT_QUERY))
             if not NOT_INSTRUMENT.search(" ".join([d["label"]] + (d.get("parentLabel") or [])))]
    say(f"Wikidata: {len(found)} kinds of musical instrument with a Commons category")
    rng.shuffle(found)

    def rows_of(d, title, text):
        """The instrument's row: its name, kind and country of origin."""
        kind = kind_of(d)
        name = d["label"]
        answer = f"This is {a_or_an(name)} {name}" + (f", {a_or_an(kind)} {kind}" if kind else "") + \
            origin_words(d) + "."
        return [{"question": ASK_INSTRUMENT, "answer": sentence(answer)}]
    return from_subjects("wikidata_instruments", s, found, limit, rows_of, per_subject=4, rng=rng, deeper=1)


# ----------------------------------------------------------------- the Met: musical instruments

MET = "https://collectionapi.metmuseum.org/public/collection/"
MET_INSTRUMENTS = 18                   # the Department of Musical Instruments


def met_kind(classification):
    """ "an aerophone" from the Met's Hornbostel-Sachs class "Aerophone-Whistle Flute" (its main class only: the
    rest joins words with hyphens in ways that cannot be split back reliably), or ""."""
    main = (classification or "").split("-", 1)[0].strip().lower()
    return main if main in ("aerophone", "chordophone", "idiophone", "membranophone", "electrophone") else ""


def met_name(name):
    """An instrument's name in lower case for the middle of a sentence ("Tenor Valve Trombone in B-flat" -> "tenor
    valve trombone in B-flat"), keeping words written in capitals or with a capital after a hyphen."""
    return " ".join(w if w.isupper() or re.search(r"-[A-Z]|^[A-Z]-", w) else w.lower() for w in name.split())


def met_rows(obj):
    """The rows of one Met instrument: "What instrument is this?" (name, kind, culture, country, date) and "Tell me
    about this museum object." (the same with its maker and materials)."""
    name = clean(obj.get("objectName")) or clean(obj.get("title"))
    if not name:
        return []
    kind = met_kind(obj.get("classification"))
    culture, country = clean(obj.get("culture")), clean(obj.get("country"))
    country = country_named(country) or country
    date = clean(obj.get("objectDate"))
    lower = met_name(name)
    first_part = f"This is {a_or_an(lower)} {lower}" + (f" ({a_or_an(kind)} {kind})" if kind else "")
    bits = [b for b in (culture, f"from {place_words(country)}" if country else "", date) if b]
    answer = sentence(first_part + (", " + ", ".join(bits) if bits else ""))
    rows = [{"question": ASK_INSTRUMENT, "answer": answer}]
    title, maker, medium = clean(obj.get("title")), clean(obj.get("artistDisplayName")), clean(obj.get("medium"))
    more = [answer]
    if title and title.lower() != name.lower():
        more.insert(0, sentence(f"{title}"))
    if maker:
        more.append(sentence(f"Made by {maker}"))
    if medium:
        more.append(sentence(f"Made of {medium[0].lower() + medium[1:]}"))
    if len(more) > 1:
        rows.append({"question": MUSEUM, "answer": " ".join(more)})
    place = where(country, "origin") if country else {}
    return [dict(r, **place) for r in rows]


def build_met_instruments(limit):
    """The Met instruments pack: the department's objects with pictures (the paged v1.1 search), each object's
    record read (public domain ones only, CC0), its large web picture fetched."""
    s, rng = session(), random.Random(84)
    ids, offset = [], 0
    while True:
        page = s.get(MET + "v1.1/search", timeout=60, params={"departmentId": MET_INSTRUMENTS, "hasImages": "true",
                                                              "q": "*", "offset": offset, "limit": 100}).json()
        got = page.get("objectIDs") or []
        ids += got
        offset += len(got)
        if not got or offset >= page.get("total", 0):
            break
        time.sleep(0.2)
    rng.shuffle(ids)
    say(f"The Met: {len(ids)} musical instruments with pictures")
    items = []
    for object_id in ids:
        if len(items) >= limit * 1.15 + 2:
            break
        time.sleep(0.05)
        try:
            obj = s.get(f"{MET}v1/objects/{object_id}", timeout=30).json()
        except Exception:  # noqa: BLE001 - left out
            continue
        picture = obj.get("primaryImageSmall") or obj.get("primaryImage")
        if not obj.get("isPublicDomain") or not picture:
            continue
        rows = met_rows(obj)
        if not rows:
            continue
        credit = (f"{clean(obj.get('title'))}, The Metropolitan Museum of Art, {clean(obj.get('creditLine'))}, "
                  f"CC0 (Open Access), {obj.get('objectURL') or ''}").replace(", ,", ",")
        items.append((f"met-{object_id}.jpg", picture, [dict(r, credit=credit) for r in rows]))
    say(f"The Met: {len(items)} public-domain instruments")
    fetched = fetch_all(items, workers=4, pause=0.1)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Wikidata: places of worship

# (Wikidata kind, the words used, the kind's own faith where Wikidata gives the place none, or "").
WORSHIP_KINDS = [
    ("Q16970", "church", "Christianity"), ("Q2977", "cathedral", "Christianity"), ("Q108325", "chapel", "Christianity"),
    ("Q163687", "basilica", "Christianity"), ("Q1088552", "Catholic church", "the Catholic Church"),
    ("Q2031836", "Eastern Orthodox church", "the Eastern Orthodox Church"), ("Q32815", "mosque", "Islam"),
    ("Q34627", "synagogue", "Judaism"), ("Q842402", "Hindu temple", "Hinduism"),
    ("Q5393308", "Buddhist temple", "Buddhism"), ("Q427287", "wat (a Buddhist temple)", "Buddhism"),
    ("Q180987", "stupa", "Buddhism"), ("Q199451", "pagoda", ""), ("Q337986", "gurdwara", "Sikhism"),
    ("Q845945", "Shinto shrine", "Shinto"), ("Q2613100", "Jain temple", "Jainism"),
    ("Q1568313", "Bahá'í House of Worship", "the Bahá'í Faith"), ("Q1151612", "Taoist temple", "Taoism"),
    ("Q618618", "temple of Confucius", "Confucianism"), ("Q115278", "fire temple", "Zoroastrianism"),
    ("Q743165", "Kingdom Hall", "Jehovah's Witnesses"), ("Q6807904", "meeting house", ""),
    ("Q44613", "monastery", ""),
]
# The fewest Wikipedia articles a place needs, for the kinds with very many places (the query service would take
# too long to sort them all).
WORSHIP_MIN_ARTICLES = {"Q16970": 8, "Q1088552": 5, "Q108325": 3, "Q2977": 2, "Q44613": 3, "Q2031836": 3, "Q32815": 2}
WORSHIP_QUERY = """SELECT ?item ?itemLabel ?image ?cat ?religionLabel ?countryLabel ?placeLabel ?styleLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT ?item ?sl WHERE { ?item wdt:P31 wd:%s ; wdt:P18 ?i ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P18 ?image .
  OPTIONAL { ?item wdt:P373 ?cat } OPTIONAL { ?item wdt:P140 ?religion } OPTIONAL { ?item wdt:P17 ?country }
  OPTIONAL { ?item wdt:P131 ?place } OPTIONAL { ?item wdt:P149 ?style }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


def style_words(d):
    """ "Gothic Revival" from a subject's style (P149) "Gothic Revival architecture", or "" (none, or several)."""
    styles = d.get("styleLabel") or []
    if len(styles) != 1:
        return ""
    return re.sub(r"\s+(architecture|style)$", "", styles[0], flags=re.I)


def worship_rows(d, title, text):
    """The rows of one picture of a place of worship: its name, kind, place and faith; where it is; its style."""
    faiths = sorted(d.get("religionLabel") or [], key=len, reverse=True)
    faith = faiths[0] if faiths else d["default_faith"]
    place = wd_place(d)
    inside = INSIDE.search(f"{title} {text}")
    name = named(d["label"])
    answer = (f"This is the inside of {name}" if inside else f"This is {name}") + \
        f", {a_or_an(d['kind'])} {d['kind']}" + (f" in {place}" if place else "") + \
        (f", a place of worship of {faith_words(faith)}" if faith else "") + "."
    rows = [{"question": ASK_WORSHIP, "answer": sentence(answer), **where(place)}]
    if place:
        rows.append({"question": ASK_WHERE, "answer": f"It was taken at {name} in {place_words(place)}.",
                     **where(place)})
    style = style_words(d)
    if style and not inside:
        rows.append({"question": ASK_STYLE, "answer": f"It is built in the {style} style.", **where(place)})
    return rows


def build_wikidata_worship(limit):
    """The places of worship pack: for each kind (WORSHIP_KINDS), the best-known places with a picture on Wikidata
    (most Wikipedia articles first), the kinds taken in turn so every faith gets in."""
    s, rng = session(), random.Random(85)
    per_kind = max(20, int(limit * 1.2 / len(WORSHIP_KINDS)))
    groups = []
    for qid, kind, faith in WORSHIP_KINDS:
        found = subjects(sparql(s, WORSHIP_QUERY % (qid, WORSHIP_MIN_ARTICLES.get(qid, 1), per_kind)))
        for d in found:
            d["kind"], d["default_faith"] = kind, faith
        say(f"Wikidata: {len(found)} {kind} places with a picture")
        groups.append(found)
        time.sleep(1)
    chosen = round_robin(groups, rng)
    return from_subjects("wikidata_worship", s, chosen, limit, worship_rows, per_subject=3, rng=rng)


# ----------------------------------------------------------------- Commons: religious life

FESTIVAL_Q = "What festival or religious occasion does this picture show?"
OBJECT_Q = "What religious object is this?"
WHAT_Q = "What is this?"
# Commons category (or several, the first ones that exist are used) -> (question, answer).
RELIGIOUS_LIFE = {
    ("Dipavali", "Diwali"): (FESTIVAL_Q, "It shows Diwali (Deepavali), the festival of lights of Hindus, Jains and "
                                         "Sikhs."),
    ("Holi",): (FESTIVAL_Q, "It shows Holi, the Hindu spring festival of colours."),
    ("Eid al-Fitr",): (FESTIVAL_Q, "It shows Eid al-Fitr, the Muslim festival at the end of Ramadan."),
    ("Eid al-Adha",): (FESTIVAL_Q, "It shows Eid al-Adha, the Muslim festival of the sacrifice."),
    ("Ramadan",): (FESTIVAL_Q, "It shows Ramadan, the Muslim month of fasting."),
    ("Iftar",): (FESTIVAL_Q, "It shows an iftar, the evening meal at which Muslims break their fast in Ramadan."),
    ("Nativity scenes",): (FESTIVAL_Q, "It shows a nativity scene, the birth of Jesus, set up by Christians at "
                                       "Christmas."),
    ("Hanukkah",): (FESTIVAL_Q, "It shows Hanukkah, the Jewish festival of lights."),
    ("Passover Seder",): (FESTIVAL_Q, "It shows a Passover Seder, the Jewish ritual meal of Passover."),
    ("Sukkot",): (FESTIVAL_Q, "It shows Sukkot, the Jewish festival of booths."),
    ("Purim",): (FESTIVAL_Q, "It shows Purim, a Jewish festival."),
    ("Vesak",): (FESTIVAL_Q, "It shows Vesak, the Buddhist festival of the Buddha's birth, enlightenment and death."),
    ("Vaisakhi",): (FESTIVAL_Q, "It shows Vaisakhi, the Sikh and Punjabi spring festival."),
    ("Navaratri",): (FESTIVAL_Q, "It shows Navaratri, a Hindu festival of nine nights."),
    ("Durga Puja",): (FESTIVAL_Q, "It shows Durga Puja, the Hindu festival of the goddess Durga."),
    ("Ganesh Chaturthi",): (FESTIVAL_Q, "It shows Ganesh Chaturthi, the Hindu festival of the god Ganesha."),
    ("Thaipusam",): (FESTIVAL_Q, "It shows Thaipusam, a Tamil Hindu festival of the god Murugan."),
    ("Losar",): (FESTIVAL_Q, "It shows Losar, the Tibetan Buddhist New Year."),
    ("Bon Festival",): (FESTIVAL_Q, "It shows Obon, the Japanese Buddhist festival honouring ancestors."),
    ("Timkat",): (FESTIVAL_Q, "It shows Timkat, the Ethiopian Orthodox festival of Epiphany."),
    ("Corpus Christi processions",): (FESTIVAL_Q, "It shows a Corpus Christi procession, a Catholic feast."),
    ("Holy Week processions",): (FESTIVAL_Q, "It shows a Holy Week procession, before the Christian feast of "
                                             "Easter."),
    ("Hajj",): (FESTIVAL_Q, "It shows the Hajj, the Muslim pilgrimage to Mecca."),
    ("Kumbh Mela",): (FESTIVAL_Q, "It shows the Kumbh Mela, a Hindu pilgrimage and festival of bathing in a sacred "
                                  "river."),
    ("Altars",): (WHAT_Q, "This is an altar, where offerings or worship take place."),
    ("Mihrabs",): (WHAT_Q, "This is a mihrab, the niche in a mosque's wall that shows the direction of Mecca for "
                           "prayer."),
    ("Minbars",): (WHAT_Q, "This is a minbar, the pulpit in a mosque from which the sermon is given."),
    ("Iconostases",): (WHAT_Q, "This is an iconostasis, the wall of icons in an Eastern Orthodox church."),
    ("Torah arks",): (WHAT_Q, "This is a Torah ark, the cabinet in a synagogue that holds the Torah scrolls."),
    ("Butsudan",): (WHAT_Q, "This is a butsudan, a Buddhist household altar in Japan."),
    ("Kamidana",): (WHAT_Q, "This is a kamidana, a household Shinto shrine."),
    ("Torii",): (WHAT_Q, "This is a torii, the gateway of a Shinto shrine."),
    ("Pulpits",): (WHAT_Q, "This is a pulpit, from which sermons are preached in a church."),
    ("Baptismal fonts",): (WHAT_Q, "This is a baptismal font, used for baptism in a Christian church."),
    ("Prayer wheels",): (OBJECT_Q, "This is a prayer wheel, used in Tibetan Buddhism."),
    ("Prayer flags",): (OBJECT_Q, "These are prayer flags of Tibetan Buddhism."),
    ("Rosaries",): (OBJECT_Q, "This is a rosary, Catholic prayer beads."),
    ("Misbaha",): (OBJECT_Q, "This is a misbaha (tasbih), Muslim prayer beads."),
    ("Japamala", "Japa mala"): (OBJECT_Q, "This is a japamala, prayer beads used by Hindus and Buddhists."),
    ("Tefillin",): (OBJECT_Q, "These are tefillin, small leather boxes with Torah verses that Jewish men wear for "
                              "morning prayer."),
    ("Tallit",): (OBJECT_Q, "This is a tallit, the Jewish prayer shawl."),
    ("Mezuzot",): (OBJECT_Q, "This is a mezuzah, a small case holding a scroll, fixed to the doorpost of a Jewish "
                             "home."),
    ("Menorah (Temple)", "Menorah"): (OBJECT_Q, "This is a menorah, the seven-branched lamp, a symbol of Judaism."),
    ("Hanukkiyot", "Hanukiah"): (OBJECT_Q, "This is a hanukkiah, the nine-branched lamp lit at Hanukkah."),
    ("Prayer rugs",): (OBJECT_Q, "This is a prayer rug, used by Muslims for prayer."),
    ("Torah scrolls",): (OBJECT_Q, "This is a Torah scroll, the handwritten scroll of the Jewish scriptures."),
    ("Crucifixes",): (OBJECT_Q, "This is a crucifix, a cross with the figure of Jesus, a Christian symbol."),
    ("Khanda",): (OBJECT_Q, "This is the khanda, the symbol of Sikhism."),
    ("Thangka", "Thangkas"): (OBJECT_Q, "This is a thangka, a Tibetan Buddhist painting on cloth."),
    ("Diya", "Diyas"): (OBJECT_Q, "These are diyas, small oil lamps lit at Diwali and in Hindu worship."),
    ("Omamori",): (OBJECT_Q, "This is an omamori, a Japanese charm from a shrine or temple."),
    ("Ema (Shinto)",): (OBJECT_Q, "These are ema, wooden prayer plaques hung at a Shinto shrine."),
    ("Cassocks",): ("What religious clothing is this?", "This is a cassock, the long robe worn by Christian clergy."),
    ("Chasubles",): ("What religious clothing is this?", "This is a chasuble, the outer vestment a priest wears to "
                                                         "celebrate Mass."),
    ("Mitres",): ("What religious clothing is this?", "This is a mitre, the tall hat worn by bishops."),
    ("Kippah", "Kippot"): ("What religious clothing is this?", "This is a kippah, the skullcap worn by Jewish men."),
    ("Buddhist monks",): ("Who are these people?", "These are Buddhist monks, in their robes."),
}


def build_commons_religious_life(limit):
    """The religious life pack: the categories of RELIGIOUS_LIFE taken in turn, a few free pictures from each (and
    from two of its subcategories), with the category's fixed sentence and the file's caption."""
    s, rng = session(), random.Random(86)
    chosen = []
    for names, (question, answer) in RELIGIOUS_LIFE.items():
        chosen.append({"label": names[0], "cat": list(names), "ask": question, "say": answer})
    rng.shuffle(chosen)
    per = max(3, -(-int(limit * 1.2) // len(chosen)))
    return from_subjects("commons_religious_life", s, chosen, limit,
                         lambda d, title, text: [{"question": d["ask"], "answer": d["say"]}],
                         per_subject=per, rng=rng, deeper=2)


# ----------------------------------------------------------------- Wikidata: landmarks

LANDMARK_KINDS = [("Q12518", "tower"), ("Q23413", "castle"), ("Q16560", "palace"), ("Q12280", "bridge"),
                  ("Q11303", "skyscraper"), ("Q4989906", "monument"), ("Q39715", "lighthouse"), ("Q179700", "statue"),
                  ("Q162875", "mausoleum"), ("Q153562", "opera house"), ("Q483110", "stadium"),
                  ("Q57821", "fortification"), ("Q839954", "archaeological site")]
NOT_WORSHIP = "FILTER NOT EXISTS { ?item wdt:P31 ?w . VALUES ?w { %s } }" % " ".join(
    f"wd:{q}" for q, _, _ in WORSHIP_KINDS)
LANDMARK_QUERY = """SELECT ?item ?itemLabel ?image ?cat ?kindLabel ?countryLabel ?placeLabel ?styleLabel ?start
                           ?architectLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT ?item ?sl WHERE { %s ?item wdt:P18 ?i ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) %s }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P18 ?image .
  OPTIONAL { ?item wdt:P373 ?cat } OPTIONAL { ?item wdt:P31 ?kind } OPTIONAL { ?item wdt:P17 ?country }
  OPTIONAL { ?item wdt:P131 ?place } OPTIONAL { ?item wdt:P149 ?style } OPTIONAL { ?item wdt:P571 ?start }
  OPTIONAL { ?item wdt:P84 ?architect }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
LANDMARK_KIND_WORDS = {q: w for q, w in LANDMARK_KINDS}


def landmark_rows(d, title, text):
    """The rows of one picture of a landmark: its name, kind, place, year, architect and style; where it is."""
    place = wd_place(d)
    kind = d.get("kind_words") or kind_of(d, "kindLabel")
    kind = "" if kind.lower() in ("world heritage site", "tourist attraction", "building", "structure") else kind
    name = named(d["label"])
    inside = INSIDE.search(f"{title} {text}")
    answer = (f"This is the inside of {name}" if inside else f"This is {name}") + \
        (f", {a_or_an(kind)} {kind}" if kind else "") + (f" in {place}" if place else "") + "."
    starts = sorted({year_of(v) for v in d.get("start") or [] if year_of(v)})
    if len(starts) == 1:
        answer += f" It dates from {starts[0]}."
    architects = d.get("architectLabel") or []
    if len(architects) == 1:
        answer += f" Its architect was {architects[0]}."
    rows = [{"question": ASK_LANDMARK, "answer": answer, **where(place)}]
    if place:
        rows.append({"question": ASK_WHERE, "answer": f"It was taken at {name} in {place_words(place)}.",
                     **where(place)})
    style = style_words(d)
    if style and not inside:
        rows.append({"question": ASK_STYLE, "answer": f"It is built in the {style} style.", **where(place)})
    return rows


def build_wikidata_landmarks(limit):
    """The landmarks pack: World Heritage Sites with a picture (most Wikipedia articles first) and, for each kind of
    LANDMARK_KINDS, the best-known ones (20 or more Wikipedia articles), places of worship left out (they are in
    wikidata_worship); the groups taken in turn."""
    s, rng = session(), random.Random(87)
    per = max(30, int(limit * 1.0 / (len(LANDMARK_KINDS) + 4)))
    groups = [subjects(sparql(s, LANDMARK_QUERY % ("?item wdt:P1435 wd:Q9259 .", 5, NOT_WORSHIP, per * 4)))]
    say(f"Wikidata: {len(groups[0])} World Heritage Sites with a picture")
    for qid, words in LANDMARK_KINDS:
        found = subjects(sparql(s, LANDMARK_QUERY % (f"?item wdt:P31 wd:{qid} .", 20, NOT_WORSHIP, per)))
        for d in found:
            d["kind_words"] = words
        say(f"Wikidata: {len(found)} well-known {words} landmarks")
        groups.append(found)
        time.sleep(1)
    chosen = round_robin([groups[0]] * 3 + groups[1:], rng)
    chosen = list({d["id"]: d for d in chosen}.values())
    return from_subjects("wikidata_landmarks", s, chosen, limit, landmark_rows, per_subject=3, rng=rng)


# ----------------------------------------------------------------- Wikidata: architectural styles and building parts

ARCH_QUERY = """SELECT ?item ?itemLabel ?cat ?originLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT DISTINCT ?item WHERE { %s ?item wdt:P373 ?c ; wikibase:sitelinks ?sl . FILTER(?sl >= 3) } }
  ?item wdt:P373 ?cat . OPTIONAL { ?item wdt:P495 ?origin }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""


def build_wikidata_architecture(limit):
    """The architecture pack: architectural styles (instances of architectural style) and building parts (instances
    and subclasses of architectural element), each with free pictures from its Commons category and two of its
    subcategories."""
    s, rng = session(), random.Random(88)
    styles = subjects(sparql(s, ARCH_QUERY % "?item wdt:P31 wd:Q32880 ."))
    parts = subjects(sparql(s, ARCH_QUERY % "VALUES ?t { wd:Q391414 } { ?item wdt:P31 ?t } UNION "
                                            "{ ?item wdt:P279 ?t }"))
    say(f"Wikidata: {len(styles)} architectural styles, {len(parts)} building parts")
    for d in styles:
        d["is_style"] = True

    def rows_of(d, title, text):
        """The style's or part's row."""
        if d.get("is_style"):
            style = re.sub(r"\s+(architecture|style)$", "", d["label"], flags=re.I)
            return [{"question": "What architectural style is this?", "answer":
                     sentence(f"This is {style} architecture" + origin_words(d))}]
        return [{"question": "What part of a building is this?",
                 "answer": sentence(f"This is {a_or_an(d['label'])} {d['label']}")}]
    chosen = round_robin([styles, parts], rng)
    return from_subjects("wikidata_architecture", s, chosen, limit, rows_of, per_subject=3, rng=rng, deeper=2)


# ----------------------------------------------------------------- Google Landmarks Dataset v2

GLD = "https://s3.amazonaws.com/google-landmark/metadata/"
GLD_NOT_FREE = re.compile(r"\b(SA|NC|ND|GFDL|FAL|share ?alike|non-?commercial|no ?deriv)", re.I)
GLD_FREE = re.compile(r"^\s*(cc0|cc-zero|public domain|pd\b|pd-|cc[ -]by[ -]\d|cc[ -]by\b|attribution)", re.I)


def gld_rows(s, url):
    """The rows of a large Google Landmarks CSV file, read as it downloads. Lines are split at newline bytes only
    (requests' iter_lines also splits at Unicode line separators, which some Commons titles contain, and that put
    the address and licence files out of step)."""
    def lines():
        """The file's lines, decoded."""
        with s.get(url, timeout=600, stream=True) as r:
            r.raise_for_status()
            rest = b""
            for chunk in r.iter_content(1 << 20):
                rest += chunk
                *done, rest = rest.split(b"\n")
                for line in done:
                    yield line.decode("utf-8", "replace").rstrip("\r")
            if rest:
                yield rest.decode("utf-8", "replace")
    return csv.reader(lines())


def gld_names(s):
    """{landmark id: its name} from the Commons category addresses of train_label_to_category.csv."""
    out = {}
    for row in gld_rows(s, GLD + "train_label_to_category.csv"):
        if len(row) == 2 and row[0].isdigit():
            name = clean(urllib.parse.unquote(row[1].rsplit("Category:", 1)[-1]).replace("_", " "))
            out[row[0]] = re.sub(r"\s*\(([^()]+)\)$", r", \1", name)     # "X (Bologna)" -> "X, Bologna"
    return out


def gld_licence(text):
    """ "CC BY 3.0", "CC0" or "public domain" from an attribution licence field ("CC BY 3.0(http://...)"), or ""
    when it is not free (share-alike, GFDL, non-commercial)."""
    name = re.sub(r"\(https?://[^)]*\)", "", text or "").strip()
    if not name or GLD_NOT_FREE.search(name) or not GLD_FREE.match(name):
        return ""
    return name.replace("CC-BY-", "CC BY ").replace("-", " ") if name.upper().startswith("CC-BY") else name


def build_gldv2_landmarks(limit, per_landmark=2):
    """The Google Landmarks pack: the "clean" training images (train_clean.csv, 27 MB), read with their addresses
    (train.csv) and licences (train_attribution.csv) row by row as they download (the two files are in the same
    order), the free ones only, at most per_landmark a landmark; pictures from Commons at 1,280 pixels."""
    s, rng = session(), random.Random(89)
    clean_ids = {}
    for row in gld_rows(s, GLD + "train_clean.csv"):
        if len(row) == 2 and row[0].isdigit():
            for image_id in row[1].split():
                clean_ids[image_id] = row[0]
    names = gld_names(s)
    say(f"Google Landmarks v2: {len(clean_ids)} clean images of {len(names)} landmarks")
    items, per, read = [], {}, 0
    want = int(limit * 1.3) + 4
    for a, b in zip(gld_rows(s, GLD + "train.csv"), gld_rows(s, GLD + "train_attribution.csv")):
        read += 1
        if len(a) != 3 or len(b) != 5 or a[0] != b[0] or a[0] not in clean_ids:
            continue
        landmark = clean_ids[a[0]]
        licence, name = gld_licence(b[3]), names.get(landmark, "")
        if not licence or not name or per.get(landmark, 0) >= per_landmark or rng.random() < 0.5:
            continue
        per[landmark] = per.get(landmark, 0) + 1
        file_name = urllib.parse.unquote(a[1].rsplit("/", 1)[-1])
        picture = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(file_name) + \
            "?width=1280"
        credit = (f"{clean(b[4])} by {clean(b[2]) or 'unknown'}, {licence}, "
                  f"{b[1].replace('http://', 'https://')}; Google Landmarks Dataset v2 (Weyand, Araujo, Cao and Sim, "
                  "2020), labels CC BY 4.0")
        row = {"question": "What landmark or place is this?", "answer": sentence(f"This is {named(name)}"),
               "credit": credit}
        items.append((f"gld-{a[0]}.jpg", picture, [row] if not is_child(name, b[4]) else [dict(row, child=True)]))
        if len(items) >= want:
            break
    say(f"Google Landmarks v2: {len(items)} free images chosen ({read} lines read)")
    fetched = fetch_all(items, workers=3, pause=0.3)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Wikidata: vehicle models

# (Wikidata kind, how the query finds it, the question, the words for the kind when Wikidata gives no better one).
VEHICLE_KINDS = [("Q3231690", "?item wdt:P31 wd:Q3231690 .", ASK_CAR, "car"),
                 ("Q23866334", "?item wdt:P31 wd:Q23866334 .", "What motorcycle is this?", "motorcycle"),
                 ("Q23039057", "?item wdt:P31 wd:Q23039057 .", "What bus is this?", "bus"),
                 ("Q43193", "{ ?item wdt:P31 wd:Q43193 } UNION { ?item wdt:P279 wd:Q43193 }", "What truck is this?",
                  "truck"),
                 ("Q3407658", "?item wdt:P31 wd:Q3407658 .", "What tram is this?", "tram"),
                 ("Q19832486", "?item wdt:P31 wd:Q19832486 .", "What locomotive or train is this?", "locomotive"),
                 ("Q25653", "?item wdt:P31 wd:Q25653 .", "What boat is this?", "ferry")]
VEHICLE_QUERY = """SELECT ?item ?itemLabel ?cat ?makerLabel ?parentLabel ?originLabel ?start ?end WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT ?item ?sl WHERE { %s ?item wdt:P373 ?c ; wikibase:sitelinks ?sl . FILTER(?sl >= %d) }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P373 ?cat .
  OPTIONAL { ?item wdt:P176 ?maker } OPTIONAL { ?item wdt:P279 ?parent } OPTIONAL { ?item wdt:P495 ?origin }
  OPTIONAL { ?item wdt:P571|wdt:P580|wdt:P729|wdt:P2754 ?start } OPTIONAL { ?item wdt:P582|wdt:P730 ?end }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
VEHICLE_GENERIC = GENERIC_KINDS | {"car", "automobile", "motor car", "motorcycle", "bus", "truck", "tram",
                                   "locomotive", "vehicle model", "car model", "motor vehicle", "road vehicle"}


def vehicle_rows(d, title, text):
    """The row of one vehicle picture: the model, its kind, maker, country and years, as Wikidata gives them."""
    if INSIDE.search(title) or re.search(r"\b(engine|dashboard|cockpit|badge|emblem|wheel|seats?)\b", title, re.I):
        return []                                  # details, not the vehicle seen whole
    kinds = [k for k in d.get("parentLabel") or [] if k.lower() not in VEHICLE_GENERIC and not re.match(r"^\d", k)]
    kind = sorted(kinds, key=len)[0] if kinds else d["default_kind"]
    makers = d.get("makerLabel") or []
    by = f" made by {makers[0]}" if len(makers) == 1 else ""
    name = d["label"] if d["default_kind"] != "ferry" else named(d["label"])
    article_name = name if d["default_kind"] == "ferry" or name.startswith("the ") else f"{a_or_an(name)} {name}"
    answer = f"This is {article_name}, {a_or_an(kind)} {kind}{by}" + origin_words(d) + "."
    starts = sorted({year_of(v) for v in d.get("start") or [] if year_of(v)})
    ends = sorted({year_of(v) for v in d.get("end") or [] if year_of(v)})
    if starts and ends and len(ends) == 1:
        answer += f" It was made from {starts[0]} to {ends[0]}."
    elif starts:
        answer += f" It was first made in {starts[0]}." if d["default_kind"] != "ferry" else \
            f" It dates from {starts[0]}."
    return [{"question": d["ask"], "answer": answer}]


def build_wikidata_vehicle_models(limit):
    """The vehicle models pack: for each kind of VEHICLE_KINDS, the models with most Wikipedia articles (car models
    take half the pack), a few free pictures from each model's Commons category (details, interiors and scale
    models left out)."""
    s, rng = session(), random.Random(90)
    groups = []
    for qid, finder, question, words in VEHICLE_KINDS:
        share = 0.5 if qid == "Q3231690" else 0.5 / (len(VEHICLE_KINDS) - 1)
        found = subjects(sparql(s, VEHICLE_QUERY % (finder, 3, max(20, int(limit * share * 0.8)))))
        for d in found:
            d["ask"], d["default_kind"] = question, words
        say(f"Wikidata: {len(found)} {words} models")
        groups.append(found)
        time.sleep(1)
    chosen = round_robin([groups[0]] * (len(groups) - 1) + groups[1:], rng)
    chosen = list({d["id"]: d for d in chosen}.values())
    return from_subjects("wikidata_vehicle_models", s, chosen, limit, vehicle_rows, per_subject=3, rng=rng)


# ----------------------------------------------------------------- Commons: kinds of vehicle

VEHICLE_Q = "What vehicle is this?"
VEHICLE_CATEGORIES = {
    ("Taxis in London", "London taxis", "Hackney carriages"): (VEHICLE_Q, "This is a London taxi, a black cab."),
    ("Taxis in New York City", "Taxicabs of New York City"): (VEHICLE_Q, "This is a New York City taxi, a yellow "
                                                                         "cab."),
    ("Taxis in Tokyo",): (VEHICLE_Q, "This is a taxi in Tokyo, Japan."),
    ("Taxis in Mumbai",): (VEHICLE_Q, "This is a taxi in Mumbai, India."),
    ("Taxis in Hong Kong",): (VEHICLE_Q, "This is a taxi in Hong Kong."),
    ("Taxis in Bangkok",): (VEHICLE_Q, "This is a taxi in Bangkok, Thailand."),
    ("Taxis in Mexico City",): (VEHICLE_Q, "This is a taxi in Mexico City, Mexico."),
    ("Taxis in Cairo",): (VEHICLE_Q, "This is a taxi in Cairo, Egypt."),
    ("Taxis in Istanbul",): (VEHICLE_Q, "This is a taxi in Istanbul, Turkey."),
    ("Auto rickshaws in India", "Auto rickshaws"): (VEHICLE_Q, "This is an auto rickshaw, a three-wheeled taxi."),
    ("Tuk-tuks in Thailand",): (VEHICLE_Q, "This is a tuk-tuk, a three-wheeled taxi in Thailand."),
    ("Jeepneys",): (VEHICLE_Q, "This is a jeepney, a shared minibus of the Philippines."),
    ("Matatus",): (VEHICLE_Q, "This is a matatu, a shared minibus of Kenya."),
    ("Dolmuş",): (VEHICLE_Q, "This is a dolmuş, a shared minibus of Turkey."),
    ("Marshrutkas", "Marshrutka"): (VEHICLE_Q, "This is a marshrutka, a shared minibus."),
    ("Cycle rickshaws",): (VEHICLE_Q, "This is a cycle rickshaw, a pedal-powered taxi."),
    ("School buses in the United States",): (VEHICLE_Q, "This is a yellow school bus of the United States."),
    ("Double-decker buses in London", "London buses"): (VEHICLE_Q, "This is a London bus."),
    ("Shinkansen",): (VEHICLE_Q, "This is a Shinkansen, a Japanese high-speed train."),
    ("Trams in Melbourne",): (VEHICLE_Q, "This is a tram in Melbourne, Australia."),
    ("Ferries",): (VEHICLE_Q, "This is a ferry."),
    ("Narrowboats",): (VEHICLE_Q, "This is a narrowboat, a canal boat."),
    ("Dhows",): (VEHICLE_Q, "This is a dhow, a traditional sailing boat."),
    ("Gondolas of Venice", "Gondolas in Venice"): (VEHICLE_Q, "This is a gondola in Venice, Italy."),
    ("Tandem bicycles",): (VEHICLE_Q, "This is a tandem bicycle, made for two riders."),
    ("Cargo bicycles", "Cargo bikes"): (VEHICLE_Q, "This is a cargo bicycle."),
    ("Motor scooters",): (VEHICLE_Q, "This is a motor scooter."),
    ("Mopeds",): (VEHICLE_Q, "This is a moped."),
    ("Tractors",): (VEHICLE_Q, "This is a tractor."),
    ("Dump trucks",): (VEHICLE_Q, "This is a dump truck."),
    ("Semi-trailer trucks",): (VEHICLE_Q, "This is an articulated lorry (a semi-trailer truck)."),
    ("Ice cream vans",): (VEHICLE_Q, "This is an ice cream van."),
    ("Food trucks",): (VEHICLE_Q, "This is a food truck."),
    ("Motorhomes",): (VEHICLE_Q, "This is a motorhome."),
    ("Horse-drawn carriages",): (VEHICLE_Q, "This is a horse-drawn carriage."),
    ("Snowmobiles",): (VEHICLE_Q, "This is a snowmobile."),
}


def build_commons_vehicle_kinds(limit):
    """The kinds of vehicle pack: the categories of VEHICLE_CATEGORIES taken in turn, a few free pictures from each
    (and from two subcategories), with the category's fixed sentence and the file's caption."""
    s, rng = session(), random.Random(91)
    chosen = [{"label": names[0], "cat": list(names), "ask": q, "say": a} for names, (q, a) in VEHICLE_CATEGORIES.items()]
    rng.shuffle(chosen)
    per = max(3, -(-int(limit * 1.2) // len(chosen)))
    return from_subjects("commons_vehicle_kinds", s, chosen, limit,
                         lambda d, title, text: [] if INSIDE.search(title) else
                         [{"question": d["ask"], "answer": d["say"]}], per_subject=per, rng=rng, deeper=2)


# ----------------------------------------------------------------- Wikidata and Commons: toys, games, playing cards

TOY_QUERY = """SELECT ?item ?itemLabel ?cat ?originLabel WHERE {
  hint:Query hint:optimizer "None" .
  { SELECT DISTINCT ?item WHERE { %s ?item wdt:P373 ?c . } }
  ?item wdt:P373 ?cat . OPTIONAL { ?item wdt:P495 ?origin }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
TOY_CATEGORIES = {
    "Dice": (ASK_TOY, "These are dice."), "Lego": (ASK_TOY, "These are LEGO bricks."),
    "Chess sets": (ASK_GAME, "This is a chess set."), "Rubik's Cube": (ASK_TOY, "This is a Rubik's Cube."),
    "Dominoes": (ASK_GAME, "These are dominoes."), "Mahjong tiles": (ASK_GAME, "These are mahjong tiles."),
    "Jigsaw puzzles": (ASK_TOY, "This is a jigsaw puzzle."), "Dolls": (ASK_TOY, "This is a doll."),
    "Teddy bears": (ASK_TOY, "This is a teddy bear."), "Kites": (ASK_TOY, "This is a kite."),
    "Spinning tops": (ASK_TOY, "This is a spinning top."), "Yo-yos": (ASK_TOY, "This is a yo-yo."),
    "Wooden toys": (ASK_TOY, "This is a wooden toy."),
    "Game controllers": ("What is this?", "This is a video-game controller."),
    "Gamepads": ("What is this?", "This is a gamepad, a video-game controller."),
}


def card_answer(label):
    """ "This is the ace of spades." from a playing card's label ("ace of spades", "Queen of Hearts", "joker")."""
    label = label[0].lower() + label[1:] if label[:1].isupper() and not label[:2].isupper() else label
    label = re.sub(r"\b(Spades|Hearts|Diamonds|Clubs)\b", lambda m: m.group(1).lower(), label)
    return sentence(f"This is the {label}" if not label.startswith(("a ", "an ", "the ")) else f"This is {label}")


def build_wikidata_toys_games(limit):
    """The toys and games pack: playing cards (instances of playing card), board games and card games (with their
    country of origin), toys (subclasses of toy) and the Commons categories of TOY_CATEGORIES, taken in turn."""
    s, rng = session(), random.Random(92)
    cards = subjects(sparql(s, TOY_QUERY % "?item wdt:P31 wd:Q47883 ."))
    boards = subjects(sparql(s, TOY_QUERY % "?item wdt:P31 wd:Q131436 ; wikibase:sitelinks ?sl . FILTER(?sl >= 2)"))
    card_games = subjects(sparql(s, TOY_QUERY % "?item wdt:P31 wd:Q142714 ; wikibase:sitelinks ?sl . "
                                                "FILTER(?sl >= 2)"))
    toys = subjects(sparql(s, TOY_QUERY % "?item wdt:P279 wd:Q11422 ."))
    for group, kind in ((cards, "card"), (boards, "board game"), (card_games, "card game"), (toys, "toy")):
        for d in group:
            d["kind"] = kind
    named_cats = [{"label": c, "cat": [c], "ask": q, "say": a, "kind": "category"} for c, (q, a) in TOY_CATEGORIES.items()]
    say(f"Wikidata: {len(cards)} playing cards, {len(boards)} board games, {len(card_games)} card games, "
        f"{len(toys)} toys")

    def rows_of(d, title, text):
        """The row of one picture: which card, game or toy."""
        kind = d["kind"]
        if kind == "card":
            return [{"question": ASK_CARD, "answer": card_answer(d["label"])}]
        if kind in ("board game", "card game"):
            return [{"question": ASK_GAME, "answer": sentence(f"This is {d['label']}, {a_or_an(kind)} {kind}"
                                                              + origin_words(d))}]
        if kind == "toy":
            return [{"question": ASK_TOY, "answer": sentence(f"This is {a_or_an(d['label'])} {d['label']}"
                                                             + origin_words(d))}]
        return [{"question": d["ask"], "answer": d["say"]}]
    chosen = round_robin([cards, cards, boards, card_games, toys, named_cats * 4], rng)
    chosen = list({id(d): d for d in chosen}.values())
    return from_subjects("wikidata_toys_games", s, chosen, limit, rows_of, per_subject=3, rng=rng, deeper=2,
                         models_ok=True)


# ----------------------------------------------------------------- Hugging Face datasets: cards and chess

def hf_files(repo):
    """The file names of a Hugging Face dataset repository."""
    from huggingface_hub import HfApi
    return HfApi().list_repo_files(repo, repo_type="dataset")


def hf_url(repo, path):
    """The download address of one file of a Hugging Face dataset."""
    return f"https://huggingface.co/datasets/{repo}/resolve/main/" + urllib.parse.quote(path)


CARDS_REPO = "drFarid/French-Playing-Cards"
CARD_SUITS = {"coeur": "hearts", "pique": "spades", "trefle": "clubs", "trèfle": "clubs", "carreau": "diamonds"}
CARD_RANKS = {"1": "ace", "as": "ace", "valet": "jack", "dame": "queen", "roi": "king", "2": "two", "3": "three",
              "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}


def card_from_folder(folder):
    """ "the queen of hearts" from a folder name such as "Coeur Dame", or "" for an unknown one."""
    words = folder.lower().split()
    if len(words) != 2 or words[0] not in CARD_SUITS or words[1] not in CARD_RANKS:
        return ""
    return f"the {CARD_RANKS[words[1]]} of {CARD_SUITS[words[0]]}"


def build_playing_cards(limit):
    """The playing cards pack: every photo in the dataset's card folders ("data/Coeur Dame/..."), the card named in
    English: "This is the queen of hearts." """
    rng = random.Random(93)
    items = []
    for path in hf_files(CARDS_REPO):
        parts = path.split("/")
        if len(parts) != 3 or parts[0] != "data" or not path.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        card = card_from_folder(parts[1])
        if card:
            items.append((safe_name("card", f"{parts[1]}-{parts[2]}"), hf_url(CARDS_REPO, path),
                          {"question": ASK_CARD, "answer": sentence(f"This is {card}"),
                           "credit": "French Playing Cards (drFarid), MIT licence, "
                                     "https://huggingface.co/datasets/drFarid/French-Playing-Cards"}))
    say(f"Playing cards: {len(items)} photos")
    rng.shuffle(items)
    return fetch_all(items[:int(limit * 1.05) + 2], workers=6)[:limit]


CHESS_REPO = "LibreYOLO/chess-pieces-mjzgj"
CHESS_CLASSES = ("bishop", "black-bishop", "black-king", "black-knight", "black-pawn", "black-queen", "black-rook",
                 "white-bishop", "white-king", "white-knight", "white-pawn", "white-queen", "white-rook")
PIECE_ORDER = ("king", "queen", "rook", "bishop", "knight", "pawn")


def pieces_words(counts):
    """ "a king, a queen, two rooks and five pawns" from {piece: count}, in the usual order."""
    parts = []
    for piece in PIECE_ORDER:
        n = counts.get(piece, 0)
        if n:
            parts.append(f"{a_or_an(piece)} {piece}" if n == 1 else f"{number_word(n)} {piece}s")
    return listed(parts) if parts else ""


def chess_answer(classes):
    """The answer for one photo from its boxed pieces' class names."""
    sides = {"white": {}, "black": {}, "": {}}
    for name in classes:
        colour, _, piece = name.rpartition("-")
        sides[colour][piece] = sides[colour].get(piece, 0) + 1
    parts = []
    for colour in ("white", "black"):
        words = pieces_words(sides[colour])
        if words:
            parts.append(f"{colour.capitalize()} has {words}.")
    if sides[""]:
        parts.append(f"There is also {pieces_words(sides[''])} whose colour is not marked.")
    total = len(classes)
    count = "There is one chess piece" if total == 1 else f"There are {number_word(total)} chess pieces"
    return f"{count} on the board. " + " ".join(parts) if parts else ""


def build_chess_pieces(limit):
    """The chess pieces pack: the 289 photos (train, valid, test), each with its YOLO label file, the pieces counted
    by colour and kind."""
    s, rng = session(), random.Random(94)
    files = hf_files(CHESS_REPO)
    labels = {p for p in files if p.endswith(".txt") and "/labels/" in p}
    items = []
    for path in files:
        if "/images/" not in path or not path.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        label = path.replace("/images/", "/labels/").rsplit(".", 1)[0] + ".txt"
        if label not in labels:
            continue
        items.append((path, label))
    rng.shuffle(items)
    out = []
    for path, label in items[:int(limit * 1.05) + 2]:
        try:
            lines = s.get(hf_url(CHESS_REPO, label), timeout=60).text.split("\n")
        except Exception:  # noqa: BLE001 - left out
            continue
        classes = [CHESS_CLASSES[int(x.split()[0])] for x in lines if x.split() and x.split()[0].isdigit()
                   and int(x.split()[0]) < len(CHESS_CLASSES)]
        answer = chess_answer(classes)
        if answer:
            out.append((safe_name("chess", path.rsplit("/", 1)[-1][:40]), hf_url(CHESS_REPO, path),
                        {"question": "What chess pieces are on the board?", "answer": answer,
                         "credit": "Chess Pieces dataset (Joseph Nelson and Brad Dwyer, Roboflow; Roboflow 100), "
                                   "CC BY 4.0, https://universe.roboflow.com/roboflow-100/chess-pieces-mjzgj, via "
                                   "https://huggingface.co/datasets/LibreYOLO/chess-pieces-mjzgj"}))
    say(f"Chess pieces: {len(out)} photos with labels")
    return fetch_all(out, workers=6)[:limit]


RENDERS_REPO = "PeterAM4/chessboard-renders"
FEN_PIECES = {"k": "king", "q": "queen", "r": "rook", "b": "bishop", "n": "knight", "p": "pawn"}


def fen_answer(fen, turn=""):
    """A position said in plain words from the piece field of a FEN: "White: king on g1, rooks on a1 and f1 ...
    Black: ..." (and whose move it is, when known)."""
    squares = {"white": {}, "black": {}}
    rows = fen.split("/")
    if len(rows) != 8:
        return ""
    for r, row in enumerate(rows):
        file = 0
        for ch in row:
            if ch.isdigit():
                file += int(ch)
                continue
            if ch.lower() not in FEN_PIECES or file > 7:
                return ""
            colour = "white" if ch.isupper() else "black"
            squares[colour].setdefault(FEN_PIECES[ch.lower()], []).append("abcdefgh"[file] + str(8 - r))
            file += 1
    parts = []
    for colour in ("white", "black"):
        said = []
        for piece in PIECE_ORDER:
            where_ = sorted(squares[colour].get(piece, []))
            if where_:
                said.append(f"{piece} on {where_[0]}" if len(where_) == 1 else f"{piece}s on {listed(where_)}")
        if said:
            parts.append(f"{colour.capitalize()}: {', '.join(said)}.")
    move = {"w": " It is White's move.", "b": " It is Black's move."}.get(turn, "")
    return " ".join(parts) + move if parts else ""


def build_chess_positions(limit):
    """The chess positions pack: rendered boards from the validation split and the training files (read row group by
    row group from Hugging Face, never whole), the position said square by square."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    fs, rng = HfFileSystem(), random.Random(95)
    paths = sorted(p for p in hf_files(RENDERS_REPO) if p.endswith(".parquet") and
                   (p.startswith("data/validation/") or p.startswith("data/train/")))
    rng.shuffle(paths)
    out = []
    for path in paths:
        if len(out) >= limit:
            break
        f = pq.ParquetFile(fs.open(f"datasets/{RENDERS_REPO}/{path}"))
        groups = list(range(f.metadata.num_row_groups))
        rng.shuffle(groups)
        for g in groups[:2]:
            table = f.read_row_group(g, columns=["id", "image", "fen", "source", "render"]).to_pylist()
            rng.shuffle(table)
            for row in table[:max(1, min(len(table), (limit - len(out)) // 2 + 1, 60))]:
                answer = fen_answer(row.get("fen") or "", ((row.get("render") or {}).get("turn") or ""))
                data = smaller((row.get("image") or {}).get("bytes") or b"")
                if not answer or not data:
                    continue
                if row.get("source") == "scattered":
                    answer += " The pieces are placed at random, not from a game."
                out.append((f"chess-render-{row['id']}.jpg", data,
                            {"question": "What is the position on this chessboard?", "answer": answer,
                             "credit": "Chessboard renders (Peter A. Massih, 2026), CC BY 4.0, "
                                       "https://huggingface.co/datasets/PeterAM4/chessboard-renders ; positions "
                                       "from the Lichess database, CC0"}))
            if len(out) >= limit:
                break
    say(f"Chess positions: {len(out)} rendered boards")
    return out[:limit]


# ----------------------------------------------------------------- DeepScoresV2: printed sheet music

SCORES_REPO = "zzsi/deep-scores-v2"
CLEF_WORDS = {"clefG": "treble", "clefF": "bass", "clefCAlto": "alto", "clefCTenor": "tenor",
              "clefUnpitchedPercussion": "percussion"}
DYNAMICS = {"dynamicP": "p", "dynamicF": "f", "dynamicM": "m", "dynamicMP": "mp", "dynamicMF": "mf",
            "dynamicPP": "pp", "dynamicFF": "ff", "dynamicSforzato": "sf", "dynamicForte": "f", "dynamicPiano": "p"}


def score_answer(categories):
    """What a printed page of music shows, from the names of its labelled symbols: the clefs, the numbers of its
    time signatures, sharps or flats in its key signatures, how many notes and rests, and its dynamics markings."""
    counts = {}
    for c in categories:
        counts[c] = counts.get(c, 0) + 1
    clefs = [w for k, w in CLEF_WORDS.items() if counts.get(k)]
    notes = sum(n for k, n in counts.items() if k.startswith("notehead"))
    rests = sum(n for k, n in counts.items() if k.startswith("rest"))
    if not notes and not rests:
        return ""
    text = "This is a page of printed sheet music" + \
        (f" with {listed(clefs)} clef{'s' if len(clefs) > 1 else ''}." if clefs else ".")
    digits = sorted({k[len("timeSig"):] for k in counts if re.fullmatch(r"timeSig\d+", k)}, key=int)
    if counts.get("timeSigCommon"):
        text += " The time signature is common time (C)."
    elif counts.get("timeSigCutCommon"):
        text += " The time signature is cut time."
    elif digits:
        text += f" The time signature uses the number{'s' if len(digits) > 1 else ''} {listed(digits)}."
    if counts.get("keySharp"):
        text += " The key signature has sharps."
    elif counts.get("keyFlat"):
        text += " The key signature has flats."
    amounts = [f"about {notes} notes" if notes != 1 else "one note"] + \
        ([f"{rests} rests" if rests != 1 else "one rest"] if rests else [])
    text += f" It has {listed(amounts)}."
    marks = list(dict.fromkeys(w for k, w in DYNAMICS.items() if counts.get(k)))
    if marks:
        text += f" Dynamics markings: {', '.join(marks)}."
    return text


def build_deepscores_sheet_music(limit):
    """The sheet music pack: pages of the DeepScoresV2 "complete" set (computer-engraved scores in five music fonts,
    every symbol boxed and named), read row group by row group from the Hugging Face copy, each page said from its
    symbols' names. Pages are big (about 2,700 pixels) and stay at the packs' usual size so the symbols stay
    readable."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfFileSystem
    fs, rng = HfFileSystem(), random.Random(96)
    paths = sorted(p for p in hf_files(SCORES_REPO) if p.endswith(".parquet"))
    rng.shuffle(paths)
    out = []
    for path in paths:
        if len(out) >= limit:
            break
        f = pq.ParquetFile(fs.open(f"datasets/{SCORES_REPO}/{path}"))
        groups = list(range(f.metadata.num_row_groups))
        rng.shuffle(groups)
        for g in groups[:2]:
            table = f.read_row_group(g, columns=["file_name", "image", "annotation_set", "objects"]).to_pylist()
            rng.shuffle(table)
            for row in table[:max(1, min(len(table), limit - len(out), 80))]:
                if row.get("annotation_set") != "deepscores":
                    continue
                answer = score_answer((row.get("objects") or {}).get("category") or [])
                data = smaller((row.get("image") or {}).get("bytes") or b"")
                if answer and data:
                    out.append((safe_name("score", row.get("file_name") or len(out)), data,
                                {"question": "What can you tell me about this sheet music?", "answer": answer,
                                 "credit": "DeepScoresV2 (Lukas Tuggener, Yvan Putra Satyawan, Alexander Pacha, "
                                           "Juergen Schmidhuber and Thilo Stadelmann, ICPR 2020), CC BY 4.0, "
                                           "https://zenodo.org/records/4012193 ; copy at "
                                           "https://huggingface.co/datasets/zzsi/deep-scores-v2"}))
            if len(out) >= limit:
                break
    say(f"DeepScoresV2: {len(out)} pages")
    return out[:limit]


# ----------------------------------------------------------------- the packs

COMMONS_NOTE = "Wikimedia Commons, https://commons.wikimedia.org : pictures CC0, public domain or CC BY (never BY-SA, " \
               "NC or ND), each with its author and file page below; captions CC0."
WIKIDATA_NOTE = "Facts (names, kinds, places, faiths, styles, makers, years) from Wikidata, CC0, " \
                "https://www.wikidata.org."

CULTURE_PACKS = {
    "open_images_culture": (build_open_images_culture, "Open Images V7 (Google): image-level labels verified by "
                                                       "people, CC BY 4.0, https://storage.googleapis.com/openimages/"
                                                       "web/index.html. Each photo is CC BY 2.0 (checked photo by "
                                                       "photo), credited below with its photographer and Flickr page."),
    "wikidata_sports": (build_wikidata_sports, f"Sports, sports equipment and sports grounds. {WIKIDATA_NOTE} "
                                               f"{COMMONS_NOTE}"),
    "wikidata_instruments": (build_wikidata_instruments, f"Musical instruments of the world. {WIKIDATA_NOTE} "
                                                         f"{COMMONS_NOTE}"),
    "met_instruments": (build_met_instruments, "The Metropolitan Museum of Art, Department of Musical Instruments, "
                                               "Open Access (public-domain objects only), CC0, "
                                               "https://metmuseum.github.io ; each object's record and credit line "
                                               "below."),
    "wikidata_worship": (build_wikidata_worship, f"Places of worship of every faith. {WIKIDATA_NOTE} {COMMONS_NOTE}"),
    "commons_religious_life": (build_commons_religious_life, "Festivals, ceremonies, pilgrimages, religious objects "
                                                             f"and clergy dress of many faiths. {COMMONS_NOTE}"),
    "wikidata_landmarks": (build_wikidata_landmarks, f"Landmarks and World Heritage Sites. {WIKIDATA_NOTE} "
                                                     f"{COMMONS_NOTE}"),
    "wikidata_architecture": (build_wikidata_architecture, f"Architectural styles and building parts. {WIKIDATA_NOTE} "
                                                           f"{COMMONS_NOTE}"),
    "gldv2_landmarks": (build_gldv2_landmarks, "Google Landmarks Dataset v2 (Tobias Weyand, Andre Araujo, Bingyi Cao "
                                               "and Jack Sim, CVPR 2020), https://github.com/cvdfoundation/"
                                               "google-landmark : labels CC BY 4.0; only images whose Commons licence "
                                               "(the dataset's train_attribution.csv) is CC0, public domain or CC BY, "
                                               "each credited below."),
    "wikidata_vehicle_models": (build_wikidata_vehicle_models, f"Car, motorcycle, bus, truck, tram, locomotive and "
                                                               f"ferry models. {WIKIDATA_NOTE} {COMMONS_NOTE}"),
    "commons_vehicle_kinds": (build_commons_vehicle_kinds, f"Taxis, minibuses, bicycles, boats and other vehicles. "
                                                           f"{COMMONS_NOTE}"),
    "wikidata_toys_games": (build_wikidata_toys_games, f"Playing cards, board and card games, toys. {WIKIDATA_NOTE} "
                                                       f"{COMMONS_NOTE}"),
    "playing_cards": (build_playing_cards, "French Playing Cards (drFarid), MIT licence, "
                                           "https://huggingface.co/datasets/drFarid/French-Playing-Cards"),
    "chess_pieces": (build_chess_pieces, "Chess Pieces (Joseph Nelson and Brad Dwyer, Roboflow), part of Roboflow 100 "
                                         "(Ciaglia et al., 2022), CC BY 4.0, "
                                         "https://universe.roboflow.com/roboflow-100/chess-pieces-mjzgj ; copy at "
                                         "https://huggingface.co/datasets/LibreYOLO/chess-pieces-mjzgj"),
    "chess_positions": (build_chess_positions, "Chessboard renders (Peter A. Massih, 2026), CC BY 4.0, "
                                               "https://huggingface.co/datasets/PeterAM4/chessboard-renders ; positions "
                                               "from the Lichess database (CC0); piece meshes CC0, MIT and CC BY as "
                                               "listed by the dataset."),
    "deepscores_sheet_music": (build_deepscores_sheet_music, "DeepScoresV2 (Tuggener, Satyawan, Pacha, Schmidhuber "
                                                             "and Stadelmann, 2020), CC BY 4.0, "
                                                             "https://zenodo.org/records/4012193 ; copy at "
                                                             "https://huggingface.co/datasets/zzsi/deep-scores-v2"),
}

# How many pictures a full build takes from each collection (about what each offers after the licence checks).
CULTURE_LIMITS = {
    "open_images_culture": 8000,      # of about 23,000 free photos with a verified culture label (val and test)
    "wikidata_sports": 3000,          # about 750 sports, kinds of equipment and grounds, at most 4 pictures each
    "wikidata_instruments": 4000,     # about 1,700 kinds of instrument, at most 4 pictures each
    "met_instruments": 3500,          # of about 4,000 instruments with pictures (the public-domain ones)
    "wikidata_worship": 6000,         # 23 kinds of place of worship, the best known first, 3 pictures each
    "commons_religious_life": 2000,   # 57 categories (and their subcategories)
    "wikidata_landmarks": 6000,       # World Heritage Sites and 13 kinds of landmark, 3 pictures each
    "wikidata_architecture": 2500,    # about 500 styles and 600 building parts
    "gldv2_landmarks": 8000,          # of about 1.6 million clean images (the free ones, 2 a landmark)
    "wikidata_vehicle_models": 6000,  # car models half; motorcycles, buses, trucks, trams, locomotives, ferries
    "commons_vehicle_kinds": 1500,    # 36 categories
    "wikidata_toys_games": 2000,      # about 150 playing cards, 470 games, 270 toys and 15 categories
    "playing_cards": 1877,            # every photo
    "chess_pieces": 289,              # every photo
    "chess_positions": 3000,          # of 500,000 renders
    "deepscores_sheet_music": 2000,   # of 255,385 engraved pages
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one culture pack builder.")
    parser.add_argument("key", choices=sorted(CULTURE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = CULTURE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
