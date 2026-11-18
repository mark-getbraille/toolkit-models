"""Pack builders for HOUSEHOLD DEVICES: the kinds of device in the toolkit's manual collections (manuals/categories.py):
small kitchen appliances, home appliances, computers, game consoles and routers, TVs and audio, older electronics of the
1990s and 2000s (VCRs, camcorders, cassette and CD players, Walkman and Discman, MiniDisc, answering machines, cordless
phones, pagers, PDAs, film cameras, clock radios, typewriters), lawn, garden and outdoor machines, things around the
house, power tools, office machines, personal electronics and health devices. Used by build_packs.py in the same way as
its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is
{"question", "answer", "credit"}, plus "place" where the source says where the photo was taken (or, for a museum
object, where it was made: "place_kind": "origin") and "child": True where the picture's words name a child. A picture
with more than one question comes once with its JPEG and then again as (None, None, row) rows whose "file" names the
same picture (food_packs.with_twins). The limit counts pictures.

Why: so that the picture describer can say WHAT A DEVICE IS, and where the source says so its make, model and era:
"This is a JVC HR-3300, a videocassette recorder (VCR) made by JVC. This model first came out in 1976." Controls and
control panels (thermostats, oven and microwave panels, washer dials, stove knobs, remotes, lift buttons, cash
machines, dashboards) are NOT here: they are us_modern_packs.commons_us_controls, home_packs.commons_appliances and
mechanical_packs.

Every answer is a fixed sentence written here from the source's own record, never guessed and never written by an AI
model:
  - Wikidata (CC0): the model's English name, its kind (the class Wikidata puts it in), its maker (P176) or brand
    (P1716) and the year it first came out (P571 inception, P577 publication date or P5444 model year), only when
    Wikidata gives it;
  - a Wikimedia Commons category's name ("Videocassette recorders" -> "This is a videocassette recorder (VCR) ...",
    with one short plain line about what that kind of device does), and the file's own caption as "Write a short
    description of this picture for someone who cannot see it." when it is a real one;
  - the Smithsonian's own catalogue record (title, object type, description, date made).
Questions: "What is this?", "What make and model is this?", "About when was this made?" (only when the source gives
a date), "Tell me about this museum object." and the file's caption.

What was already covered, and so is not repeated here: Open Images device labels (open_images_objects asks about
toasters, microwave ovens, televisions, remote controls, laptops, lawn mowers, blenders, coffee makers, washing
machines, fridges, hair dryers, sewing machines and many more; open_images_tech about routers, cameras, projectors,
typewriters, fax machines, game consoles ...), Amazon Berkeley Objects product photos (abo_products, CC BY 4.0),
Dollar Street homes (dollar_street), and the Commons categories of commons_things (phones, laptops, desktop computers,
keyboards, mice, tablets, smartwatches, webcams, digital cameras, projectors, modems, radios, chainsaws, blenders,
juicers, espresso machines, coffee grinders, waffle irons, food processors, slow cookers ...), commons_kitchen
(toasters, kettles, rice cookers, pressure cookers, cookers), commons_appliances (microwave ovens, washing machines,
scales, meters), commons_tools (drills, saws, grinders, lawn mowers) and commons_disability (braille displays and
writers, hearing aids). Wikidata's product MODELS are new (no pack asked "what make and model?"), and so are the Commons
device categories listed in COMMONS_DEVICES.

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE words leave a file out); files whose words name a person
(PERSON) are left out, so that these packs show the devices themselves and may be used for picture-making; rows whose
words name a child are marked "child" all the same.

The packs (all open, checked at the source in November 2026):
  wikidata_devices   Wikidata product models of household devices (DEVICE_KINDS), each with a picture: its Wikidata
                     picture (P18) and a few files of its Commons category (P373). Data CC0 ("All data in Wikidata
                     has a CC0 license.", https://www.wikidata.org/wiki/Wikidata:Licensing); pictures CC0, public
                     domain or CC BY, each credited (BY-SA files are the share-alike kit entry
                     device_models_sa). "What is this?", "What make and model is this?" and "About when was this
                     made?".
  commons_devices    Wikimedia Commons categories of device kinds no other pack has (COMMONS_DEVICES). Captions CC0
                     (Commons structured data); pictures CC0, public domain or CC BY, checked file by file from
                     each file's own licence (author credited). "What is this?" and the caption.
  nmah_devices       Smithsonian National Museum of American History, Open Access: records of household devices
                     (sewing machines, typewriters, phonographs, toasters, irons, stoves, heaters, fans, washing
                     machines, telephones, radios, cameras, including patent models) whose pictures are CC0,
                     checked picture by picture from each record's own media rights ("usage": {"access": "CC0"};
                     https://www.si.edu/openaccess). "Tell me about this museum object." with the catalogue
                     description, "What is this?" from the record's title and object type and "About when was this
                     made?" from its date. A free picture whose description is under twelve words is set aside for a
                     description (build_packs.needs_description).

Non-open collections on the same subject (Commons BY-SA device files and model photos; CO3D's turntable videos of
toasters, microwaves, hair dryers, keyboards, laptops, remotes, TVs, phones and mice) are kit download entries in
training-kit/kit/device_sources.py, with the sign-up and left-out collections listed there.

    python packs/device_packs.py wikidata_devices --limit 8      (prints a few rows: a quick check of one builder)
"""

import collections
import json
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say, ALT_TEXT, MUSEUM, SI_BUCKET, si_keys, first_sentences
from build_packs import pass_random, needs_description, listing_out_of_time  # top-ups, set-aside, time (build_packs)
from food_packs import with_twins, count_pictures
from everyday_packs import a_or_an
from expression_packs import CHILD, mark_child, child_count
from home_packs import (NUDE, NOT_RESPECTFUL, FIRST_PERSON, home_entries, commons_fetch, category_files, file_name,
                        COMMONS_PLACES)
from culture_packs import sparql, subjects, year_of, from_subjects, round_robin
from documentary_packs import finish
from service_packs import si_media, si_notes, when_words
from world_packs import full_stop
from places import where, place_from_text

WHAT_Q = "What is this?"
MAKE_Q = "What make and model is this?"
WHEN_Q = "About when was this made?"

# Words that show a person in the picture (these packs show the devices themselves; see the module docstring).
PERSON = re.compile(r"\b(man|men|woman|women|person|people|persons|boy|boys|girl|girls|child\w*|kids?|bab(y|ies)|"
                    r"toddlers?|teen\w*|users?|worker\w*|operator\w*|customers?|students?|selfie|portraits?|"
                    r"wearing|holding|he|she|his|her|him|they are|family|families|crowd\w*|dr|mr|mrs|ms|sir|"
                    r"lady|mister|herr|frau|meneer|mevrouw)\b", re.I)
# A caption in English has some of these words (captions in other languages are not used: no translation here).
ENGLISH_WORDS = re.compile(r"\b(the|of|and|with|in|at|on|a|an|is|from|for|this|its)\b", re.I)
# Nationaal Archief (Anefo) photos are already the open "anefo" pack (archive_packs.py), with their Dutch captions.
ANEFO = re.compile(r"Bestanddeelnr|\bAnefo\b", re.I)
# Files that are not a photo of the device seen whole: its box, manual, advertisement, insides, parts or screen.
NOT_THE_DEVICE = re.compile(r"\b(box(es)?|boxed|packag\w*|manuals?|advert\w*|ads?|brochures?|catalog(ue)?s?|logos?|"
                            r"icons?|screenshots?|screen ?shots?|screens? showing|teardowns?|disassembl\w*|"
                            r"dismantl\w*|motherboards?|mainboards?|pcbs?|circuit boards?|inside|insides|interior|"
                            r"internals?|opened|open case|schematics?|diagrams?|drawings?|patents?|sketch\w*|"
                            r"renders?|rendering|3d|cgi|serial numbers?|stickers?|chargers?|power adapters?|"
                            r"controllers?|gamepads?|joypads?|game cartridges?|games? (for|of)|exhibitions?|"
                            r"museum display|stamps?|coins?|toys?|lego|models? of|scale models?|miniatures?|"
                            r"replicas?|cosplay|spare parts?|parts)\b", re.I)
# (A tape, disc or cassette in the picture is kept: "a VCR with a tape half inserted" is what the owner wants said.)


# ----------------------------------------------------------------- wikidata_devices

# The kinds of device (Wikidata class, how an answer says it), most specific first: an item is counted under the
# first kind whose class tree holds it (a camcorder is also in Wikidata's videocassette recorder tree, an air fryer in
# the oven tree). Each kind takes its turn, so phones and cameras, with thousands of models, do not fill the pack.
DEVICE_KINDS = [
    # small kitchen appliances
    ("Q17232663", "air fryer"), ("Q17209136", "toaster oven"), ("Q14890", "toaster"),
    ("Q1210743", "espresso machine"), ("Q211841", "coffee maker"), ("Q501862", "blender"),
    ("Q1126251", "food processor"), ("Q642345", "slow cooker"), ("Q1137500", "rice cooker"),
    ("Q1364042", "electric kettle"), ("Q1139975", "waffle iron"), ("Q153059", "deep fryer"), ("Q12294124", "juicer"),
    ("Q127956", "microwave oven"),
    # home appliances
    ("Q124441", "washing machine"), ("Q496334", "clothes dryer"), ("Q186263", "dishwasher"),
    ("Q182995", "kitchen stove (cooker)"), ("Q37828", "refrigerator"), ("Q1265533", "air conditioner"),
    ("Q101674", "vacuum cleaner"), ("Q1146526", "dehumidifier"), ("Q1073283", "humidifier"),
    # computers, game consoles and networks
    ("Q3962", "laptop"), ("Q155972", "tablet computer"), ("Q56155", "desktop computer"),
    ("Q16338", "personal computer"), ("Q941818", "handheld game console"), ("Q8076", "video game console"),
    ("Q5318", "router"), ("Q5290", "computer monitor"), ("Q82", "printer"), ("Q82744", "scanner"),
    # TVs and audio
    ("Q8075", "television set"), ("Q1567371", "streaming media player"), ("Q842729", "set-top box"),
    ("Q11190950", "Blu-ray player"), ("Q3783103", "DVD player"), ("Q2900397", "soundbar"),
    ("Q300126", "AV receiver"), ("Q17591720", "turntable (record player)"), ("Q275568", "video projector"),
    ("Q570", "loudspeaker"),
    # older electronics
    ("Q335234", "camcorder"), ("Q380616", "videocassette recorder (VCR)"), ("Q7231333", "portable CD player"),
    ("Q1023100", "CD player"), ("Q1358666", "boombox"), ("Q107193795", "portable cassette player"),
    ("Q510176", "cassette deck"), ("Q121552543", "cassette recorder"), ("Q568717", "answering machine"),
    ("Q1195934", "cordless telephone"), ("Q832436", "pager"), ("Q162768", "personal digital assistant (PDA)"),
    ("Q313695", "instant camera"), ("Q196353", "single-lens reflex (SLR) camera"), ("Q62927", "digital camera"),
    ("Q3928875", "clock radio"), ("Q506260", "transistor radio"), ("Q159391", "radio"), ("Q46335", "typewriter"),
    ("Q125184070", "fax machine"), ("Q185369", "photocopier"), ("Q31087", "calculator"),
    # lawn, garden and outdoor
    ("Q25056621", "riding mower"), ("Q260521", "lawn mower"), ("Q1450186", "leaf blower"), ("Q208040", "chainsaw"),
    ("Q1254365", "generator"), ("Q1545773", "pressure washer"), ("Q853185", "barbecue grill"),
    # around the house
    ("Q3045295", "carbon monoxide alarm"), ("Q565858", "smoke alarm"), ("Q5521874", "garage door opener"),
    ("Q384459", "doorbell"), ("Q26884850", "smart speaker"), ("Q1181944", "ceiling fan"), ("Q25841836", "electric fan"),
    ("Q12069731", "space heater"), ("Q1196206", "air purifier"), ("Q49013", "sewing machine"),
    ("Q483634", "iron (for clothes)"), ("Q15004", "hair dryer"), ("Q925577", "hair clipper"),
    ("Q10568696", "curling iron"), ("Q979744", "electric toothbrush"), ("Q839144", "treadmill"),
    # tools and the office
    ("Q58964", "drill"), ("Q421922", "paper shredder"), ("Q4346060", "label printer"),
    # personal electronics
    ("Q22645", "smartphone"), ("Q17517", "mobile phone"), ("Q10872571", "portable media player"),
    ("Q5362345", "smartwatch"),
    # health devices
    ("Q842840", "blood glucose meter"), ("Q503968", "blood pressure monitor"), ("Q11831723", "pulse oximeter"),
    ("Q2281580", "nebulizer"), ("Q323808", "hearing aid"),
]
# The models of one kind: items in its class tree (an instance or a subclass of it, as Wikidata files models both
# ways) that have a maker or a brand (so a general kind such as "foldable smartphone" is not taken for a model) and a
# picture or a Commons category; the best-known first (most Wikipedia articles).
DEVICE_QUERY = """SELECT ?item ?itemLabel ?cat ?image ?makerLabel ?brandLabel ?start ?kindLabel WHERE {
  { SELECT DISTINCT ?item ?sl WHERE { ?c wdt:P279* wd:%s . { ?item wdt:P31 ?c } UNION { ?item wdt:P279 ?c }
      FILTER EXISTS { ?item wdt:P176|wdt:P1716 [] } FILTER EXISTS { ?item wdt:P373|wdt:P18 [] }
      ?item wikibase:sitelinks ?sl . } ORDER BY DESC(?sl) LIMIT %d }
  OPTIONAL { ?item wdt:P373 ?cat } OPTIONAL { ?item wdt:P18 ?image }
  OPTIONAL { ?item wdt:P176 ?maker } OPTIONAL { ?item wdt:P1716 ?brand }
  OPTIONAL { ?item wdt:P571|wdt:P577|wdt:P5444 ?start } OPTIONAL { ?item wdt:P31|wdt:P279 ?kind }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }"""
# Class names that say nothing about what the device is ("product model", "consumer electronics").
GENERIC_KIND = re.compile(r"^(products?|product (model|line|family|series)|models?|brand|trademark|series|range|"
                          r"line|family|commercial object|electronic device|electronics|consumer electronics|"
                          r"home appliance|household appliance|appliance|device|machine|discontinued product|"
                          r"entry-level|computer hardware|hardware|technology|invention|object|item|"
                          r"industrial design|design)$", re.I)
# Endings that turn a model class into its kind ("camcorder model" -> "camcorder").
MODEL_WORDS = re.compile(r"^(model|type|kind) of (an? )?|\s+(model|models|product line|product family|series|range|"
                         r"line|family|variant|product)$", re.I)
# Company endings left out when an answer says who made it ("Sony Group" -> "Sony", "Canon Inc." -> "Canon").
COMPANY_ENDINGS = re.compile(r"[,\s]+(Group|Inc\.?|Incorporated|Corporation|Corp\.?|Co\.?,? Ltd\.?|Company|Ltd\.?|"
                             r"Limited|LLC|L\.L\.C\.|plc|PLC|GmbH|AG|S\.A\.|SA|S\.p\.A\.|N\.V\.|B\.V\.|K\.K\.|"
                             r"Kabushiki Kaisha|Holdings|Electronics Co\.?)$")


def company(label):
    """A maker's name as an answer says it: "Sony Group" -> "Sony", "Canon Inc." -> "Canon"."""
    name = clean(label)
    for _ in range(3):
        shorter = COMPANY_ENDINGS.sub("", name).strip(" ,")
        if shorter == name or not shorter:
            break
        name = shorter
    return name


def own_kinds(subject):
    """The kinds Wikidata itself puts a model in (its "instance of" and "subclass of" classes), with "model",
    "series" and the like taken off ("smartphone model series" -> "smartphone"), leaving out classes that say
    nothing ("product model") and brand or product-line names ("iPhone", "Canon EOS": they start with a capital)."""
    out = []
    for label in subject.get("kindLabel") or []:
        kind = clean(label)
        for _ in range(3):
            kind = MODEL_WORDS.sub("", kind).strip()
        if not kind or GENERIC_KIND.match(kind) or kind.lower() == subject["label"].lower() or \
                re.fullmatch(r"Q\d+", kind) or re.search(r"\d", kind) or \
                (kind[:1].isupper() and not re.match(r"^[A-Z]{2,}\b", kind)):
            continue
        if kind not in out:
            out.append(kind)
    return out


def kind_words(subject, default):
    """How an answer names a model's kind: the class Wikidata itself puts the model in that shares the head word of
    the kind it was found under (the shortest such: "digital camera" for a Canon EOS 600D found under SLR cameras);
    else Wikidata's own class when there is just one ("digital movie camera" for the Panavision Genesis, which
    Wikidata's class tree also puts under camcorders); else the kind it was found under ("JVC HR-3300" ->
    "videocassette recorder (VCR)")."""
    head = re.sub(r"\s*\(.*\)$", "", default).split()[-1].lower()
    kinds = own_kinds(subject)
    sharing = sorted((k for k in kinds if head in k.lower().split()), key=len)
    if sharing:
        return default if sharing[0].lower() == re.sub(r"\s*\(.*\)$", "", default).lower() else sharing[0]
    return kinds[0] if len(kinds) == 1 else default


def maker_of(subject):
    """The one maker (P176), else the one brand (P1716) Wikidata gives a model, as said in an answer; "" when it
    gives none or several."""
    for key in ("makerLabel", "brandLabel"):
        names = list(dict.fromkeys(company(m) for m in subject.get(key) or [] if not re.fullmatch(r"Q\d+", m)))
        if len(names) == 1 and names[0]:
            return names[0]
    return ""


def first_year(subject):
    """The earliest year Wikidata gives for when a model first came out, or "" (years after now are left out)."""
    years = sorted(y for y in (year_of(v) for v in subject.get("start") or []) if y.isdigit()
                   and 1850 <= int(y) <= 2026)
    return years[0] if years else ""


def model_rows(subject):
    """The rows of one Wikidata model (the same for each of its pictures): "What is this?", "What make and model is
    this?" and, when Wikidata gives a year, "About when was this made?"."""
    name, kind, maker, year = subject["label"], subject["kind"], maker_of(subject), first_year(subject)
    said_maker = maker and maker.lower().split()[0] not in name.lower()
    bare_kind = re.sub(r"\s*\(.*\)$", "", kind).lower()
    what = f"This is {a_or_an(name)} {name}" + ("" if name.lower().endswith(bare_kind) else
                                                 f", {a_or_an(kind)} {kind}") + \
        (f", made by {maker}" if said_maker and name.lower().endswith(bare_kind) else
         f" made by {maker}" if said_maker else "")
    rows = [{"question": WHAT_Q, "answer": full_stop(what) + (f" This model first came out in {year}." if year
                                                                else "")},
            {"question": MAKE_Q, "answer": full_stop(f"It is {a_or_an(name)} {name}" +
                                                      (f", made by {maker}" if said_maker else ""))}]
    if year:
        rows.append({"question": WHEN_Q, "answer": f"It is {a_or_an(name)} {name}, a model that first came out in "
                                                   f"{year}."})
    return rows


def device_picture_rows(subject, title, text):
    """The rows of one picture of a model: [] when the file is not a photo of the device seen whole (its box,
    manual, insides, parts, a drawing ...) or its words name a person or nudity."""
    words = f"{title} {text}"
    if NOT_THE_DEVICE.search(title) or NOT_THE_DEVICE.search(text) or PERSON.search(words) or NUDE.search(words) \
            or ANEFO.search(words):
        return []
    return model_rows(subject)


def device_models(s, kinds, per_kind):
    """[subject] for the kinds: each a dict as culture_packs.subjects gives it ("id", "label", "cat", "image",
    "makerLabel", "brandLabel", "start", "kindLabel"), with "kind" (how the answer names it); a model is counted
    under its first kind only."""
    taken, groups = set(), []
    for qid, phrase in kinds:
        if listing_out_of_time():
            say("  (the time for finding models is up: the kinds found so far are used)")
            break
        found = []
        for d in subjects(sparql(s, DEVICE_QUERY % (qid, per_kind))):
            if d["id"] in taken or not (d.get("cat") or d.get("image")) or d["label"].lower() == phrase.lower():
                continue
            taken.add(d["id"])
            d["kind"] = kind_words(d, phrase)
            found.append(d)
        say(f"Wikidata {phrase}: {len(found)} models")
        groups.append(found)
        time.sleep(1)
    return groups


def build_wikidata_devices(limit):
    """The Wikidata device models pack: every kind of DEVICE_KINDS in turn, a model at a time, up to two free
    pictures of each (its Wikidata picture first, then its Commons category)."""
    s, rng = session(), pass_random(5381)
    per_kind = max(10, min(150, limit // 20 + 5))
    groups = device_models(s, DEVICE_KINDS, per_kind)
    chosen = round_robin(groups, rng)
    entries = from_subjects("wikidata_devices", s, chosen, limit, device_picture_rows, per_subject=2, rng=rng)
    return english_captions_only(entries)


def english_captions_only(entries):
    """The pack entries without the file captions that are not in English (culture_packs.from_subjects adds each
    file's caption as "Describe this picture."; an Italian or German caption is left out, as no translation is made
    here). A caption is never a picture's first row, so no picture is lost."""
    return [(name, data, row) for name, data, row in entries
            if row.get("question") != "Describe this picture." or len(ENGLISH_WORDS.findall(row["answer"])) >= 2]


# ----------------------------------------------------------------- commons_devices

def device(category, answer, deeper=False):
    """A Commons device category: (category, look in its subcategories too, the answer to "What is this?")."""
    return (category, deeper, answer)


# Only kinds no other pack's Commons categories have (see the module docstring); every category was checked to exist
# on Commons in November 2026. The answer says what the category says, with one short plain line about the kind.
COMMONS_DEVICES = [
    # small kitchen appliances
    device("Coffee machines", "This is a coffee machine (coffee maker), which brews coffee."),
    device("Food mixers", "This is a food mixer, which mixes and beats food such as cake batter."),
    device("Bread machines", "This is a bread machine, which mixes, rises and bakes a loaf of bread."),
    device("Toaster ovens", "This is a toaster oven: a small countertop oven that toasts, bakes and grills."),
    device("Deep fryers", "This is a deep fryer, which cooks food in hot oil."),
    device("Popcorn makers", "This is a popcorn maker."),
    device("Ice cream makers", "This is an ice cream maker."),
    device("Food dehydrators", "This is a food dehydrator, which dries fruit, vegetables and meat."),
    device("Multicookers", "This is a multicooker (an electric pressure cooker and slow cooker in one)."),
    # home appliances
    device("Refrigerators", "This is a refrigerator (fridge).", True),
    device("Chest freezers", "This is a chest freezer: a freezer with a lid on top."),
    device("Freezers", "This is a freezer."),
    device("Wine coolers", "This is a wine cooler, a small fridge for wine bottles."),
    device("Water coolers", "This is a water cooler, which gives chilled drinking water."),
    device("Front-loading washing machines", "This is a front-loading washing machine: the door is on the front."),
    device("Top-loading washing machines", "This is a top-loading washing machine: the lid is on top."),
    device("Air conditioners", "This is an air conditioner, which cools the air in a room."),
    device("Portable air conditioners", "This is a portable air conditioner, which stands on the floor and blows "
                                        "warm air out through a hose."),
    device("Vacuum cleaners", "This is a vacuum cleaner.", True),
    device("Robotic vacuum cleaners", "This is a robot vacuum cleaner, which moves around the floor on its own."),
    device("Dehumidifiers", "This is a dehumidifier, which takes damp out of the air."),
    device("Humidifiers", "This is a humidifier, which adds moisture to the air."),
    # computers, consoles and networks
    device("Home computers", "This is a home computer.", False),
    device("All-in-one computers", "This is an all-in-one computer: the computer is built into the screen."),
    device("Computer monitors", "This is a computer monitor (screen)."),
    device("Routers", "This is a router, which connects computers and other devices to a network or the "
                      "internet."),
    device("Network switches", "This is a network switch, which connects computers with network cables."),
    device("Inkjet printers", "This is an inkjet printer."),
    device("Laser printers", "This is a laser printer."),
    device("Scanners", "This is a scanner, which copies pages and photos into a computer."),
    device("Xbox consoles", "This is an Xbox games console, made by Microsoft.", True),
    device("Nintendo consoles", "This is a Nintendo games console.", True),
    # TVs and audio
    device("Television sets", "This is a television set.", True),
    device("Television receivers", "This is a television set."),
    device("Set-top boxes", "This is a set-top box, which connects a television to cable, satellite or the "
                            "internet."),
    device("Digital media players", "This is a streaming media player, which plays films and programmes from the "
                                    "internet on a television."),
    device("DVD players", "This is a DVD player."), device("Blu-ray players", "This is a Blu-ray player."),
    device("Soundbars", "This is a soundbar: a long, thin speaker that sits under a television."),
    device("AV receivers", "This is an AV receiver (amplifier) for a home cinema or stereo."),
    device("Record players", "This is a record player (turntable)."),
    device("Turntables", "This is a turntable (record player)."),
    device("Boomboxes", "This is a boombox: a portable stereo with a radio and a cassette or CD player."),
    device("Bluetooth speakers", "This is a portable Bluetooth speaker."),
    device("Amazon Echo", "This is an Amazon Echo smart speaker."),
    device("Google Home", "This is a Google Home smart speaker."),
    device("Smart speakers", "This is a smart speaker, which answers spoken questions and plays music."),
    # older electronics
    device("VHS recorders", "This is a VHS video recorder (VCR), which records and plays VHS video tapes."),
    device("Camcorders", "This is a camcorder: a video camera that records onto a tape, disc or card."),
    device("Cassette decks", "This is a cassette deck, which plays and records audio cassettes."),
    device("Tape recorders", "This is a tape recorder."),
    device("Portable cassette players", "This is a portable cassette player."),
    device("Sony Walkman cassette players", "This is a Sony Walkman, a portable cassette player.", True),
    device("Sony Discman", "This is a Sony Discman, a portable CD player.", True),
    device("Sony MD Walkman", "This is a Sony MiniDisc Walkman, a portable MiniDisc player."),
    device("Portable CD players", "This is a portable CD player."),
    device("CD players", "This is a CD player."),
    device("MiniDisc", "This is a MiniDisc or a MiniDisc player (MiniDisc is a small recordable disc in a case, "
                       "from the 1990s)."),
    device("Answering machines", "This is a telephone answering machine, which records messages from callers."),
    device("Cordless telephones", "This is a cordless telephone: a home phone whose handset works away from its "
                                  "base."),
    device("Rotary dial telephones", "This is a rotary dial telephone: you dial each number by turning the dial."),
    device("Push-button telephones", "This is a push-button telephone."),
    device("Pagers", "This is a pager (beeper), which shows short messages and numbers sent to it."),
    device("Personal digital assistants", "This is a personal digital assistant (PDA), a handheld computer "
                                          "from before smartphones."),
    device("Film cameras", "This is a film camera."),
    device("Instant cameras", "This is an instant camera, which prints the photo straight away."),
    device("Polaroid cameras", "This is a Polaroid instant camera."),
    device("Clock radios", "This is a clock radio: an alarm clock with a radio."),
    device("Electric typewriters", "This is an electric typewriter."),
    device("Fax machines", "This is a fax machine, which sends and receives copies of pages over a phone line."),
    device("Digital audio players", "This is a digital music player (MP3 player)."),
    device("IPod", "This is an Apple iPod, a portable music player."),
    device("E-readers", "This is an e-reader, for reading electronic books."),
    # lawn, garden and outdoor
    device("Lawn tractors", "This is a lawn tractor (a riding lawn mower)."),
    device("Robotic lawn mowers", "This is a robot lawn mower, which mows the grass on its own."),
    device("Reel mowers", "This is a reel mower (cylinder mower), a push mower with spinning blades."),
    device("Electric lawn mowers", "This is an electric lawn mower."),
    device("String trimmers", "This is a string trimmer (strimmer, weed eater), which cuts grass with a spinning "
                              "nylon line."),
    device("Leaf blowers", "This is a leaf blower."),
    device("Hedge trimmers", "This is a hedge trimmer."),
    device("Snow blowers", "This is a snow blower, which throws snow off paths and driveways."),
    device("Engine-generators", "This is a generator, which makes electricity from an engine."),
    device("Pressure washers", "This is a pressure washer, which cleans with a strong jet of water."),
    device("Rototillers", "This is a rototiller (tiller), which digs and turns over garden soil."),
    device("Gas grills", "This is a gas barbecue grill."),
    device("Barbecues", "This is a barbecue grill."),
    # around the house
    device("Carbon monoxide detectors", "This is a carbon monoxide alarm."),
    device("Garage door openers", "This is a garage door opener."),
    device("Doorbells", "This is a doorbell."),
    device("Desk fans", "This is a desk fan."), device("Box fans", "This is a box fan."),
    device("Electric fans", "This is an electric fan."),
    device("Ceiling fans", "This is a ceiling fan."),
    device("Electric heaters", "This is an electric heater."), device("Fan heaters", "This is a fan heater."),
    device("Space heaters", "This is a space heater, which heats one room."),
    device("Air purifiers", "This is an air purifier, which cleans the air in a room."),
    device("Sewing machines", "This is a sewing machine.", True),
    device("Singer sewing machines", "This is a Singer sewing machine."),
    device("Electric irons", "This is an electric iron, for ironing clothes."),
    device("Hairdryers", "This is a hair dryer."),
    device("Hair irons", "This is a hair straightener (hair iron)."),
    device("Curling irons", "This is a curling iron (curling tongs)."),
    device("Electric shavers", "This is an electric shaver."),
    device("Hair clippers", "This is a pair of hair clippers."),
    device("Electric toothbrushes", "This is an electric toothbrush."),
    device("Treadmills", "This is a treadmill (running machine)."),
    device("Stationary bicycles", "This is an exercise bike."),
    device("Electric blankets", "This is an electric blanket."),
    # power tools and the office
    device("Table saws", "This is a table saw."), device("Miter saws", "This is a mitre saw."),
    device("Reciprocating saws", "This is a reciprocating saw."),
    device("Impact drivers", "This is an impact driver."),
    device("Nail guns", "This is a nail gun."), device("Air compressors", "This is an air compressor."),
    device("Photocopiers", "This is a photocopier."), device("Paper shredders", "This is a paper shredder."),
    device("Calculators", "This is a calculator."), device("Label printers", "This is a label printer (label maker)."),
    device("Laminators", "This is a laminator."), device("Overhead projectors", "This is an overhead projector."),
    device("Pencil sharpeners", "This is a pencil sharpener."),
    # personal electronics and health
    device("Headphones", "These are headphones."), device("Earphones", "These are earphones."),
    device("Wireless earbuds", "These are wireless earbuds."),
    device("GPS navigation devices", "This is a GPS navigation device (satnav)."),
    device("Activity trackers", "This is an activity tracker (fitness band)."),
    device("Pulse oximeters", "This is a pulse oximeter, which clips on a finger to measure the pulse and the "
                              "oxygen in the blood."),
    device("Nebulizers", "This is a nebulizer, which turns liquid medicine into a mist to breathe in."),
]


def device_items(s, specs, limit, prefix):
    """[(file name, picture address, rows)] from Commons device categories, as home_packs.build_commons_topic does
    (the categories take turns, so each gets an even share; CC0, public domain and CC BY files only), leaving out
    files that are not a photo of the device itself or whose words name a person or nudity; a real, respectful
    caption also gives "Write a short description ..."."""
    import math
    items, seen = [], set()
    order = list(specs)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    queues = [[category, deeper, answer, None] for category, deeper, answer in order]
    want, rounds = int(limit * 1.15) + 2, 0
    while len(items) < want and queues and rounds < 50 and not listing_out_of_time():
        rounds += 1
        for q in list(queues):
            if len(items) >= want or listing_out_of_time():
                break
            category, deeper, answer, titles = q
            if titles is None:
                titles = [t for t in category_files(s, category, deeper) if t not in seen]
                pass_random(category).shuffle(titles)
                say(f"Commons {category}: {len(titles)} files")
            batch, q[3] = titles[:share * 2], titles[share * 2:]
            if not batch:
                queues.remove(q)
                continue
            got = 0
            for title, url, credit, text in home_entries(s, batch):
                rows = commons_rows(title, text, answer, credit)
                if got >= share or title in seen or not rows:
                    continue
                seen.add(title)
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[3]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    return items[:want]


def commons_rows(title, text, answer, credit):
    """The rows of one Commons device file: "What is this?" with the category's answer and, when the file has a
    real, respectful caption, "Write a short description ..." with it; [] when it is not a photo of the device itself
    or its words name a person or nudity. Rows whose words name a child are marked "child"."""
    words = f"{title} {text}"
    if NUDE.search(words) or PERSON.search(words) or NOT_THE_DEVICE.search(title) or ANEFO.search(words):
        return []
    place = where(COMMONS_PLACES.get(title, ""))
    rows = [mark_child({"question": WHAT_Q, "answer": answer, "credit": credit, **place}, words)]
    if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text) and \
            len(ENGLISH_WORDS.findall(text)) >= 2 and \
            set(re.findall(r"[a-z]+", text.lower())) - set(re.findall(r"[a-z]+", title.lower())):
        rows.append(mark_child({"question": ALT_TEXT, "answer": text, "credit": credit, **place}, words))
    return rows


def build_commons_devices(limit):
    """The Commons household devices pack."""
    items = device_items(session(), COMMONS_DEVICES, limit, "device")
    fetched = commons_fetch(items)[:limit]
    say(f"commons_devices: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- nmah_devices

# The object types that are household devices (the record's own "object type" words), with how an answer names them.
NMAH_DEVICES = [
    (r"sewing machine|machine,? sewing", "a sewing machine"), (r"typewriter", "a typewriter"),
    (r"phonograph|graphophone|gramophone|talking machine", "a phonograph"), (r"toaster", "a toaster"),
    (r"waffle iron|iron,? waffle|wafer iron|iron,? wafer", "a waffle iron"),
    (r"sad ?iron|flat ?iron|iron,? (coal|charcoal|electric|gas|sad|flat|box|smoothing)|clothes iron|"
     r"electric iron|smoothing iron", "an iron (for clothes)"),
    (r"stove|range,? (gas|electric|kitchen)|cookstove", "a stove"), (r"heater", "a heater"),
    (r"\bfans?\b|fan,? electric|electric fan", "an electric fan"),
    (r"washing machine|washer,? clothes", "a washing machine"),
    (r"refrigerator|icebox|ice box", "a refrigerator"), (r"vacuum cleaner|cleaner,? vacuum", "a vacuum cleaner"),
    (r"telephone", "a telephone"), (r"radio(?! detector)|receiver,? radio", "a radio"), (r"television", "a television"),
    (r"camera(?! lucida)", "a camera"), (r"mixer(?!,? drink)|blender", "a food mixer"),
    (r"coffee ?(maker|pot|percolator)|percolator", "a coffee maker"),
    (r"calculat(or|ing machine)|adding machine|\badder\b", "a calculating machine"), (r"computer", "a computer"),
    (r"video ?(cassette )?recorder|vcr\b", "a video recorder (VCR)"), (r"tape recorder|cassette", "a tape recorder"),
    (r"hair ?dryer|hair drier", "a hair dryer"), (r"razor,? electric|electric (razor|shaver)", "an electric razor"),
    (r"clock radio", "a clock radio"), (r"appliance", "a household appliance"),
]
NMAH_DEVICES = [(re.compile(r"\b(" + p + r")", re.I), said) for p, said in NMAH_DEVICES]
# Object types that are pictures or papers about a device, not the device.
NMAH_NOT_DEVICE = re.compile(r"\b(photograph\w*|print|prints|lithograph|cyanotype|collotype|platinum|halftone|"
                             r"sketch\w*|drawing|engraving|trade (catalog|literature)|advertis\w*|book|manuscript|"
                             r"sheet music|letter|postcard|poster|card|label|patent (drawing|document)|negative|"
                             r"glass plate|stereograph|film|phonorecord|record|token|medal|tablets?)\b", re.I)


def nmah_kind(object_type):
    """How an answer names the device an NMAH object type is ("sewing machine patent model" -> "a sewing machine"),
    with whether it is a patent model; ("", False) when it is not a household device of this pack."""
    if not object_type or NMAH_NOT_DEVICE.search(object_type):
        return "", False
    said = next((said for pattern, said in NMAH_DEVICES if pattern.search(object_type)), "")
    return said, bool(said) and bool(re.search(r"patent model", object_type, re.I))


def nmah_title_answer(title, kind, patent):
    """ "What is this?" from the record's title and kind: "This is a toaster." when the title only names the kind,
    else "This is a sewing machine patent model, catalogued as "1851 - Isaac Singer's Sewing Machine Patent
    Model"."."""
    bare = re.sub(r"^an? ", "", kind)
    what = f"{kind} patent model (a small working model made for a patent)" if patent else kind
    if clean(title).lower().rstrip(".") in (bare, re.sub(r"\s*\(.*\)$", "", bare)):
        return f"This is {what}."
    return f"This is {what}, catalogued by the museum as \"{clean(title).rstrip('.')}\"."


def nmah_device_rows(record):
    """(picture addresses, rows) of an NMAH record with CC0 pictures of a household device, or None: "What is this?",
    "Tell me about this museum object." with its description and "About when was this made?" when it says. A record
    whose description is under twelve words is set aside for a description (needs_description)."""
    content = record.get("content", {})
    pictures = si_media(content, 2)
    if not pictures:
        return None
    free = content.get("freetext", {})
    object_type = " | ".join(clean(t.get("content")) for t in free.get("objectType") or [])
    title = clean(record.get("title"))
    kind, patent = nmah_kind(object_type)
    if not kind or not title:
        return None
    text = first_sentences(si_notes(content, ("Description", "Description (Brief)", "General History",
                                              "Physical Description")), 90)
    text = re.sub(r"\b(Physical Description|General History|Description \(Brief\)|Specifications|Markings)\b:?\s*",
                  "", text).strip()
    text = text.replace("â\x80\x99", "’").replace("â\x80\x9c", "“").replace("â\x80\x9d", "”")
    words = f"{title} {text} {object_type}"
    if NUDE.search(words):
        return None
    link = content.get("descriptiveNonRepeating", {}).get("record_link") or record.get("id", "")
    credit = f"{title}, National Museum of American History, Smithsonian Institution, CC0, {link}"
    places = {clean(p.get("label")).lower(): p.get("content") for p in free.get("place") or []}
    place = where(place_from_text(places.get("place made") or ""), "origin") if places.get("place made") else {}
    made = next((clean(d.get("content")) for d in free.get("date") or []
                 if not d.get("label") or "made" in clean(d.get("label")).lower()), "")
    when = when_words(made)
    if len(text.split()) < 12:                  # a free picture of a device whose description is too short: set aside
        needs_description(f"nmah-device-{record.get('id', '')}-0.jpg", pictures[0], credit, "CC0", text=text,
                          title=title, page_url=link, reason="its description is under twelve words",
                          extra={"object_type": object_type, "device": kind, "date": made, "child": bool(
                              CHILD.search(words))})
        return None
    rows = [{"question": WHAT_Q, "answer": nmah_title_answer(title, kind, patent), "credit": credit, **place},
            {"question": MUSEUM, "answer": full_stop(text if title.lower() in text.lower() else f"{title}. {text}"),
             "credit": credit, **place}]
    if when:
        rows.append({"question": WHEN_Q, "answer": f"The museum dates it {when}.".replace("dates it in ",
                                                                                         "dates it to "),
                     "credit": credit, **place})
    return pictures, [mark_child(r, words) for r in rows]


def build_nmah_devices(limit):
    """The nmah_devices pack: NMAH's bulk files (about 2.5 GB, read one file at a time in random order) until enough
    CC0 records of household devices are found, or the listing time is up."""
    s, items = session(), []
    keys = si_keys("nmah")
    pass_random(97).shuffle(keys)
    for key in keys:
        if len(items) >= limit * 1.3 or listing_out_of_time():
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            got = nmah_device_rows(record)
            if got:
                pictures, rows = got
                for n, url in enumerate(pictures):
                    items.append((f"nmah-device-{record.get('id', len(items))}-{n}.jpg", url, rows))
    say(f"NMAH: {len(items)} pictures of household devices")
    return finish("nmah_devices", items, limit, workers=4, pause=0.1)


# ----------------------------------------------------------------- the packs

DEVICE_PACKS = {
    "wikidata_devices": (build_wikidata_devices,
                         "Wikidata (CC0, https://www.wikidata.org/wiki/Wikidata:Licensing): product models of "
                         "household devices, their kind, maker or brand and the year they first came out. Pictures "
                         "from Wikimedia Commons, CC0, public domain or CC BY, each with its author and file page "
                         "below; captions CC0. Changes: pictures made smaller; answers written from Wikidata's "
                         "statements."),
    "commons_devices": (build_commons_devices,
                        "Wikimedia Commons household device categories: captions CC0; pictures CC0, public domain or "
                        "CC BY, each with its author and file page below. https://commons.wikimedia.org. Changes: "
                        "pictures made smaller; answers written from the category names."),
    "nmah_devices": (build_nmah_devices,
                     "Smithsonian National Museum of American History, Smithsonian Open Access, CC0 "
                     "(https://www.si.edu/openaccess): records and pictures of household devices, each record "
                     "credited below. Changes: pictures made smaller; descriptions shortened to their first "
                     "sentences."),
}

# How many pictures a full build takes from each (about what each offers after the checks, kept so that every pack
# finishes well within the build's time on GitHub).
DEVICE_LIMITS = {
    "wikidata_devices": 3000,     # about 100 kinds, up to 150 models each, two pictures a model at most
    "commons_devices": 2500,      # about 130 categories, about 20 pictures each
    "nmah_devices": 150,          # about 1 in 100 NMAH records is CC0; about 150 of them are household devices
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one household device pack builder.")
    parser.add_argument("key", choices=sorted(DEVICE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = DEVICE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    questions = collections.Counter(row["question"] for _, _, row in entries)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"questions: " + ", ".join(f"{q} {n}" for q, n in questions.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
