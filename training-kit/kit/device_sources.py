"""Household devices (the kinds of device in the toolkit's manual collections: kitchen and home appliances, computers
and game consoles, TVs and audio, older electronics such as VCRs, camcorders, Walkmans and answering machines, lawn
and garden machines, things around the house, tools, office machines, personal electronics and health devices) for
the Picture Model Training Kit: the collections that cannot be ready-made packs because of their licence. The open
ones (Wikidata product models with Commons pictures, Commons device categories, and the Smithsonian's household
devices) are in packs/device_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice.

Groups (Source.group, as in sources.py):
  "share-alike"  CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                 is CC BY-SA.
  "research"     research use, or no licence stated for the data: personal use only (--personal-research with
                 --accept-research-terms).

Answers are fixed sentences from each source's own records (a Wikidata model's name, kind, maker and year; a Commons
category's name; the object class CO3D's makers gave a video), never written by an AI model. Files whose words name a
person are left out, so these show the devices themselves.

The collections (DEVICE_SOURCES):
  share-alike
    device_models_sa   Wikimedia Commons files under CC BY-SA or GFDL: the Commons categories of household device
                       models found through Wikidata (the same kinds as the open wikidata_devices pack: "This is a
                       Sony Walkman WM-2, a portable cassette player made by Sony. This model first came out in
                       1981.") and the device-kind categories of the open commons_devices pack ("This is a VHS video
                       recorder (VCR) ..."). Captions CC0; facts CC0 (Wikidata).
  research
    co3d_devices       CO3D, Common Objects in 3D (Reizenstein et al., Meta AI, ICCV 2021): people's own videos
                       walking around a toaster, microwave oven, hair dryer, keyboard, laptop, remote control,
                       television, mobile phone or computer mouse at home; one still from the middle of each video.
                       "What is this?" -> "This is a toaster." The repository's LICENSE is CC BY-NC 4.0 and its README
                       says "The CO3D codebase is released under the CC BY-NC 4.0"; no separate licence is written for
                       the videos, so personal use only. Only the chosen frames are read out of the 20 GB zips, by HTTP
                       ranges (about 200 KB each, plus each zip's list of files, about 10 MB).

Needing sign-up (DEVICE_SIGN_UP has the links) and looked at but not included (DEVICE_NOT_INCLUDED has the reasons).

DEVICE_PICTURE_MAKING_OK: device_models_sa (the devices themselves; files naming a person are left out). CO3D's
videos were filmed by people in their homes and sometimes show them, so it is for describing only.

    python -c "import sources, device_sources"      (from the kit folder: checks the file loads)
"""

import collections
import json
import os
import random
import re
import time

from extra_sources import (NUDE, USER_AGENT, commons_file_name, commons_members, commons_sa_entries, commons_session,
                           say)
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, remote_zip, zip_members
from sources import Source, clean

WHAT_Q = "What is this?"
MAKE_Q = "What make and model is this?"
WHEN_Q = "About when was this made?"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# As in packs/device_packs.py: words that show a person, and files that are not a photo of the device itself.
PERSON = re.compile(r"\b(man|men|woman|women|person|people|persons|boy|boys|girl|girls|child\w*|kids?|bab(y|ies)|"
                    r"toddlers?|teen\w*|users?|worker\w*|operator\w*|customers?|students?|selfie|portraits?|"
                    r"wearing|holding|he|she|his|her|him|they are|family|families|crowd\w*)\b", re.I)
NOT_THE_DEVICE = re.compile(r"\b(box(es)?|boxed|packag\w*|manuals?|advert\w*|ads?|brochures?|catalog(ue)?s?|logos?|"
                            r"icons?|screenshots?|screen ?shots?|screens? showing|teardowns?|disassembl\w*|"
                            r"dismantl\w*|motherboards?|mainboards?|pcbs?|circuit boards?|inside|insides|interior|"
                            r"internals?|opened|open case|schematics?|diagrams?|drawings?|patents?|sketch\w*|"
                            r"renders?|rendering|3d|cgi|serial numbers?|stickers?|chargers?|power adapters?|"
                            r"controllers?|gamepads?|joypads?|game cartridges?|games? (for|of)|exhibitions?|"
                            r"museum display|stamps?|coins?|toys?|lego|models? of|scale models?|miniatures?|"
                            r"replicas?|cosplay|spare parts?|parts|illustrations?|paintings?|cartoons?)\b", re.I)


# ----------------------------------------------------------------- share-alike: device_models_sa

# The kinds of device (Wikidata class, how an answer says it), most specific first, as packs/device_packs.py.
DEVICE_KINDS = [
    ("Q17232663", "air fryer"), ("Q17209136", "toaster oven"), ("Q14890", "toaster"), ("Q1210743", "espresso machine"),
    ("Q211841", "coffee maker"), ("Q501862", "blender"), ("Q1126251", "food processor"), ("Q642345", "slow cooker"),
    ("Q1137500", "rice cooker"), ("Q1364042", "electric kettle"), ("Q127956", "microwave oven"),
    ("Q124441", "washing machine"), ("Q496334", "clothes dryer"), ("Q186263", "dishwasher"),
    ("Q37828", "refrigerator"), ("Q1265533", "air conditioner"), ("Q101674", "vacuum cleaner"),
    ("Q3962", "laptop"), ("Q155972", "tablet computer"), ("Q56155", "desktop computer"),
    ("Q16338", "personal computer"), ("Q941818", "handheld game console"), ("Q8076", "video game console"),
    ("Q5318", "router"), ("Q82", "printer"), ("Q8075", "television set"), ("Q1567371", "streaming media player"),
    ("Q3783103", "DVD player"), ("Q17591720", "turntable (record player)"), ("Q570", "loudspeaker"),
    ("Q335234", "camcorder"), ("Q380616", "videocassette recorder (VCR)"), ("Q7231333", "portable CD player"),
    ("Q1023100", "CD player"), ("Q1358666", "boombox"), ("Q510176", "cassette deck"),
    ("Q121552543", "cassette recorder"), ("Q568717", "answering machine"), ("Q1195934", "cordless telephone"),
    ("Q832436", "pager"), ("Q162768", "personal digital assistant (PDA)"), ("Q313695", "instant camera"),
    ("Q62927", "digital camera"), ("Q3928875", "clock radio"), ("Q159391", "radio"), ("Q46335", "typewriter"),
    ("Q31087", "calculator"), ("Q260521", "lawn mower"), ("Q208040", "chainsaw"), ("Q49013", "sewing machine"),
    ("Q15004", "hair dryer"), ("Q979744", "electric toothbrush"), ("Q22645", "smartphone"),
    ("Q17517", "mobile phone"), ("Q10872571", "portable media player"), ("Q5362345", "smartwatch"),
]
DEVICE_QUERY = """SELECT ?item ?itemLabel ?cat ?makerLabel ?brandLabel ?start WHERE {
  { SELECT DISTINCT ?item ?sl WHERE { ?c wdt:P279* wd:%s . { ?item wdt:P31 ?c } UNION { ?item wdt:P279 ?c }
      FILTER EXISTS { ?item wdt:P176|wdt:P1716 [] } ?item wdt:P373 [] ; wikibase:sitelinks ?sl . }
    ORDER BY DESC(?sl) LIMIT %d }
  ?item wdt:P373 ?cat .
  OPTIONAL { ?item wdt:P176 ?maker } OPTIONAL { ?item wdt:P1716 ?brand }
  OPTIONAL { ?item wdt:P571|wdt:P577|wdt:P5444 ?start }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
COMPANY_ENDINGS = re.compile(r"[,\s]+(Group|Inc\.?|Incorporated|Corporation|Corp\.?|Co\.?,? Ltd\.?|Company|Ltd\.?|"
                             r"Limited|LLC|plc|PLC|GmbH|AG|S\.A\.|SA|N\.V\.|B\.V\.|K\.K\.|Holdings)$")

# The device-kind categories of the open commons_devices pack (category -> what the answer calls it).
DEVICE_CATEGORIES = {
    "Coffee machines": "a coffee machine (coffee maker)", "Food mixers": "a food mixer",
    "Bread machines": "a bread machine", "Toaster ovens": "a toaster oven", "Deep fryers": "a deep fryer",
    "Refrigerators": "a refrigerator (fridge)", "Chest freezers": "a chest freezer", "Freezers": "a freezer",
    "Front-loading washing machines": "a front-loading washing machine",
    "Top-loading washing machines": "a top-loading washing machine", "Air conditioners": "an air conditioner",
    "Vacuum cleaners": "a vacuum cleaner", "Robotic vacuum cleaners": "a robot vacuum cleaner",
    "Dehumidifiers": "a dehumidifier", "Humidifiers": "a humidifier", "Home computers": "a home computer",
    "Computer monitors": "a computer monitor (screen)", "Routers": "a router", "Inkjet printers": "an inkjet printer",
    "Laser printers": "a laser printer", "Scanners": "a scanner", "Television sets": "a television set",
    "Set-top boxes": "a set-top box", "Digital media players": "a streaming media player",
    "DVD players": "a DVD player", "Blu-ray players": "a Blu-ray player", "Soundbars": "a soundbar",
    "AV receivers": "an AV receiver (amplifier)", "Record players": "a record player (turntable)",
    "Boomboxes": "a boombox", "Bluetooth speakers": "a portable Bluetooth speaker",
    "Smart speakers": "a smart speaker", "VHS recorders": "a VHS video recorder (VCR)", "Camcorders": "a camcorder",
    "Cassette decks": "a cassette deck", "Tape recorders": "a tape recorder",
    "Sony Walkman cassette players": "a Sony Walkman, a portable cassette player",
    "Sony Discman": "a Sony Discman, a portable CD player", "Portable CD players": "a portable CD player",
    "CD players": "a CD player", "Answering machines": "a telephone answering machine",
    "Cordless telephones": "a cordless telephone", "Rotary dial telephones": "a rotary dial telephone",
    "Pagers": "a pager (beeper)", "Personal digital assistants": "a personal digital assistant (PDA)",
    "Instant cameras": "an instant camera", "Clock radios": "a clock radio", "Typewriters": "a typewriter",
    "Electric typewriters": "an electric typewriter", "Fax machines": "a fax machine",
    "Digital audio players": "a digital music player (MP3 player)", "E-readers": "an e-reader",
    "Lawn tractors": "a lawn tractor (a riding lawn mower)", "Robotic lawn mowers": "a robot lawn mower",
    "String trimmers": "a string trimmer (strimmer)", "Leaf blowers": "a leaf blower",
    "Hedge trimmers": "a hedge trimmer", "Snow blowers": "a snow blower", "Engine-generators": "a generator",
    "Pressure washers": "a pressure washer", "Barbecues": "a barbecue grill",
    "Carbon monoxide detectors": "a carbon monoxide alarm", "Garage door openers": "a garage door opener",
    "Doorbells": "a doorbell", "Electric fans": "an electric fan", "Ceiling fans": "a ceiling fan",
    "Electric heaters": "an electric heater", "Air purifiers": "an air purifier",
    "Sewing machines": "a sewing machine", "Electric irons": "an electric iron", "Hairdryers": "a hair dryer",
    "Electric shavers": "an electric shaver", "Electric toothbrushes": "an electric toothbrush",
    "Treadmills": "a treadmill", "Photocopiers": "a photocopier", "Paper shredders": "a paper shredder",
    "Calculators": "a calculator", "Headphones": "headphones", "Pulse oximeters": "a pulse oximeter",
}


def company(label):
    """A maker's name as an answer says it: "Sony Group" -> "Sony", "Canon Inc." -> "Canon"."""
    name = clean(label)
    for _ in range(3):
        shorter = COMPANY_ENDINGS.sub("", name).strip(" ,")
        if shorter == name or not shorter:
            break
        name = shorter
    return name


def wd_year(value):
    """The year of a Wikidata date ("1981-07-01T00:00:00Z" -> "1981"), or "" (years before 1850 or after 2026)."""
    m = re.match(r"^(\d{4})-", value or "")
    return m.group(1) if m and 1850 <= int(m.group(1)) <= 2026 else ""


def model_answers(label, kind, makers, years):
    """[(question, answer)] for one Wikidata model: "What is this?", "What make and model is this?" and, when a year
    is known, "About when was this made?" (as packs/device_packs.model_rows)."""
    makers = list(dict.fromkeys(company(m) for m in makers if m and not re.fullmatch(r"Q\d+", m)))
    maker = makers[0] if len(makers) == 1 else ""
    year = min(years) if years else ""
    by = maker and maker.lower().split()[0] not in label.lower()
    article = "an" if label[:1].lower() in "aeio" else "a"
    kind_article = "an" if kind[:1].lower() in "aeio" else "a"
    what = f"This is {article} {label}, {kind_article} {kind}" + (f" made by {maker}" if by else "") + "."
    rows = [(WHAT_Q, what + (f" This model first came out in {year}." if year else "")),
            (MAKE_Q, f"It is {article} {label}" + (f", made by {maker}" if by else "") + ".")]
    if year:
        rows.append((WHEN_Q, f"It is {article} {label}, a model that first came out in {year}."))
    return rows


def wd_models(per_kind):
    """{Commons category: [(question, answer)]} for the Wikidata device models of DEVICE_KINDS (a model counted
    under its first kind); {} when Wikidata does not answer."""
    import requests
    s = requests.Session()
    s.headers["User-Agent"] = USER_AGENT
    out, taken = {}, set()
    for qid, phrase in DEVICE_KINDS:
        bindings = []
        for attempt in range(4):
            try:
                r = s.get(WIKIDATA_SPARQL, params={"query": DEVICE_QUERY % (qid, per_kind), "format": "json"},
                          timeout=120)
                if r.status_code == 200:
                    bindings = r.json()["results"]["bindings"]
                    break
            except Exception:  # noqa: BLE001 - busy: wait and try again
                pass
            time.sleep(10 * (attempt + 1))
        models = collections.OrderedDict()
        for b in bindings:
            item = b["item"]["value"].rsplit("/", 1)[-1]
            label = clean((b.get("itemLabel") or {}).get("value"))
            if item in taken or not label or re.fullmatch(r"Q\d+", label):
                continue
            d = models.setdefault(item, {"label": label, "cats": set(), "makers": [], "brands": [], "years": set()})
            d["cats"].add((b.get("cat") or {}).get("value", ""))
            for key, name in (("makers", "makerLabel"), ("brands", "brandLabel")):
                value = clean((b.get(name) or {}).get("value"))
                if value and value not in d[key]:
                    d[key].append(value)
            year = wd_year((b.get("start") or {}).get("value"))
            if year:
                d["years"].add(year)
        for item, d in models.items():
            taken.add(item)
            makers = d["makers"] if len(d["makers"]) == 1 else d["brands"]
            for cat in d["cats"]:
                if cat:
                    out.setdefault(cat, model_answers(d["label"], phrase, makers, d["years"]))
        time.sleep(1)
    say(f"  Wikidata: {len(out)} device model categories.")
    return out


def sa_device_items(specs, want, prefix, per_category):
    """[(file name, address, row)] for Commons files under CC BY-SA or GFDL from specs {category: [(question,
    answer)]}: the category's rows, and the file's caption as a description when it is a real one. Files that are
    not a photo of the device itself, or whose words name a person or nudity, are left out; rows naming a child are
    marked "child"."""
    s, items, seen, pictures = commons_session(), [], set(), 0
    categories = sorted(specs)
    random.Random(prefix).shuffle(categories)
    for category in categories:
        if pictures >= want:
            break
        try:
            titles = [t for t in commons_members(s, category, "file") if t not in seen]
        except RuntimeError:
            continue                                     # Commons kept refusing: the next category
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 3]):
            words = f"{title} {text}"
            if found >= per_category or NUDE.search(words) or PERSON.search(words) or NOT_THE_DEVICE.search(title):
                continue
            seen.add(title)
            child = {"child": True} if CHILD_WORDS.search(words) else {}
            name = commons_file_name(prefix, title)
            for question, answer in specs[category]:
                items.append((name, url, {"question": question, "answer": answer, "split": "", "credit": credit,
                                          **child}))
            if text and set(re.findall(r"[a-z]+", text.lower())) - set(re.findall(r"[a-z]+", title.lower())):
                items.append((name, url, {"question": "Write a short description of this picture for someone who "
                                                      "cannot see it.", "answer": text, "split": "",
                                          "credit": credit, **child}))
            found += 1
        pictures += found
    say(f"  Commons share-alike: {pictures} device pictures from {len(categories)} categories.")
    return items


def prepare_device_models_sa(source, data_dir, work, cap):
    """Commons files under CC BY-SA or GFDL of Wikidata's device models (two thirds of the cap) and of the device
    kinds (one third)."""
    want = cap + source.test
    models = wd_models(max(10, min(80, want // len(DEVICE_KINDS) + 5)))
    items = sa_device_items(models, int(want * 0.67) + 1, "device-model-sa", 2)
    kinds = {c: [(WHAT_Q, f"This is {a}.")] for c, a in DEVICE_CATEGORIES.items()}
    items += sa_device_items(kinds, want - len({i[0] for i in items}), "device-kind-sa",
                             max(2, (want // 3) // len(kinds) + 1))
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: CO3D

CO3D_LINKS = "https://raw.githubusercontent.com/facebookresearch/co3d/main/co3d/links.json"
CO3D_CREDIT = ("CO3D: Common Objects in 3D (Jeremy Reizenstein, Roman Shapovalov, Philipp Henzler, Luca Sbordone, "
               "Patrick Labatut and David Novotny, Meta AI, ICCV 2021), https://github.com/facebookresearch/co3d, "
               "CC BY-NC 4.0 (the repository's licence)")
CO3D_KINDS = {"toaster": "a toaster", "microwave": "a microwave oven", "hairdryer": "a hair dryer",
              "keyboard": "a computer keyboard", "laptop": "a laptop", "remote": "a remote control",
              "tv": "a television", "cellphone": "a mobile phone", "mouse": "a computer mouse"}
CO3D_PARTS_PER_KIND = 2         # zip parts read for each kind (each holds about 100 videos)


def co3d_frames(names):
    """{video folder: the frame from the middle of it} from the names in a CO3D zip
    ("toaster/274_29381_56794/images/frame000101.jpg")."""
    videos = collections.defaultdict(list)
    for name in names:
        m = re.match(r"^([^/]+/[^/]+)/images/frame\d+\.jpg$", name)
        if m:
            videos[m.group(1)].append(name)
    return {video: sorted(frames)[len(frames) // 2] for video, frames in videos.items()}


def prepare_co3d_devices(source, data_dir, work, cap):
    """CO3D stills: for each kind of CO3D_KINDS, one still from the middle of each video of a few zip parts (read by
    HTTP ranges, so only the chosen frames and each zip's list of files are downloaded), an even share for each
    kind."""
    from more_sources import download_to
    with open(download_to(work, CO3D_LINKS, "co3d_links.json"), encoding="utf-8") as f:
        links = json.load(f)["full"]
    share = max(1, (cap + source.test) // len(CO3D_KINDS) + 1)
    rows = []
    for kind, answer in CO3D_KINDS.items():
        parts = list(links.get(kind) or [])
        random.Random(kind).shuffle(parts)
        chosen = []
        for url in parts[:CO3D_PARTS_PER_KIND]:
            if len(chosen) >= share:
                break
            try:
                frames = co3d_frames(remote_zip(url).namelist())
            except Exception as e:  # noqa: BLE001 - a part that cannot be read: the next one
                say(f"  CO3D {kind}: a zip could not be read ({e}).")
                continue
            videos = sorted(frames)
            random.Random(url).shuffle(videos)
            picked = [(frames[v], {"question": WHAT_Q, "answer": f"This is {answer}.", "split": "",
                                   "credit": CO3D_CREDIT}) for v in videos[:share - len(chosen)]]
            chosen += [(url, p) for p in picked]
        say(f"  CO3D {kind}: {len(chosen)} videos chosen.")
        for url in dict.fromkeys(u for u, _ in chosen):
            rows += zip_members(source, data_dir, work, lambda url=url: remote_zip(url),
                                [p for u, p in chosen if u == url], workers=3)
    return rows


# ----------------------------------------------------------------- the collections

DEVICE_SOURCES = [
    # ---- share-alike
    Source("device_models_sa", "Household devices and their make and model: Wikimedia Commons files under CC BY-SA "
                               "or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions and Wikidata facts CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org; "
           "model facts from Wikidata (CC0)", "share-alike", 2000, 20, prepare_device_models_sa,
           "about 300 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    # ---- research
    Source("co3d_devices", "CO3D: toasters, microwaves, hair dryers, keyboards, laptops, remotes, TVs, phones and "
                           "mice filmed at home, stills (personal use)",
           "CC BY-NC 4.0 is the repository's licence (github.com/facebookresearch/co3d); no separate licence is "
           "written for the videos", CO3D_CREDIT, "research", 1000, 20, prepare_co3d_devices,
           "about 200 MB of stills and 200 MB of zip file lists, read straight from the web",
           terms="https://github.com/facebookresearch/co3d/blob/main/LICENSE",
           terms_summary="The repository is CC BY-NC 4.0 (use with credit, not for commercial purposes); no separate "
                         "licence is written for the videos, so personal, non-commercial use only."),
]

# The collections a picture-making model may learn from: the share-alike device photos (no people).
DEVICE_PICTURE_MAKING_OK = {"device_models_sa"}

DEVICE_SIGN_UP = {
    "Powerhouse Collection API (Sydney)":
        "https://api.maas.museum : a free API key is needed (it would come from a GitHub secret such as "
        "POWERHOUSE_API_KEY). Thousands of Australian household appliances, radios, TVs and computers with "
        "catalogue descriptions. The API did not answer from the machine these entries were made on, so the "
        "picture licences were not checked; add a pack only after reading them.",
    "Museums Victoria Collections (Australia; CC BY and public domain)":
        "https://collections.museumsvictoria.com.au/api : open, but it refused the machine these entries were made "
        "on (403). It holds many household appliances and electronics; get them yourself, or add a pack when it "
        "answers.",
    "Te Papa API key": "https://data.tepapa.govt.nz : a guest token works; few household devices there have open "
                       "pictures (most are All Rights Reserved or CC BY-NC-ND).",
    "Kaggle and Roboflow appliance sets": "https://www.kaggle.com and https://universe.roboflow.com : an account; "
                                          "check each set's licence and where its photos came from.",
}

DEVICE_NOT_INCLUDED = {
    "MyFixit and iFixit repair guides (CC BY-NC-SA)":
        "iFixit's robots.txt says \"Content-Signal: search=yes, ai-input=yes, ai-train=no\" and \"Use of iFixit "
        "content for LLM training or for other commercial purposes without a specific license is a violation of our "
        "Terms of Use\" (https://www.ifixit.com/robots.txt); MyFixit's step photos are iFixit's. Only with written "
        "permission from iFixit.",
    "Science Museum Group (pictures CC BY-NC-SA 4.0)": "collection.sciencemuseumgroup.org.uk refused the machine "
                                                       "(403), as before (archive_sources.py).",
    "Cooper Hewitt, Smithsonian Design Museum": "its records are CC0, but no device record of it in Smithsonian "
                                                "Open Access has a picture marked CC0 (all 256 of its bulk files "
                                                "were read in November 2026).",
    "Europeana household devices": "the museums with many devices (Swedish, Estonian, Norwegian, German and Dutch) "
                                   "describe them in their own languages; English records are few (29 sewing "
                                   "machines, mostly British Library book pictures). A translated pack, like "
                                   "europeana_fi, could be added later.",
    "Objectron (Google, C-UDA 1.0)": "of its nine kinds only laptops and cameras are devices, already well covered.",
    "Amazon Berkeley Objects": "open (CC BY 4.0): the ready-made abo_products pack already has its appliances and "
                               "electronics.",
    "Open Images V7 device labels, Dollar Street": "open: already open_images_objects, open_images_tech and "
                                                   "dollar_street.",
    "ENERGY STAR and US Department of Energy": "product data only, no product photos (as us_sources.py says).",
}
