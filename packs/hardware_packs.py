"""Pack builders for HARDWARE, TOOLS AND SHOP EQUIPMENT: fasteners, door, cabinet and window hardware, building and
shelf hardware, plumbing and electrical parts, building materials and shop supplies, hand tools and trade tools, power
tools and outdoor power equipment, woodshop and metal shop machines and welding, personal protective equipment,
sewing and food-preparation equipment, Amazon Berkeley Objects' hardware and tool listings, and the Smithsonian's
historic locks, hinges and tools. Used by build_packs.py in the same way as its own PACKS: each builder is
build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"}, plus "place" where the source states one, "child": true where the words of a picture name a child, and
"facts" (the Commons category a file was found in, its title, and the features read from its categories), kept for
later uses. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

WHAT THE ANSWERS SAY, AND WHERE IT COMES FROM. The picture describer should be able to name a part and its key
features: for a screw or bolt its head type, drive type, thread, material and finish, and its size where stated.
Every answer is a fixed sentence written here from the source's own words; nothing is written by an AI model and
nothing is guessed:
  - the KIND of part ("a carriage bolt", "a butt hinge", "a jointer") comes from the Commons category the file sits
    in (the most specific one: a file in "Carriage bolts" is a carriage bolt, not just "a bolt"), with one short
    generic line on what it is for, written here (KINDS tables);
  - each FEATURE (head, drive, thread, material, finish) comes from the names of the file's own Commons categories
    ("Countersunk screws", "Torx", "Stainless steel screws") or plain words of its own title ("phillips",
    "stainless", "galvanized"): FEATURES below. When two of a file's categories give two different answers for one
    feature (a photo in both "Phillips screws" and "Torx"), that feature is not said;
  - a SIZE is said only where the file's own title names a fastener and states its size in a standard form (a
    metric thread "M8 x 40", a penny size "16d", a screw gauge "#8", a length in millimetres or inches), and then
    only as "The file's title gives the size: ...". Never estimated from the picture;
  - ABO listings: the product's own name, brand, colour, material and finish, and sizes only where the name states
    them;
  - the Smithsonian's records: the object's own name, maker, date, place and materials as catalogued.
No installation or repair instructions are given in the packs (those are in the manuals library); safety equipment
and ladder answers carry one plain safety line.

The packs (all open: CC0, public domain or CC BY, checked file by file; CC BY 4.0 for ABO):
  commons_fasteners           Wikimedia Commons: nails by kind (common, finishing, roofing, brads, cut, ring-shank,
                              masonry), screws by kind (wood, deck, drywall, self-tapping, self-drilling, machine,
                              set, socket cap, thumb, confirmat, security), by head (countersunk, pan, dome, cheese,
                              fillister, truss, hex, square, flanged) and by drive (Phillips, Pozidriv, slotted, Torx,
                              square/Robertson, hex socket, tri-wing, security), bolts (carriage, hex, lag, eye, U,
                              J, anchor, T, structural, hanger), nuts (hex, lock, nyloc, wing, cap/acorn, castle,
                              flange, square, T, coupling, rivet), washers (flat, lock, fender, Belleville),
                              anchors (wall plugs, toggle and molly bolts, wedge and sleeve anchors), rivets, staples,
                              threaded rod, cotter, clevis, linch and hitch pins, hose clamps, cable ties, and
                              thread and pitch gauges. Files already asked about by home_packs commons_tools and
                              mechanical_packs commons_machine_parts are left out (EXISTING).
  commons_door_hardware       Commons: hinges (butt, piano, concealed/European, strap, spring, T, pivot), door
                              handles, knobs and levers, deadbolts and locks, padlocks, keys, strike plates, door
                              closers, hasps, latches and catches, door bolts, door stops, door viewers, door
                              knockers, letter plates, weatherstripping; cabinet and furniture hardware (pulls,
                              knobs, drawer slides, cam locks, dowels, shelf supports, flat-pack fittings); window
                              hardware (locks, cranks and operators, sash fasteners, insect screens).
  commons_building_hardware   Commons: brackets, joist hangers and structural connectors, corner braces, truss
                              plates, shelf standards and pins, picture hangers, hooks, chain, wire rope, rope and
                              knots, shackles, turnbuckles, carabiners, pulleys and blocks, casters, springs, fence
                              and gate hardware, garage door parts and openers, mailboxes and house numbers.
  commons_plumbing_electrical Commons: pipe fittings (elbows, tees, couplings, unions, reducers, caps, PEX, PVC,
                              copper, compression, push-fit, press), valves (shut-off, ball, gate, stop), P-traps,
                              faucets, toilet parts (fill valves, flappers, flush valves), electrical boxes, outlets
                              and switches, cover plates, wire nuts and connectors, breakers and panels, cable and
                              wire types (NM/Romex, THHN, armoured, coaxial), extension cords, and NEMA plug and
                              socket types not in home_packs commons_connectors.
  commons_building_materials  Commons: lumber and timber, plywood, OSB, MDF, particle board, pressure-treated wood,
                              drywall, pipe and tube materials (copper, PVC, PEX, steel, cast iron, ABS), tapes (duct,
                              electrical, masking and painter's, PTFE plumber's), sandpaper, glues and adhesives,
                              caulk, wire and cable spools.
  commons_hand_tools_trades   Commons: hand tools commons_tools and things_packs commons_things do not ask about
                              (hammers by type, screwdriver bits, wrenches by type, sockets and ratchets, pliers by
                              type, saws by type, planes, files and rasps, clamps, squares, levels, pry bars, staple
                              guns, stud finders, testers, calipers, micrometers), automotive shop tools (jacks, jack
                              stands, creepers, OBD scanners, impact wrenches, battery chargers, tyre tools, engine
                              hoists), HVAC, plumbing and electrical trade tools (manifold gauges, drain augers, pipe
                              cutters and threaders, tube benders, conduit benders, fish tapes, wire strippers,
                              crimpers, clamp meters), masonry, concrete, tile, painting and drywall tools, ladders
                              and scaffolding (with a safety line), material handling (hand trucks, dollies, come-
                              alongs, hoists), and accessible tools where Commons has them.
  commons_power_tools         Commons: drills and impact drivers, circular, mitre, table, jig, reciprocating and band
                              saws, sanders, routers, grinders, nail guns, oscillating and rotary tools, heat guns,
                              air compressors and air tools, pressure washers, wet/dry vacuums, blades and bits shown
                              alone, and outdoor power equipment (chainsaws, string trimmers, leaf blowers, edgers,
                              tillers, log splitters, snow blowers, generators, chipper-shredders).
  commons_shop_machines       Commons: woodshop machines (jointers, planers, table saws, band saws, drill presses,
                              lathes and turning tools, scroll saws, spindle, belt and disc sanders, router tables,
                              dust collectors, mortisers, shapers, CNC routers, laser cutters, workbenches and vices,
                              dovetail and pocket-hole jigs) and metal shop machines (metal lathes, milling machines,
                              end mills, chucks, collets, surface grinders, bench grinders, cold and band saws, brakes,
                              shears, rollers, punches, anvils, forges, welders by process, plasma cutters, welding
                              helmets, taps and dies, dial indicators, height gauges, hydraulic presses).
  commons_ppe                 Commons: respirators (N95, half and full face, powered), dust masks, hearing protection,
                              safety glasses and goggles, face shields, hard hats, gloves by type, high-visibility
                              clothing, safety footwear and fall protection harnesses, each with one plain line on
                              what it protects against (never a promise that it is enough).
  commons_sewing_food_equipment  Commons: sewing machines, sergers, cutting tools (rotary cutters, shears, pinking
                              shears), sewing notions; and food-preparation equipment that home_packs commons_kitchen
                              does not ask about (meat slicers, stand mixers, commercial mixers, sous-vide cookers,
                              food processors, meat grinders, vacuum sealers, commercial ovens and fryers).
  abo_hardware                Amazon Berkeley Objects (CC BY 4.0): the door, cabinet and bathroom hardware, locks,
                              hooks, tools and tool sets, ladders and protective equipment listings (these product
                              types are taken from things_packs abo_products, ABO_HARDWARE_TYPES, so no listing is
                              in both). "What is this?" -> "This is a cabinet knob by AmazonBasics. Its listing calls
                              it: ... Finish: satin nickel. Size (from its listing): 1.44 inch diameter. A pack of
                              25." and "What finish is this?", "What size is it?" where the listing says.
  nmah_hardware_tools         The Smithsonian's National Museum of American History open-access records (CC0, the
                              open-access bucket): locks, padlocks, keys, hinges, latches, door knockers, hardware and
                              hand tools with a CC0 picture, named from the record ("This is a padlock, made by ...
                              in ..., about 1850. Its record gives its materials: brass, iron.").

Looked at and not built here (the reasons are in training-kit/kit/hardware_sources.py, with the share-alike Commons
files and the sign-up datasets): Open Images (its hardware and tool classes are already asked about by
everyday_packs and home_packs), McMaster-Carr and other catalogues (copyrighted pictures), Cooper Hewitt (its pictures
are not in the Smithsonian open-access bucket), Roboflow and Kaggle fastener sets (sign-up).

    python packs/hardware_packs.py commons_fasteners --limit 8      (prints a few rows: a quick check)
"""

import collections
import csv
import gzip
import io
import json
import math
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, needs_description, pass_random
from build_packs import fetch_all, SI_BUCKET, si_keys
from food_packs import with_twins, count_pictures, commons_members
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import (mech_entries, in_english, answer_for, capital, PLACES, JUST_A_RECORD, NOT_A_CHILD,
                              NOT_A_PHOTO)
from us_packs import file_categories
from places import where, country_named

WHAT_Q = "What is this?"
TOOL_Q = "What tool is this, and what is it used for?"
HEAD_Q = "What kind of head does it have?"
DRIVE_Q = "What screwdriver or bit does it take?"
THREAD_Q = "What kind of thread does it have?"
MATERIAL_Q = "What is it made of, and what is its finish?"
SIZE_Q = "What size is it?"
FINISH_Q = "What finish is this?"
DESCRIBE_Q = "Describe this picture."
FEATURE_QUESTIONS = {"head": HEAD_Q, "drive": DRIVE_Q, "thread": THREAD_Q}

# Lines added to answers about safety equipment and ladders (never a promise of protection).
PPE_LINE = ("Check its label and fit, and that it is the right kind for the job; it protects only when worn "
            "correctly.")
LADDER_LINE = ("Read the ladder's safety labels: they give its weight rating and how to set it up; never stand on the "
               "top step or cap.")


# ----------------------------------------------------------------- the rules: kinds and features

def kind(pattern, name, purpose=None, question=WHAT_Q, line=None):
    """One kind rule: a regular expression on a Commons category's name, the part's name (said after "This is"),
    a short line on what it is for (or None), the question asked, and a safety line added at the end (or None)."""
    return (re.compile(pattern, re.I), name, purpose, question, line)


def tool(pattern, name, purpose=None, line=None):
    """A kind rule for a tool ("What tool is this, and what is it used for?")."""
    return kind(pattern, name, purpose, TOOL_Q, line)


# Features read from category names and file titles: (pattern, feature, value). The value is said as it stands
# ("It has a countersunk (flat) head."; "It takes a Phillips (cross-shaped) screwdriver or bit.").
FEATURES = [(re.compile(p, re.I), f, v) for p, f, v in [
    # heads
    (r"\bcountersunk\b|\bflat[- ]head (screw|bolt)s?\b", "head", "a countersunk (flat) head, which sits flush with "
                                                             "the surface"),
    (r"\boval[- ]head\b|\braised countersunk\b", "head", "an oval (raised countersunk) head"),
    (r"\bpan[- ]head\b", "head", "a pan head: low, with a flat top and rounded edges"),
    (r"\b(dome|button)[- ]?head\b|\bround[- ]head\b", "head", "a round (dome) head"),
    (r"\bcheese[- ]head\b", "head", "a cheese head: a short cylinder with a flat top"),
    (r"\bfillister[- ]head\b", "head", "a fillister head: a tall cylinder with a rounded top"),
    (r"\btruss[- ]head\b", "head", "a truss head: wide and low"),
    (r"\bbugle[- ]head\b", "head", "a bugle head, curved underneath (as on drywall screws)"),
    (r"\bwafer[- ]head\b|\bwasher[- ]head\b", "head", "a wide, thin wafer head"),
    (r"\bflange(d)?[- ]head\b|\bhex flange\b", "head", "a flanged head with a built-in washer"),
    (r"\bsocket head cap\b|\bsocket cap\b", "head", "a socket cap head: a tall round head"),
    (r"\bhex(agon(al)?)?[- ]head\b|\bhex external\b|\bexternal hex\b", "head", "a hex (six-sided) head, turned "
                                                                                "with a spanner or socket"),
    (r"\bsquare[- ]head\b", "head", "a square head, turned with a spanner"),
    (r"\bheadless\b|\bgrub screws?\b", "head", "no head: it sinks below the surface"),
    # drives
    (r"\bphillips\b", "drive", "a Phillips (cross-shaped) screwdriver or bit"),
    (r"\bpozi(driv|drive)?\b", "drive", "a Pozidriv screwdriver or bit (a cross with extra small lines)"),
    (r"\bslot(ted)?[- ](screw|head|drive)s?\b|\bslotted\b", "drive", "a flat (slotted) screwdriver"),
    (r"\bsecurity torx\b|\btamper[- ]resistant torx\b|\btorx tr\b|\bpin[- ]in[- ]star\b", "drive",
     "a security Torx bit (a six-point star with a pin in the middle)"),
    (r"\btorx\b|\bhexalobular\b|\bstar drive\b", "drive", "a Torx (six-point star) screwdriver or bit"),
    (r"\brobertson\b|\bsquare drive\b|\bsquare (socket|recess)\b", "drive", "a square (Robertson) screwdriver or "
                                                                            "bit"),
    (r"\bhex (socket|key|drive)\b|\binternal hex\b|\ballen\b|\bhex socket\b|\bsocket head\b", "drive",
     "a hex key (Allen key) or hex bit"),
    (r"\btri[- ]?wing\b", "drive", "a tri-wing bit (three slots)"),
    (r"\bspanner (head|drive)\b|\bsnake[- ]eye\b", "drive", "a spanner (snake-eye) bit with two pins"),
    (r"\btorq[- ]set\b", "drive", "a Torq-set bit"),
    (r"\bone[- ]way (screws?|drive)\b", "drive", "nothing to undo it: it is a one-way screw that only turns in"),
    (r"\bpentalobe\b", "drive", "a pentalobe (five-point) bit"),
    (r"\bfrearson\b", "drive", "a Frearson (sharp cross) screwdriver"),
    # threads
    (r"\bdouble[- ]thread", "thread", "a double thread (two threads side by side)"),
    (r"\bfine[- ]thread", "thread", "a fine thread"),
    (r"\bcoarse[- ]thread", "thread", "a coarse thread"),
    (r"\bleft[- ]hand(ed)? thread", "thread", "a left-hand thread (it tightens anticlockwise)"),
    (r"\bself[- ]tapping\b|\bthread[- ]forming\b|\bthread[- ]cutting\b", "thread", "a self-tapping thread that "
                                                                                   "cuts its own way in"),
    (r"\bself[- ]drilling\b|\btek screws?\b", "thread", "a drill point and a self-tapping thread"),
    (r"\bmachine screws?\b|\bmachine thread", "thread", "a machine thread, for a nut or a tapped hole"),
    # materials
    (r"\bstainless( steel)?\b|\binox\b", "material", "stainless steel"),
    (r"\bbrass\b", "material", "brass"), (r"\bbronze\b", "material", "bronze"),
    (r"\bcopper\b", "material", "copper"), (r"\balumin(i)?um\b", "material", "aluminium"),
    (r"\btitanium\b", "material", "titanium"), (r"\bnylon\b", "material", "nylon"),
    (r"\bplastic\b|\bpolyamide\b|\bpvc\b", "material", "plastic"), (r"\bcast iron\b", "material", "cast iron"),
    (r"\bwrought iron\b", "material", "wrought iron"), (r"\bwooden\b|\bwood (nails|pegs)\b", "material", "wood"),
    # finishes
    (r"\bgalvani[sz]ed\b|\bhot[- ]dip\b", "finish", "galvanized (zinc-coated against rust)"),
    (r"\bzinc[- ]plated\b|\bzinc[- ]coated\b|\bzinced\b", "finish", "zinc-plated"),
    (r"\bblack oxide\b", "finish", "black oxide"), (r"\bchrome[- ]?plated\b|\bchromed\b", "finish", "chrome-plated"),
    (r"\bnickel[- ]plated\b", "finish", "nickel-plated"), (r"\bpowder[- ]coated\b", "finish", "powder-coated"),
    (r"\bceramic[- ]coated\b|\bcoated (deck|decking) screws\b", "finish", "coated for outdoor use"),
    (r"\brust(y|ed)\b|\bcorroded\b", "finish", "rusty (corroded)"),
]]

# Sizes in a standard form in a file's TITLE only (descriptions often give a camera's "50 mm" lens).
SIZE = re.compile(r"(?<![\w.])(M(?:1\.6|2(?:\.5)?|3|4|5|6|8|10|12|14|16|18|20|22|24|27|30|33|36|42|48|56|64)"
                  r"(?:\s?[x×]\s?\d{1,3}(?:[.,]\d{1,2})?){0,2})(?![\w.])|(?<![\w#])(\d{1,2}d)\s?(?:common |box |"
                  r"finish(?:ing)? )?nails?\b|(?<![\w#])(#\d{1,2}(?:-\d{2})?)(?:\s?[x×]\s?\d+(?:[-/ ]\d+)*\")?(?=\W)|"
                  r"(?<![\w.])(\d{1,3}(?:[.,]\d)?\s?mm)\s?(?:long|length|screws?|bolts?|nails?)\b|"
                  r"(?<![\w./])(\d{1,2}(?:-\d/\d{1,2}|/\d{1,2})?\s?(?:inch|in\.|\")(?:\s?(?:long|length))?)"
                  r"(?=\s|$|,|\))", re.I)
PHOTO_WORDS = re.compile(r"\b(lens|camera|f/\d|iso|film|exposure|zoom)\b", re.I)
# A size is read only from a title that names a fastener ("Bolt M12", not "Mercedes M5 engine").
FASTENER_WORDS = re.compile(r"\b(screws?|bolts?|nuts?|nails?|washers?|rivets?|anchors?|rods?|studs?|pins?|threads?|"
                            r"fasteners?|plugs?|staples?|brads?)\b", re.I)


def title_size(title):
    """The size a file's own title states in a standard form ("Screw M6x20.jpg" -> "M6x20", "16d common nails" ->
    "16d", "#8 x 1-1/4\" wood screw" -> "#8"), or "" (also when the title is about a camera or lens)."""
    text = re.sub(r"^File:|\.\w{3,4}$", "", title or "")
    text = re.sub(r"[_]+", " ", text)
    if PHOTO_WORDS.search(text) or not FASTENER_WORDS.search(text):
        return ""
    m = SIZE.search(text)
    if not m:
        return ""
    return next(g for g in m.groups() if g).replace(" x ", "x").strip()


def file_features(texts, title):
    """{feature: value} read from a file's category names (texts) and its own title, leaving out a feature that is
    given two different values."""
    found = collections.defaultdict(set)
    for text in list(texts) + [re.sub(r"^File:|\.\w{3,4}$|_", " ", title or "")]:
        for pattern, feature, value in FEATURES:
            if pattern.search(text):
                found[feature].add(value)
    # "Socket head cap screw": a cap head with a hex socket, not a second head type.
    cap = "a socket cap head: a tall round head"
    if cap in found.get("head", set()) and len(found["head"]) > 1:
        found["head"].discard(cap)
    return {f: next(iter(v)) for f, v in found.items() if len(v) == 1}


def file_kind(kinds, found_in, categories, title):
    """The kind rule for a file: looking at the category it was found in, else its other categories, else its own
    title, the rule whose match is the longest (the most specific: "Impact wrenches" is an impact wrench, not just a
    wrench; "Window locks" a window lock, not just a lock; the first rule wins a tie); None when nothing matches."""
    for text in [found_in] + [c for c in categories if c != found_in] + [re.sub(r"^File:|\.\w{3,4}$|_", " ", title)]:
        best, length = None, 0
        for rule in kinds:
            m = rule[0].search(text)
            if m and len(m.group(0)) > length:
                best, length = rule, len(m.group(0))
        if best:
            return best
    return None


def feature_sentence(features, plural=False):
    """The features said in one or two plain sentences ("It has a countersunk (flat) head, and takes a Phillips
    (cross-shaped) screwdriver or bit. Material: stainless steel. Finish: zinc-plated."); "They have ..." for a
    plural name ("wood screws")."""
    it, has, takes = ("They", "have", "take") if plural else ("It", "has", "takes")
    parts = []
    if features.get("head") and features.get("drive"):
        parts.append(f"{it} {has} {features['head']}, and {takes} {features['drive']}.")
    elif features.get("head"):
        parts.append(f"{it} {has} {features['head']}.")
    elif features.get("drive"):
        parts.append(f"{it} {takes} {features['drive']}.")
    if features.get("thread"):
        parts.append(f"{it} {has} {features['thread']}.")
    if features.get("material"):
        parts.append(f"Material: {features['material']}.")
    if features.get("finish"):
        parts.append(f"Finish: {features['finish']}.")
    return " ".join(parts)


def part_rows(rule, features, size, text):
    """The question-and-answer rows of one picture: what it is (with its features, its size where its title states
    one, and a safety line where the kind has one), then one row per feature and the size, and the file's own
    description. A feature that does not fit the kind (a "head" said of a drill) is left out by the caller."""
    _, name, purpose, question, line = rule
    answer = answer_for(name, purpose)
    if not answer.endswith("."):
        answer += "."
    plural = answer.startswith("These are")
    it, has, takes, are = ("They", "have", "take", "are") if plural else ("It", "has", "takes", "is")
    said = feature_sentence(features, plural)
    if said:
        answer += " " + said
    if size:
        answer += f" The file's title gives the size: {size}."
    if line:
        answer += " " + line
    rows = [{"question": question, "answer": answer}]
    for feature, q in FEATURE_QUESTIONS.items():
        if features.get(feature):
            verb = takes if feature == "drive" else has
            rows.append({"question": q, "answer": f"{it} {verb} {features[feature]}."})
    if features.get("material") or features.get("finish"):
        bits = [f"{it} {are} made of {features['material']}" if features.get("material") else "",
                f"its finish is {features['finish']}" if features.get("finish") else ""]
        rows.append({"question": MATERIAL_Q, "answer": capital(", and ".join(b for b in bits if b)) + "."})
    if size:
        rows.append({"question": SIZE_Q, "answer": f"The file's title gives the size: {size}."})
    if text:
        rows.append({"question": DESCRIBE_Q, "answer": text})
    return rows


# Which features make sense for which packs: screws and bolts have heads, drives and threads; hinges, knobs and
# tools only materials and finishes (a "Phillips" in a tool's title is the screwdriver's tip, said by its kind).
SCREW_LIKE = re.compile(r"\b(screws?|bolts?|nails?|rivets?|nuts?|washers?|anchors?|pins?|studs?|rods?|plugs?|"
                        r"fasteners?|staples?)\b", re.I)


def keep_features(features, rule, pack_features):
    """The features a picture's answer may say: those the pack allows, and the head, drive and thread only for a
    screw-like part (by its kind's name)."""
    out = {f: v for f, v in features.items() if f in pack_features}
    if not SCREW_LIKE.search(rule[1]):
        for f in ("head", "drive", "thread"):
            out.pop(f, None)
    if "nut" in rule[1] or "washer" in rule[1]:
        out.pop("head", None)
        out.pop("drive", None)
    return out


# ----------------------------------------------------------------- shared: the Commons walk

# Subcategories that are not photos of the thing, or are about something else: drawings and art, firms and shops,
# places and events, history, and things that share a word (climbing bolts, ice screws, medical screws, wheel nuts,
# railway fastenings, clothing fasteners, jewellery, firearms).
SKIP = re.compile(r"\b(drawings?|diagrams?|illustrations?|icons?|logos?|in art|in heraldry|coats? of arms|animations?|"
                  r"videos?|patents?|pronunciation|toys?|lego|models?|miniatures?|museums?|exhibitions?|"
                  r"manufacturers?|compan(y|ies)|brands?|shops?|stores?|people|persons|by country|by year|by decade|"
                  r"history|historical|climbing|ice screws?|medical|surgical|implants?|orthopa?edic|dental|rail(way)?s? "
                  r"(bolts|fastenings)|wheel (bolts|nuts)|lug nuts|loose wheel nut|clothing|textile|brooch\w*|"
                  r"buckles?|zippers?|netsuke|jewel\w*|firearms?|bolt action|rifles?|guns?|swords?|weapons?|"
                  r"screw-shaped food|food|pushpins?|paper fasteners|tie clips|stamps?|banknotes?|coins?|"
                  r"quality images|featured pictures|valued images|nailsmiths|lamentation|crucifixion|"
                  r"in fiction|in literature|in film|sculptures?|monuments?|memorials?)\b", re.I)
# Words that show a museum or archaeological object, not today's hardware (a Commons "Shelf supports" category holds
# an Egyptian bench end): such files are left out of the Commons packs (nmah_hardware_tools has historic hardware).
ANCIENT = re.compile(r"\b(MET|Metropolitan Museum|museum|musée|museo|ancient|archaeolog\w*|dynasty|pharaoh|"
                     r"palace of|treasury|reliquar\w*|\d+ BCE?|century BC|byzantine|medieval)\b", re.I)
# Old photos (a year before 1950 in the title or caption, or a war) often show something else under the category's
# name (a 1916 army saw mill filed under "Table saws"): left out of the Commons packs too.
HISTORIC = re.compile(r"\b(1[0-8]\d\d|19[0-4]\d)s?\b|\b(world war|western front|civil war|wartime)\b", re.I)
# Words that leave a file out of these everyday packs (injuries and accidents).
HARM = re.compile(r"\b(injur\w*|wound\w*|blood\w*|accidents?|amputat\w*|killed|dead|deaths?|fatal\w*|x-ray|"
                  r"radiograph\w*|surgery|surgical|implant\w*|stab\w*|torture\w*|crucifi\w*)\b", re.I)


def topic(root, depth=1):
    """One Commons topic: a root category and how many levels of its subcategories to walk."""
    return (root, depth)


def walk(s, root, depth):
    """The root and its subcategories down to depth levels, leaving out those SKIP names and those of EXISTING
    (asked about by another pack), each once. A category that does not exist gives only itself (with no files)."""
    found, level = [root], [root]
    for _ in range(depth):
        nxt = []
        for c in level:
            if listing_out_of_time():
                return found
            for sub in commons_members(s, c, "subcat"):
                name = sub.split(":", 1)[-1]
                if name not in found and not SKIP.search(name):
                    found.append(name)
                    nxt.append(name)
        level = nxt
    return found


def topic_files(s, root, depth, seen):
    """[(file title, the category it was found in)] for a topic, shuffled the same way each time (a different way on
    a top-up pass); drawings and art left out by their names, and the files directly in a category another pack asks
    about (EXISTING) left out."""
    found = {}
    for category in walk(s, root, depth):
        if listing_out_of_time():
            break
        if category in EXISTING:
            continue
        for title in commons_members(s, category, "file"):
            if title not in seen and not NOT_A_PHOTO.search(title):
                found.setdefault(title, category)
    files = list(found.items())
    pass_random(len(root) * 7919 + sum(map(ord, root))).shuffle(files)
    return files


def hardware_commons(topics, kinds, limit, prefix, key, pack_features=("head", "drive", "thread", "material",
                                                                         "finish", "size")):
    """A Commons pack from topics, naming each file by the kinds rules: the topics take turns, in a fixed shuffled
    order, so each gets an even share. Each file's licence is checked (mechanical_packs.mech_entries: CC0, public
    domain or CC BY); files whose words name nudity or injuries are left out; a free file whose categories match no
    kind is set aside for a description when it has none of its own. Returns the pack entries."""
    s, items, seen = session(), [], set()
    order = list(topics)
    pass_random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[t, None] for t in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            (root, depth), files = q
            try:
                if files is None:
                    files = topic_files(s, root, depth, seen)
                    say(f"Commons {root}: {len(files)} files")
                batch, q[1] = files[:share * 2], files[share * 2:]
                if not batch:
                    queues.remove(q)
                    continue
                found_in = dict(batch)
                entries = mech_entries(s, [title for title, _ in batch])
                cats = file_categories(s, [e[0] for e in entries])
            except RuntimeError as e:          # Commons kept refusing: keep what was found and stop asking
                say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                queues = []
                break
            got = 0
            for title, url, credit, text, raw in entries:
                if got >= share or title in seen:
                    continue
                its = cats.get(title, [])
                words = NOT_A_CHILD.sub(" ", f"{title} {text} {' '.join(its)}")
                if NUDE.search(words):
                    considered(title, url, "its words are about nudity")
                    continue
                if HARM.search(words):
                    considered(title, url, "its words name an injury, surgery or an accident (an everyday pack)")
                    continue
                if ANCIENT.search(words) or HISTORIC.search(f"{title} {text}"):
                    considered(title, url, "a museum, archaeological or old photo, not today's hardware")
                    continue
                seen.add(title)
                text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
                text = text if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text) else ""
                category = found_in.get(title, root)
                rule = file_kind(kinds, category, its, title)
                if rule is None:
                    if not text:
                        needs_description(file_name(prefix, title), url, credit, credit.rsplit(", ", 2)[-2],
                                          text="", title=title, place=PLACES.get(title, ""),
                                          reason="no kind this pack can name from its categories, and no English "
                                                 "caption", page_url=credit.rsplit(", ", 1)[-1],
                                          extra={"commons_category": category, "child": bool(CHILD.search(words))})
                    considered(title, url, "no kind this pack can name from its categories")
                    continue
                features = keep_features(file_features([category] + its, title), rule, pack_features)
                size = title_size(title) if "size" in pack_features and SCREW_LIKE.search(rule[1]) else ""
                place = where(PLACES.get(title, ""))
                facts = {"commons_category": category, "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0],
                         **({"features": features} if features else {}), **({"size": size} if size else {})}
                rows = [mark_child(dict(r, credit=credit, facts=facts, **place), words)
                        for r in part_rows(rule, features, size, text)]
                items.append((file_name(prefix, title), url, rows))
                got += 1
            if not q[1]:
                queues.remove(q)
    pass_random(prefix + "-order").shuffle(items)
    fetched = commons_fetch(items[:want])[:limit]
    say(f"{key}: {len(fetched)} pictures")
    return with_twins(fetched)


# ----------------------------------------------------------------- what other packs already ask about

def _existing():
    """The Commons categories whose own files other packs already ask about (home_packs commons_tools and
    commons_connectors, things_packs commons_things, mechanical_packs commons_machine_parts and commons_car_parts):
    this module walks through them to their subcategories but does not take their files again."""
    import home_packs
    import things_packs
    import mechanical_packs
    names = {spec[0] for spec in home_packs.COMMONS_TOOLS + home_packs.COMMONS_CONNECTORS}
    names |= {spec[0] for spec in getattr(things_packs, "COMMONS_THINGS", [])}
    names |= {spec[0] for spec in mechanical_packs.COMMONS_MACHINE_PARTS + mechanical_packs.COMMONS_CAR_PARTS}
    return frozenset(names)


EXISTING = _existing()


# ----------------------------------------------------------------- commons_fasteners

FASTENER_TOPICS = [
    topic("Screws by type", 1), topic("Screws by head", 1), topic("Screws by type of drive", 1),
    topic("Security screws", 1), topic("Wood screws", 1), topic("Spax screws", 0), topic("Lag bolts", 1),
    topic("Screw heads", 0), topic("Metal nails", 2), topic("Wooden nails", 0), topic("Bolts", 1),
    topic("Carriage bolts", 0), topic("Eye bolts", 1), topic("Anchor bolts", 1), topic("Structural bolts", 1),
    topic("U-bolts", 0), topic("Nuts (hardware)", 1), topic("Locking nuts", 1), topic("Washers (hardware)", 1),
    topic("Lock washers", 1), topic("Wall plugs", 1), topic("Toggle bolts", 0), topic("Molly bolts", 0),
    topic("Screw anchor bolts", 0), topic("Rivets", 1), topic("Blind rivets", 0), topic("Staples (fasteners)", 1),
    topic("Threaded rods", 0), topic("Threaded fasteners", 1), topic("Cotter pins", 1), topic("Split pins", 1),
    topic("Lynch pins", 0), topic("Taper pins", 0), topic("Hose clamps", 1), topic("Cable ties", 1),
    topic("Fastener identification markings", 0), topic("Thread gauges", 1), topic("Thread pitch gauges", 0),
    topic("Screw thread pitch", 0), topic("External threads", 1), topic("Quality images of fasteners", 0),
    topic("Fasteners on white background", 0), topic("Timber framing fasteners", 1), topic("Spacers (fasteners)", 0),
]
FASTENER_KINDS = [
    # gauges and threads (asked first: a gauge photo also sits in screw categories)
    kind(r"\bthread pitch gauges?\b|\bscrew pitch gauges?\b|\bpitch gauges?\b", "a thread pitch gauge",
         "a set of toothed metal blades; the blade whose teeth fit a screw's thread exactly gives its pitch.", TOOL_Q),
    kind(r"\bthread gauges?\b|\bring gauges?\b|\bplug gauges?\b", "a thread gauge",
         "it checks that a screw thread is the right size and pitch (a ring gauge for bolts, a plug gauge for "
         "threaded holes).", TOOL_Q),
    kind(r"\bbolt gauges?\b|\bscrew gauges?\b|\bthread checkers?\b", "a bolt and screw gauge",
         "a plate with threaded holes and studs that tells a bolt's diameter and thread.", TOOL_Q),
    kind(r"\bscrew thread pitch\b|\bthread forms?\b|\bexternal threads\b", "a screw thread",
         "the spiral ridge on a screw or bolt; its pitch is the distance from one ridge to the next."),
    kind(r"\bfastener identification markings\b", "a bolt head with grade markings",
         "the marks on the head tell its strength grade and who made it."),
    # screws by kind
    kind(r"\bconfirmat\b", "a confirmat screw", "a thick screw with a wide thread that joins chipboard panels in "
                                                "flat-pack furniture."),
    kind(r"\b(double[- ]thread )?deck(ing)? screws?\b", "deck screws", "outdoor screws for fixing deck boards."),
    kind(r"\bdrywall screws?\b|\bplasterboard screws?\b", "drywall screws", "screws with a bugle head for fixing "
                                                                             "plasterboard to studs."),
    kind(r"\bself[- ]drilling\b|\btek screws?\b", "self-drilling screws", "screws with a drill-bit point that drill "
                                                                          "their own hole in metal."),
    kind(r"\bsheet[- ]metal screws?\b|\bself[- ]tapping\b|\bthread[- ]forming\b", "self-tapping screws",
         "screws that cut or form their own thread in metal or plastic."),
    kind(r"\bnailscrews?\b", "nail screws", "nails with a screw thread on the shank."),
    kind(r"\bgrub screws?\b|\bset screws?\b", "a set screw (grub screw)", "a headless screw that holds a part "
                                                                         "tight on a shaft."),
    kind(r"\bsocket head cap screws?\b", "a socket head cap screw", "a machine screw with a tall round head and a "
                                                                    "hex socket."),
    kind(r"\bbutton head screws?\b", "a button head screw", "a machine screw with a low rounded head and a hex "
                                                            "socket."),
    kind(r"\bthumb ?screws?\b", "a thumb screw", "a screw with a flat or knurled head, turned by hand."),
    kind(r"\bhanger bolts?\b", "a hanger bolt", "wood thread at one end and machine thread at the other."),
    kind(r"\blag (bolts?|screws?)\b|\bcoach screws?\b", "a lag screw (lag bolt)", "a heavy wood screw with a hex "
                                                                                  "head, turned with a spanner."),
    kind(r"\bsecurity screws?\b|\btamper[- ]resistant\b|\bone[- ]way screws?\b", "a security screw",
         "a screw with an unusual drive so that it cannot be undone with ordinary screwdrivers."),
    kind(r"\btreehouse screws?\b|\btreehouse attachment", "a treehouse attachment bolt", "a very large bolt that "
                                                                                       "holds a beam to a tree."),
    kind(r"\bspax\b|\bwood screws?\b|\bchipboard screws?\b", "wood screws", "screws with a sharp point and a coarse "
                                                                           "thread, for wood."),
    kind(r"\bmachine screws?\b|\bcomputer screws?\b", "machine screws", "screws with a fine, even thread that go "
                                                                        "into a nut or a threaded hole."),
    kind(r"\bscrews and wall plugs\b", "a screw and wall plug", "the plug goes into a drilled hole so the screw "
                                                                "holds in brick, block or plasterboard."),
    # anchors
    kind(r"\btoggle bolts?\b|\btoggles? \(fasteners\)|\bspring toggles?\b", "a toggle bolt",
         "a hollow-wall anchor with spring wings that open behind the wall."),
    kind(r"\bmolly bolts?\b|\bhollow[- ]wall anchors?\b", "a molly bolt (hollow-wall anchor)",
         "a metal sleeve that spreads behind plasterboard as its screw is tightened."),
    kind(r"\bwedge anchors?\b|\bsleeve anchors?\b|\bexpansion (anchors?|bolts?)\b|\bconcrete anchors?\b|"
         r"\bscrew anchor bolts\b|\banchor channel\b", "a concrete anchor",
         "it is set in a hole drilled in concrete or masonry and expands to grip it."),
    kind(r"\bwall plugs?\b|\bplastic anchors?\b|\bdrywall anchors?\b|\braw ?plugs?\b", "wall plugs (plastic anchors)",
         "plastic sleeves pushed into a drilled hole so a screw holds in brick, block or plasterboard."),
    # bolts
    kind(r"\bcarriage bolts?\b|\bcoach bolts?\b", "a carriage bolt", "a bolt with a smooth domed head and a square "
                                                                     "neck that stops it turning in wood."),
    kind(r"\beye ?bolts?\b", "an eye bolt", "a bolt with a loop at the top for a rope, chain or hook."),
    kind(r"\bu[- ]bolts?\b", "a U-bolt", "a bolt bent into a U and threaded at both ends, to clamp round a pipe or "
                                         "post."),
    kind(r"\bj[- ]bolts?\b", "a J-bolt", "a bolt bent into a J, set into concrete or hooked over a frame."),
    kind(r"\banchor bolts?\b|\bfoundation bolts?\b", "an anchor bolt", "a bolt set into concrete to hold a "
                                                                       "structure down."),
    kind(r"\bt[- ]bolts?\b|\bhammer[- ]head bolts?\b", "a T-bolt", "a bolt with a T-shaped head that slides into a "
                                                                    "slot."),
    kind(r"\bstructural bolts?\b|\bhv bolts?\b|\bdin 6914\b", "a structural bolt", "a heavy hex bolt for steel "
                                                                                   "construction."),
    kind(r"\bshoulder bolts?\b", "a shoulder bolt", "a bolt with a smooth, wider section under the head that a part "
                                                    "turns on."),
    kind(r"\bbolts without a thread\b|\bclevis pins?\b", "a clevis pin", "a pin with a head at one end and a hole "
                                                                        "for a cotter pin at the other."),
    kind(r"\bhex external\b|\bexternal hex\b", "a hex head screw or bolt", "a six-sided head turned with a "
                                                                            "spanner or socket."),
    kind(r"\bhex(agon)? head bolts?\b|\bhex bolts?\b", "a hex bolt", "a bolt with a six-sided head, turned with a "
                                                                     "spanner or socket."),
    # nuts
    kind(r"\bwing nuts?\b|\bbutterfly nuts?\b", "a wing nut", "a nut with two wings, tightened by hand."),
    kind(r"\bacorn nuts?\b|\bcap nuts?\b|\bdome nuts?\b", "an acorn (cap) nut", "a nut with a rounded top that "
                                                                               "covers the end of the bolt."),
    kind(r"\bcastellated nuts?\b|\bcastle nuts?\b|\bslotted nuts?\b", "a castle nut", "a nut with slots for a cotter "
                                                                                      "pin, so it cannot turn."),
    kind(r"\btee nuts?\b|\bt[- ]nuts?\b", "a T-nut", "a nut with prongs that is hammered into wood, giving a threaded "
                                                     "hole."),
    kind(r"\bnyloc\b|\bnylon[- ]insert\b|\blocking nuts?\b|\block ?nuts?\b|\bprevailing torque\b", "a lock nut",
         "a nut made to resist working loose, often with a nylon ring inside."),
    kind(r"\bflange(d)? nuts?\b", "a flange nut", "a nut with a wide built-in washer."),
    kind(r"\bsquare nuts?\b", "a square nut", "a four-sided nut."),
    kind(r"\bcoupling nuts?\b|\bsleeve nuts?\b|\bconnecting nuts?\b", "a coupling nut", "a long nut that joins two "
                                                                                        "threaded rods."),
    kind(r"\brivet nuts?\b|\brivnuts?\b", "a rivet nut", "a threaded insert set into sheet metal from one side."),
    kind(r"\bweld nuts?\b", "a weld nut", "a nut made to be welded onto a metal part."),
    kind(r"\bcage nuts?\b", "a cage nut", "a nut held in a springy cage that clips into a square hole, as in "
                                          "equipment racks."),
    kind(r"\bbarrel nuts?\b|\bsex bolts?\b|\bchicago (screws?|bolts?)\b", "a barrel nut (sex bolt)",
         "a tube with an inside thread and a head, that a screw goes into from the other side."),
    kind(r"\beye nuts?\b", "an eye nut", "a nut with a loop for lifting."),
    kind(r"\bturnbuckles?\b", "a turnbuckle", "a frame with a threaded eye or hook at each end: turning it tightens a "
                                              "wire or rope."),
    kind(r"\bhex(agon)? nuts?\b|\bnuts \(hardware\)", "a nut", "a threaded block that screws onto a bolt."),
    # washers
    kind(r"\bbelleville\b|\bdisc springs?\b|\bcone washers?\b", "a Belleville washer", "a slightly cone-shaped "
                                                                                      "spring washer."),
    kind(r"\btab washers?\b", "a tab washer", "a washer with tabs bent up against the nut so it cannot turn."),
    kind(r"\block washers?\b|\bsplit washers?\b|\bspring washers?\b|\btooth(ed)? (lock )?washers?\b",
         "a lock washer", "a split or toothed washer that stops a nut or screw working loose."),
    kind(r"\bfender washers?\b|\bpenny washers?\b|\brepair washers?\b", "a fender washer", "a flat washer with a "
                                                                                          "wide rim and a small hole, "
                                                                                          "to spread the load."),
    kind(r"\bplain washers?\b|\bflat washers?\b", "a flat washer", "a flat ring that spreads the load under a nut or "
                                                                   "screw head."),
    kind(r"\bwashers? with screws\b|\bwashers \(hardware\)", "a washer", "a ring that goes under a nut or screw "
                                                                         "head."),
    # nails
    kind(r"\broofing nails?\b|\bclout nails?\b", "roofing nails", "short nails with a wide flat head, for shingles and "
                                                                  "roofing felt."),
    kind(r"\bfinish(ing)? nails?\b|\blost head nails?\b|\bpanel pins?\b", "finishing nails",
         "thin nails with a small head that can be sunk below the surface."),
    kind(r"\bbrads?\b|\bbrad nails?\b", "brads", "very thin, short nails for trim and small work."),
    kind(r"\bring[- ]shank\b|\bannular\b|\bring nails?\b", "ring-shank nails", "nails with rings on the shank that "
                                                                               "grip the wood."),
    kind(r"\bmasonry nails?\b|\bconcrete nails?\b|\bhardened nails?\b", "masonry nails", "hardened nails for "
                                                                                         "concrete and brick."),
    kind(r"\bcut nails?\b|\bsquare nails?\b|\bhand[- ]?made nails?\b|\bwrought nails?\b", "cut nails",
         "flat, tapered nails cut from iron sheet, as in old buildings and floors."),
    kind(r"\bhorseshoe nails?\b", "horseshoe nails", "flat-sided nails that hold a horseshoe on."),
    kind(r"\bduplex nails?\b|\bdouble[- ]headed nails?\b", "duplex nails", "nails with two heads, easy to pull out "
                                                                           "of temporary work."),
    kind(r"\bupholstery nails?\b|\bupholstery tacks?\b|\btacks?\b", "upholstery tacks", "short nails with a "
                                                                                       "decorative head."),
    kind(r"\bcollated nails?\b|\bnail strips?\b|\bcoil nails?\b", "collated nails", "nails joined in a strip or coil "
                                                                                    "for a nail gun."),
    kind(r"\bwooden nails?\b|\btree ?nails?\b|\btrenails?\b|\bwooden pegs?\b", "wooden pegs (trenails)",
         "wooden pins that hold timbers together."),
    kind(r"\bwire nails?\b|\bcommon nails?\b|\bmetal nails\b|\bnails\b", "nails", "metal pins with a head, driven "
                                                                                "with a hammer."),
    # the rest
    kind(r"\bblind rivets?\b|\bpop rivets?\b", "blind (pop) rivets", "rivets set from one side with a rivet tool."),
    kind(r"\brivets?\b", "rivets", "metal pins that join plates for good."),
    kind(r"\bstaples \(fasteners\)|\bfence staples?\b|\bstaples?\b", "staples", "U-shaped wire fasteners driven with "
                                                                               "a staple gun or a hammer."),
    kind(r"\bthreaded rods?\b|\ball[- ]?thread\b|\bstuds? \(fasteners\)|\bstud bolts?\b", "a threaded rod",
         "a rod threaded along its length, used with nuts."),
    kind(r"\bcotter pins?\b|\bsplit pins?\b", "a cotter pin (split pin)", "a bent pin pushed through a hole, its "
                                                                          "legs bent apart to hold it."),
    kind(r"\blynch pins?\b|\blinch pins?\b", "a linch pin", "a pin with a sprung ring that holds a wheel or a "
                                                            "trailer part on a shaft."),
    kind(r"\bhitch pins?\b|\br[- ]clips?\b|\bhairpin cotters?\b", "a hitch pin clip (R-clip)", "a springy wire clip "
                                                                                              "that holds a pin."),
    kind(r"\btaper pins?\b|\bdowel pins?\b", "a taper pin", "a slightly tapered pin that locates two parts exactly."),
    kind(r"\bhose clamps?\b|\bhose clips?\b|\bjubilee clips?\b", "a hose clamp", "a band tightened by a screw to hold "
                                                                                "a hose on a pipe."),
    kind(r"\bcable ties?\b|\bzip ties?\b|\btie[- ]wraps?\b", "cable ties (zip ties)", "plastic straps that lock when "
                                                                                     "pulled tight."),
    kind(r"\bspacers? \(fasteners\)|\bstandoffs?\b", "a spacer (standoff)", "it holds two parts a set distance "
                                                                            "apart."),
    kind(r"\btimber framing fasteners?\b|\btimber connectors?\b", "a timber connector",
         "a metal plate or fastener that joins timbers."),
    kind(r"\bscrews? by\b|\bscrew heads?\b|\bscrews\b", "screws", "fasteners with a spiral thread, turned in with a "
                                                                 "screwdriver."),
    kind(r"\bbolts?\b", "a bolt", "a threaded fastener with a head, used with a nut."),
    kind(r"\bfasteners?\b", "fasteners", "parts that hold things together."),
]


def build_commons_fasteners(limit):
    """Nails, screws, bolts, nuts, washers, anchors, rivets, staples, pins, clamps and ties, and thread gauges."""
    return hardware_commons(FASTENER_TOPICS, FASTENER_KINDS, limit, "fastener", "commons_fasteners")


# ----------------------------------------------------------------- commons_door_hardware

DOOR_TOPICS = [
    topic("Door furniture", 2), topic("Door handles", 1), topic("Doorknobs", 1), topic("Keys", 1),
    topic("Hinges", 2), topic("Locks (security devices)", 2), topic("Padlocks", 1), topic("Door bolts", 1),
    topic("Latches", 1), topic("Hasps", 0), topic("Door closers", 1), topic("Door viewers", 0),
    topic("Door knockers", 1), topic("Strike plates", 0), topic("Deadbolts", 0), topic("Weatherstripping", 1),
    topic("Keyholes", 1), topic("Furniture hardware", 1), topic("Cam fasteners", 0), topic("Dowels", 1),
    topic("Shelf supports", 1), topic("Window hardware", 1), topic("Window locks", 0), topic("Window handles", 1),
    topic("Window cranks", 0), topic("Insect screens", 1), topic("Sash fasteners", 0), topic("Builders hardware", 1),
    topic("Panic bars", 0), topic("Electronic locks", 1), topic("Combination locks", 1), topic("Mortise locks", 0),
    topic("Rim locks", 0), topic("Bicycle locks", 0),
]
DOOR_KINDS = [
    # hinges
    kind(r"\bpiano hinges?\b|\bcontinuous hinges?\b", "a piano (continuous) hinge", "a long hinge that runs the whole "
                                                                                   "length of a lid or door."),
    kind(r"\bconcealed hinges?\b|\beuropean hinges?\b|\bcup hinges?\b|\bcabinet hinges?\b", "a concealed (European) "
         "cabinet hinge", "a hinge hidden inside the cabinet door, set in a round cup drilled in the door."),
    kind(r"\bstrap hinges?\b|\bt[- ]hinges?\b|\bgate hinges?\b", "a strap hinge", "a hinge with a long leaf, for "
                                                                                 "gates, sheds and barn doors."),
    kind(r"\bspring hinges?\b|\bself[- ]closing hinges?\b", "a spring hinge", "a hinge with a spring that closes the "
                                                                             "door by itself."),
    kind(r"\bpivot hinges?\b", "a pivot hinge", "the door turns on pins at its top and bottom."),
    kind(r"\bbutt hinges?\b|\bdoor hinges?\b|\bmortise hinges?\b", "a butt hinge", "two rectangular leaves joined by "
                                                                                   "a pin, set into the edge of a "
                                                                                   "door and its frame."),
    kind(r"\bflag hinges?\b|\blift[- ]off hinges?\b", "a lift-off hinge", "a hinge whose door can be lifted off its "
                                                                         "pin."),
    kind(r"\bhinges?\b", "a hinge", "a joint that lets a door, lid or gate swing."),
    # locks and keys
    kind(r"\bpadlocks?\b", "a padlock", "a lock with a shackle that loops through a hasp or chain."),
    kind(r"\bcombination locks?\b", "a combination lock", "a lock opened by turning dials or a knob to a number "
                                                          "code."),
    kind(r"\bdeadbolts?\b|\bdead bolts?\b", "a deadbolt", "a door lock with a solid bolt turned by a key or a thumb "
                                                          "turn, not pushed back by a spring."),
    kind(r"\belectronic locks?\b|\bkeypad locks?\b|\bsmart locks?\b|\bcard locks?\b", "an electronic lock",
         "a lock opened with a keypad code, a card, a phone or a fingerprint."),
    kind(r"\bmortise locks?\b", "a mortise lock", "a lock set into a pocket cut in the edge of the door."),
    kind(r"\brim locks?\b|\bnight latch\w*\b", "a rim lock", "a lock mounted on the inside face of the door."),
    kind(r"\bcylinder locks?\b|\block cylinders?\b|\bpin tumbler\b|\beuro(pean)? cylinders?\b", "a lock cylinder",
         "the part of a lock the key goes into."),
    kind(r"\bbicycle locks?\b|\bu[- ]locks?\b|\bcable locks?\b", "a bicycle lock", "a U-lock, chain or cable lock "
                                                                                  "for a bicycle."),
    kind(r"\bkeyholes?\b|\bescutcheons?\b|\bkeyhole covers?\b", "a keyhole escutcheon", "a plate round a keyhole."),
    kind(r"\bkeys? \(lock\)|\bkeys and keyways\b|\bkeys\b|\bskeleton keys?\b", "a key", "it opens a lock."),
    kind(r"\bstrike plates?\b|\bstrikes? \(lock\)", "a strike plate", "the metal plate on the door frame that the "
                                                                     "latch or bolt goes into."),
    kind(r"\bpanic (bars?|hardware|exit devices?)\b|\bpush bars?\b|\bcrash bars?\b", "a panic bar (exit device)",
         "a bar across an exit door: pushing it opens the door."),
    # door furniture
    kind(r"\bdoor ?knobs?\b", "a doorknob", "a round handle turned to open the latch."),
    kind(r"\blever handles?\b|\bdoor levers?\b", "a door lever handle", "a handle pushed down to open the latch; "
                                                                        "easier to use than a knob."),
    kind(r"\bdoor handles?\b|\bdoor pulls?\b|\bpull handles?\b", "a door handle", "it opens or pulls the door."),
    kind(r"\bdoor knockers?\b", "a door knocker", "a hinged ring or bar knocked against a plate to call at the "
                                                  "door."),
    kind(r"\bletter (plates?|boxes \(door\)|slots?)\b|\bmail slots?\b", "a letter plate (mail slot)",
         "a flap in a door for letters."),
    kind(r"\bdoor (viewers?|scopes?)\b|\bpeepholes?\b|\bspy holes?\b", "a door viewer (peephole)", "a small lens in "
                                                                                                  "a door to see who "
                                                                                                  "is outside."),
    kind(r"\bdoor closers?\b", "a door closer", "an arm with a spring and oil cylinder that closes the door slowly "
                                                "by itself."),
    kind(r"\bdoor stops?\b|\bdoorstops?\b|\bdoor wedges?\b", "a door stop", "it stops a door hitting the wall, or "
                                                                            "holds it open."),
    kind(r"\bdoor bolts?\b|\bbarrel bolts?\b|\bslide bolts?\b|\btower bolts?\b|\bflush bolts?\b", "a door bolt",
         "a bolt that slides across into a keeper to hold a door shut."),
    kind(r"\bhasps?\b|\bhasp and staple\b", "a hasp", "a hinged slotted strap that fits over a loop for a padlock."),
    kind(r"\bmagnetic catch\w*\b|\bcatch(es)?\b", "a catch", "it holds a cabinet door shut until pulled."),
    kind(r"\blatch(es)?\b|\bthumb latch\w*\b|\bgate latch\w*\b", "a latch", "a bar or bolt that holds a door or gate "
                                                                            "shut until lifted or turned."),
    kind(r"\bweatherstrip\w*\b|\bdraught (excluders?|strips?)\b|\bdraft (stoppers?|strips?)\b|\bdoor sweeps?\b",
         "weatherstripping", "strips round a door or window that keep out draughts and rain."),
    # cabinet and furniture
    kind(r"\bdrawer slides?\b|\bdrawer runners?\b", "a drawer slide", "a pair of metal runners, often on ball "
                                                                       "bearings, that a drawer slides on."),
    kind(r"\bdrawer pulls?\b|\bcabinet (pulls?|handles?)\b|\bfurniture handles?\b|\bbail pulls?\b", "a drawer pull",
         "a handle on a drawer or cabinet door."),
    kind(r"\bcabinet knobs?\b|\bdrawer knobs?\b|\bfurniture knobs?\b|\bknobs\b", "a knob", "a small round handle on "
                                                                                          "a drawer or cabinet."),
    kind(r"\bcam (fasteners?|locks?)\b|\bminifix\b", "a cam lock fitting", "a round cam and a pin that join flat-pack "
                                                                           "furniture panels."),
    kind(r"\bdowels?\b", "a dowel", "a round wooden pin glued into holes to join two pieces of wood."),
    kind(r"\bshelf (supports?|pins?|pegs?|clips?)\b", "shelf supports (shelf pins)", "small pegs in holes inside a "
                                                                                    "cabinet that hold a shelf."),
    kind(r"\bcabinet hardware\b|\bfurniture (hardware|fittings?)\b", "a furniture fitting", "a part used to "
                                                                                          "assemble or fit furniture."),
    # windows
    kind(r"\bwindow (locks?|latch\w*)\b|\bsash (locks?|fasteners?)\b", "a window lock", "it locks a window shut."),
    kind(r"\bwindow (cranks?|operators?|winders?)\b|\bcasement operators?\b", "a window crank (operator)",
         "a handle turned to open and close a casement window."),
    kind(r"\bwindow handles?\b|\bwindow (stays?|fittings?|hardware)\b", "a window handle", "it opens and locks a "
                                                                                         "window."),
    kind(r"\binsect screens?\b|\bwindow screens?\b|\bfly screens?\b|\bscreen doors?\b", "an insect screen",
         "a mesh over a window or door that keeps insects out."),
    kind(r"\bbuilders hardware\b|\bdoor furniture\b", "a piece of door hardware", "a fitting on a door."),
    kind(r"\blocks? \(security devices\)|\blocks\b", "a lock", "it keeps a door, lid or gate shut until it is "
                                                              "unlocked."),
]


def build_commons_door_hardware(limit):
    """Hinges, locks, keys, door furniture, cabinet and furniture hardware, and window hardware."""
    return hardware_commons(DOOR_TOPICS, DOOR_KINDS, limit, "door", "commons_door_hardware",
                            ("material", "finish"))


# ----------------------------------------------------------------- commons_building_hardware

BUILDING_TOPICS = [
    topic("Mounting brackets", 0), topic("Brackets (architecture)", 0), topic("Shelf brackets", 1),
    topic("Joist hangers", 0), topic("Structural connectors", 1), topic("Truss connector plates", 0),
    topic("Braces (fasteners)", 1), topic("Shelf standards", 0), topic("Picture hangers", 1), topic("Hangers", 1),
    topic("Hooks", 2), topic("Screw hooks", 1), topic("Coat hooks", 1), topic("Chains", 1), topic("Wire rope", 1),
    topic("Ropes", 1), topic("Knots", 1), topic("Shackles", 1), topic("Turnbuckles", 1), topic("Carabiners", 1),
    topic("Snap hooks", 0), topic("Pulleys", 1), topic("Blocks (sailing)", 0), topic("Springs (mechanical)", 1),
    topic("Gripples", 0), topic("Gate latches", 0), topic("Fence posts", 1), topic("Garage doors", 1),
    topic("Garage door openers", 1), topic("Mailboxes in the United States", 1), topic("Mailboxes", 1),
    topic("House numbers", 1), topic("House numbers in the United States", 1), topic("Tie down straps", 0),
    topic("Bungee cords", 0), topic("Suction cups", 0),
]
BUILDING_KINDS = [
    kind(r"\bjoist hangers?\b", "a joist hanger", "a folded metal bracket that holds the end of a joist against a "
                                                  "beam."),
    kind(r"\btruss (connector )?plates?\b|\bnail plates?\b|\bgang nail\w*\b", "a truss plate", "a steel plate with "
                                                                                              "teeth pressed into "
                                                                                              "the joints of a roof "
                                                                                              "truss."),
    kind(r"\bstructural connectors?\b|\bhurricane (ties?|straps?)\b|\bstrong[- ]tie\b|\bpost (bases?|caps?)\b",
         "a structural connector", "a metal bracket or strap that ties wooden framing together."),
    kind(r"\bcorner braces?\b|\bangle brackets?\b|\bl[- ]brackets?\b|\bbraces \(fasteners\)", "a corner brace "
         "(angle bracket)", "an L-shaped metal bracket that strengthens a corner."),
    kind(r"\bshelf brackets?\b", "a shelf bracket", "it holds a shelf up from the wall."),
    kind(r"\bshelf standards?\b|\bshelving tracks?\b", "a shelf standard", "a slotted metal strip on the wall that "
                                                                           "shelf brackets clip into."),
    kind(r"\bmounting brackets?\b|\bbrackets\b", "a bracket", "it holds or supports something on a wall or frame."),
    kind(r"\bpicture (hangers?|hooks?|rails?)\b", "a picture hanger", "a small hook or wire hanger for hanging a "
                                                                        "picture."),
    kind(r"\bscrew hooks?\b|\bcup hooks?\b|\bhook screws?\b", "a screw hook", "a hook with a screw thread, turned "
                                                                             "into wood."),
    kind(r"\bcoat hooks?\b|\brobe hooks?\b|\bclothes hooks?\b", "a coat hook", "a hook on a wall or door for "
                                                                               "clothes."),
    kind(r"\bsnap hooks?\b|\bcarabiners?\b|\bkarabiners?\b", "a carabiner (snap hook)", "a metal loop with a "
                                                                                       "spring gate."),
    kind(r"\bs[- ]hooks?\b", "an S-hook", "a hook bent into an S."),
    kind(r"\bhooks?\b", "a hook", "a curved piece for hanging something on."),
    kind(r"\bhangers\b", "a hanger", "it holds something hanging."),
    kind(r"\bshackles?\b", "a shackle", "a U-shaped metal link closed with a pin, for joining chain or rope."),
    kind(r"\bturnbuckles?\b|\brigging screws?\b", "a turnbuckle", "turning its body tightens the wire or rope fixed "
                                                                  "to its ends."),
    kind(r"\bwire ropes?\b|\bsteel cables?\b|\bwire rope clips?\b|\bthimbles?\b|\bgripples?\b", "wire rope",
         "rope made of twisted steel wires."),
    kind(r"\bknots?\b|\bbowlines?\b|\bhitches \(knot\)|\bsplices?\b", "a knot", "a way of tying rope."),
    kind(r"\bropes?\b|\bcordage\b|\btwine\b", "rope", "strands twisted or braided together."),
    kind(r"\bchains?\b|\bchain links?\b", "chain", "a row of metal links."),
    kind(r"\bpulleys?\b|\bblocks \(sailing\)|\bblock and tackle\b|\btackle\b", "a pulley", "a grooved wheel for a "
                                                                                          "rope; several together "
                                                                                          "make lifting easier."),
    kind(r"\bcasters?\b|\bcastors?\b", "a caster", "a small wheel on a swivel or fixed mount under furniture or a "
                                                   "cart."),
    kind(r"\bcompression springs?\b", "a compression spring", "a coil spring that pushes back when squeezed."),
    kind(r"\bextension springs?\b|\btension springs?\b", "an extension spring", "a coil spring that pulls back when "
                                                                                "stretched."),
    kind(r"\btorsion springs?\b", "a torsion spring", "a spring that twists, as on a garage door or a clothes peg."),
    kind(r"\bleaf springs?\b", "a leaf spring", "a stack of curved steel strips, as under a lorry or trailer."),
    kind(r"\bsprings? \(mechanical\)|\bcoil springs?\b|\bsprings\b", "a spring", "it stores energy and springs back "
                                                                                "to its shape."),
    kind(r"\bgarage door openers?\b", "a garage door opener", "a motor that opens and closes a garage door, often "
                                                              "with a remote control."),
    kind(r"\bgarage doors?\b", "a garage door", "a large door, often in sections that roll up on tracks."),
    kind(r"\bgate latch\w*\b|\bgate (hardware|hinges?)\b", "a gate latch", "it holds a gate shut."),
    kind(r"\bfence (hardware|brackets?|fittings?)\b|\bpost brackets?\b", "fence hardware", "fittings that hold fence "
                                                                                         "panels, rails and posts."),
    kind(r"\bfence posts?\b", "a fence post", "an upright post that holds up a fence."),
    kind(r"\bmailbox\w*\b|\bletter ?box\w*\b|\bpost ?box\w*\b", "a mailbox", "a box where post is delivered."),
    kind(r"\bhouse numbers?\b|\bstreet numbers?\b|\baddress (numbers|signs|plaques)\b", "a house number",
         "the number of the house, shown so visitors and deliveries can find it."),
    kind(r"\btie[- ]down straps?\b|\bratchet straps?\b|\bcargo straps?\b", "a ratchet strap", "a strap with a ratchet "
                                                                                          "buckle for tying down a "
                                                                                          "load."),
    kind(r"\bbungee cords?\b|\bshock cords?\b", "a bungee cord", "a stretchy cord with hooks at the ends."),
    kind(r"\bsuction cups?\b", "a suction cup", "a rubber cup that sticks to smooth surfaces."),
]


def build_commons_building_hardware(limit):
    """Brackets, connectors, shelf and wall hardware, hooks, chain, rope, pulleys, casters, springs, fence, gate and
    garage door hardware, mailboxes and house numbers."""
    return hardware_commons(BUILDING_TOPICS, BUILDING_KINDS, limit, "building", "commons_building_hardware",
                            ("material", "finish"))


# ----------------------------------------------------------------- commons_plumbing_electrical

PLUMBING_TOPICS = [
    topic("Plumbing", 1), topic("Valves", 1), topic("Electrical wiring", 2), topic("Electrical sockets", 1),
    topic("Electrical installations", 1), topic("Electrical connectors", 1), topic("Wires", 1),
    topic("Pipe fittings", 2), topic("Plumbing fittings", 1), topic("Push-fit fittings", 0), topic("PEX", 1),
    topic("PVC pipes", 1), topic("Pipe unions", 0), topic("Shut-off valves", 0), topic("Stop valves", 0),
    topic("Ball valves", 0), topic("Traps (plumbing)", 1), topic("P-traps", 0), topic("Mixer taps", 0),
    topic("Toilet parts", 1), topic("Toilet cisterns", 1), topic("Shower heads", 0), topic("Junction boxes", 1),
    topic("Light switches", 1), topic("Wall plates (electrical)", 0), topic("Twist-on wire connectors", 0),
    topic("Wire connectors", 1), topic("Terminal blocks", 0), topic("Circuit breakers", 1),
    topic("Distribution boards", 1), topic("Power cables", 1), topic("Coaxial cables", 0),
    topic("Extension cords", 1), topic("NEMA connectors", 1), topic("NEMA 14-50", 0), topic("NEMA 6-20", 0),
    topic("NEMA 5-20", 0), topic("NEMA L5-30", 0),
]
PLUMBING_KINDS = [
    kind(r"\bpush[- ]fit\b|\bsharkbite\b|\bpush[- ]to[- ]connect\b", "a push-fit pipe fitting", "the pipe is pushed "
                                                                                               "in and held by teeth "
                                                                                               "and an O-ring, with "
                                                                                               "no tools."),
    kind(r"\bcompression fittings?\b", "a compression fitting", "a nut squeezes a brass ring (an olive) onto the pipe "
                                                                "to seal it."),
    kind(r"\bpress fittings?\b|\bpress[- ]fit\b|\bpropress\b", "a press fitting", "a fitting squeezed onto the pipe "
                                                                                 "with a pressing tool."),
    kind(r"\bpex( pipes?| fittings?| tubing| crimp\w*)?\b", "PEX pipe or a PEX fitting", "PEX is bendable plastic water pipe, joined with crimp, clamp or "
                                                  "expansion fittings."),
    kind(r"\b(c?pvc|abs)( pipes?| fittings?| elbows?| tees?)?\b", "PVC pipe or a PVC fitting", "rigid plastic pipe joined with solvent "
                                                                          "cement."),
    kind(r"\bcopper (pipe )?fittings?\b|\bsweat fittings?\b|\bsolder fittings?\b", "a copper pipe fitting",
         "soldered onto copper water pipe."),
    kind(r"\bunions? \(pip|pipe unions?\b", "a pipe union", "a fitting with a nut that lets two pipes be taken "
                                                            "apart."),
    kind(r"\bcouplings? \(piping\)|\bpipe couplings?\b|\bsockets? \(pip", "a pipe coupling", "it joins two pipes in a "
                                                                                            "straight line."),
    kind(r"\belbows?\b|\bbends? \(pip", "an elbow pipe fitting", "it turns a pipe through an angle, usually 90 or 45 "
                                                                 "degrees."),
    kind(r"\btees?\b|\bt[- ]fittings?\b|\btee fittings?\b", "a tee pipe fitting", "it joins three pipes in a T."),
    kind(r"\breducers?\b|\breducing\b|\bbushings?\b", "a reducer fitting", "it joins a larger pipe to a smaller one."),
    kind(r"\bpipe caps?\b|\bend caps?\b|\bplugs? \(pip", "a pipe cap", "it closes the end of a pipe."),
    kind(r"\bshut[- ]?off valves?\b|\bstop valves?\b|\bstopcocks?\b|\bangle (stop )?valves?\b|\bisolation valves?\b",
         "a shut-off valve", "it turns off the water to one fixture or the whole house."),
    kind(r"\bball valves?\b", "a ball valve", "a quarter-turn valve: in line with the pipe it is open, across the pipe "
                                              "it is shut."),
    kind(r"\bp[- ]traps?\b|\btraps \(plumbing\)|\bs[- ]traps?\b|\bbottle traps?\b", "a P-trap", "the bend under a "
                                                                                              "sink that holds water "
                                                                                              "to keep sewer gas "
                                                                                              "out."),
    kind(r"\bfill valves?\b|\bballcocks?\b|\bfloat valves?\b", "a toilet fill valve", "it refills the toilet tank and "
                                                                                     "shuts off when the float "
                                                                                     "rises."),
    kind(r"\bflappers?\b|\bflush valves?\b", "a toilet flush valve", "it opens to let the tank's water into the bowl "
                                                                     "when you flush."),
    kind(r"\btoilet (parts|cisterns?|tanks?)\b|\bcisterns?\b", "the inside of a toilet tank", "the fill valve, flush "
                                                                                             "valve and float."),
    kind(r"\bmixer taps?\b|\bfaucets?\b|\btaps \(", "a faucet (tap)", "it lets water out; lever or knobs set the flow "
                                                                     "and temperature."),
    kind(r"\bshower heads?\b", "a shower head", "the spray head of a shower."),
    kind(r"\bpipe fittings?\b|\bplumbing fittings?\b|\bfittings?\b", "a pipe fitting", "a piece that joins pipes."),
    # electrical
    kind(r"\b(gfci|gfi|ground[- ]fault)( circuit interrupters?| outlets?| receptacles?)?\b", "a GFCI outlet", "an outlet with Test and Reset buttons that cuts "
                                                                   "the power if current leaks, used near water."),
    kind(r"\bnema 14-50( plugs?| outlets?| receptacles?| connectors?)?\b", "a NEMA 14-50 plug or outlet", "a large 240-volt, 50-amp outlet, for electric ranges, "
                                                          "car chargers and RVs: four slots."),
    kind(r"\bnema 6-(15|20|30|50)( plugs?| outlets?| receptacles?| connectors?)?\b", "a NEMA 6 plug or outlet", "a 240-volt outlet for large appliances and "
                                                                 "welders."),
    kind(r"\bnema 5-20( plugs?| outlets?| receptacles?| connectors?)?\b", "a NEMA 5-20 plug or outlet", "a 120-volt, 20-amp outlet: one slot has a T shape."),
    kind(r"\bnema l\d+-\d+( plugs?| outlets?| receptacles?| connectors?)?", "a NEMA twist-lock plug or outlet", "its curved blades are pushed in and turned to lock, as on "
                                                            "generators."),
    kind(r"\bnema( plugs?| outlets?| receptacles?| connectors?)?\b", "a NEMA plug or outlet", "a North American plug or outlet type."),
    kind(r"\boutlets?\b|\breceptacles?\b|\bsockets\b|\bpower sockets?\b", "an electrical outlet (receptacle)",
         "where a plug goes into the wall."),
    kind(r"\blight switch\w*\b|\bwall switch\w*\b|\bdimmers?\b|\btoggle switch\w*\b|\brocker switch\w*\b",
         "a light switch", "a switch on the wall that turns a light on and off."),
    kind(r"\bwall plates?\b|\bcover plates?\b|\bswitch plates?\b", "a wall plate (cover plate)", "the cover round a "
                                                                                                "switch or outlet."),
    kind(r"\btwist[- ]on wire connectors?\b|\bwire nuts?\b|\bmarrettes?\b", "a wire nut (twist-on connector)",
         "a plastic cap twisted onto the ends of wires to join them."),
    kind(r"\blever (wire )?connectors?\b|\bwago\b|\bwire connectors?\b|\bterminal blocks?\b", "a wire connector",
         "it joins electrical wires."),
    kind(r"\bjunction boxes?\b|\belectrical boxes?\b|\boutlet boxes?\b|\bswitch boxes?\b|\bpattress\w*\b",
         "an electrical box", "a box in the wall or ceiling that holds wire joints, a switch or an outlet."),
    kind(r"\bcircuit breakers?\b|\bminiature circuit breakers?\b|\brcbo\b|\brcd\b", "a circuit breaker",
         "a switch in the panel that turns off a circuit by itself when too much current flows."),
    kind(r"\bdistribution boards?\b|\belectrical panels?\b|\bbreaker (panels?|boxes?)\b|\bconsumer units?\b|"
         r"\bfuse ?boxes?\b", "an electrical panel (breaker box)", "it holds the breakers for the house's circuits."),
    kind(r"\bextension (cords?|leads?)\b|\bpower strips?\b", "an extension cord", "a cord with sockets at its end."),
    kind(r"\bcoaxial\b", "coaxial cable", "round cable for TV aerials, satellite and cable internet."),
    kind(r"\bnm[- ]b?( cables?)?\b|\bromex( cables?)?\b|\bnon[- ]metallic sheathed( cables?)?\b", "NM (Romex) cable", "house wiring cable: insulated "
                                                                                    "wires in a plastic sheath."),
    kind(r"\bthhn( wires?| cables?)?\b", "THHN wire", "single insulated wires pulled through conduit."),
    kind(r"\barmou?red cables?\b|\bbx cables?\b|\bmc cables?\b", "armoured cable", "wires inside a flexible metal "
                                                                                  "sheath."),
    kind(r"\bconduits?\b", "electrical conduit", "a tube that protects electrical wires."),
    kind(r"\bcables?\b|\bwires?\b|\bwiring\b", "electrical cable", "wires that carry electricity."),
]


def build_commons_plumbing_electrical(limit):
    """Pipe fittings, valves, traps, faucets and toilet parts; electrical boxes, outlets, switches, connectors,
    breakers, panels, cables and NEMA plug types."""
    return hardware_commons(PLUMBING_TOPICS, PLUMBING_KINDS, limit, "plumbelec", "commons_plumbing_electrical",
                            ("material", "finish"))


# ----------------------------------------------------------------- commons_building_materials

MATERIAL_TOPICS = [
    topic("Adhesive tapes", 1), topic("Engineered wood", 1), topic("Lumber", 1), topic("Timber (wood)", 1),
    topic("Plywood", 1), topic("Oriented strand board", 0), topic("Medium-density fibreboard", 0),
    topic("Particle board", 0), topic("Pressure-treated wood", 0), topic("Copper pipes", 0), topic("PVC pipes", 0),
    topic("Steel pipes", 1), topic("Duct tape", 0), topic("Masking tape", 0), topic("Painter's tape", 0),
    topic("PTFE tape", 0), topic("Thread seal tape", 0), topic("Sandpaper", 1), topic("Adhesives", 1),
    topic("Wood glue", 0), topic("Sealants", 1), topic("Wire spools", 0),
]
MATERIAL_KINDS = [
    kind(r"\boriented strand boards?\b|\bosb( boards?| panels?| sheathing)?\b", "OSB (oriented strand board)", "sheets made of wood flakes pressed with "
                                                                              "glue, for walls, floors and roofs."),
    kind(r"\bmedium[- ]density fib(re|er)boards?\b|\bmdf( boards?| panels?| sheets?)?\b", "MDF (medium-density fibreboard)", "smooth sheets of fine wood "
                                                                                       "fibres pressed with glue."),
    kind(r"\bparticle ?board\b|\bchipboard\b", "particle board (chipboard)", "sheets of wood chips pressed with "
                                                                              "glue."),
    kind(r"\bplywood\b", "plywood", "sheets made of thin layers of wood glued with the grain crossing."),
    kind(r"\bpressure[- ]treated\b|\btreated (wood|lumber|timber)\b", "pressure-treated lumber", "wood treated "
                                                                                                "against rot and "
                                                                                                "insects, for outdoor "
                                                                                                "use."),
    kind(r"\blumber\b|\btimber\b|\bdimensional\b|\bplanks?\b|\bboards?\b", "lumber (timber)", "sawn wood for "
                                                                                            "building."),
    kind(r"\bdrywall\b|\bplasterboard\b|\bgypsum board\b", "drywall (plasterboard)", "sheets of gypsum between paper "
                                                                                    "faces, for walls and "
                                                                                    "ceilings."),
    kind(r"\bcopper pipes?\b", "copper pipe", "water pipe joined by soldering or fittings."),
    kind(r"\bpvc pipes?\b", "PVC pipe", "rigid plastic pipe for drains and water."),
    kind(r"\bcast iron pipes?\b", "cast iron pipe", "heavy pipe for drains in older buildings."),
    kind(r"\bsteel pipes?\b|\bgalvani[sz]ed pipes?\b|\bblack (iron|steel) pipes?\b", "steel pipe", "threaded or "
                                                                                                "welded steel pipe."),
    kind(r"\bduct tape\b", "duct tape", "strong cloth-backed tape, usually silver-grey."),
    kind(r"\belectrical tape\b|\binsulating tape\b", "electrical tape", "stretchy vinyl tape that insulates wire "
                                                                        "joints."),
    kind(r"\bmasking tape\b|\bpainter'?s tape\b", "masking tape (painter's tape)", "paper tape that peels off cleanly, "
                                                                                  "used to mask edges when "
                                                                                  "painting."),
    kind(r"\bptfe tape\b|\bthread seal tape\b|\bteflon tape\b|\bplumber'?s tape\b", "PTFE thread tape (plumber's "
         "tape)", "thin white tape wrapped round pipe threads to seal them."),
    kind(r"\btapes?\b", "adhesive tape", "a sticky strip on a roll."),
    kind(r"\bsandpaper\b|\bsanding (sheets?|discs?)\b|\babrasive paper\b", "sandpaper", "paper coated with grit; the "
                                                                                       "lower the grit number, the "
                                                                                       "coarser it is."),
    kind(r"\babrasives?\b|\bemery\b|\bsteel wool\b", "an abrasive", "it wears a surface smooth."),
    kind(r"\bwood glue\b|\bpva\b", "wood glue", "white or yellow glue for wood joints."),
    kind(r"\bepoxy\b", "epoxy glue", "two parts mixed together that set very hard."),
    kind(r"\bcyanoacrylate\b|\bsuper ?glue\b", "super glue (cyanoacrylate)", "glue that sets in seconds."),
    kind(r"\bcaulk\w*\b|\bsealants?\b|\bsilicone sealant\b", "caulk (sealant)", "a paste squeezed into gaps to seal "
                                                                              "them."),
    kind(r"\bglues?\b|\badhesives?\b", "glue (adhesive)", "it sticks things together."),
    kind(r"\bwire spools?\b|\bcable (reels?|drums?)\b", "a spool of wire", "wire wound on a reel."),
    kind(r"\binsulation\b|\bglass wool\b|\bmineral wool\b|\bspray foam\b", "building insulation", "material that "
                                                                                                 "keeps heat in."),
    kind(r"\bengineered wood\b|\bglulam\b|\blaminated veneer\b", "engineered wood", "wood products made by gluing "
                                                                                   "wood layers, strands or fibres."),
]


def build_commons_building_materials(limit):
    """Lumber and sheet goods, drywall, pipe materials, tapes, sandpaper, glues, caulk and insulation."""
    return hardware_commons(MATERIAL_TOPICS, MATERIAL_KINDS, limit, "material", "commons_building_materials",
                            ("material", "finish"))


# ----------------------------------------------------------------- commons_hand_tools_trades

HAND_TOOL_TOPICS = [
    topic("Hand tools", 2), topic("Automotive tools", 1), topic("Hammers", 2), topic("Screwdriver bits", 1),
    topic("Screwdrivers", 1), topic("Wrenches", 2), topic("Spanners", 1), topic("Torx keys", 0),
    topic("Sockets (tool)", 1), topic("Ratchets (tool)", 1), topic("Pliers", 2), topic("Locking pliers", 0),
    topic("Slip-joint pliers", 0), topic("Saws", 1), topic("Hand saws", 1), topic("Coping saws", 0),
    topic("Rasps", 0), topic("Squares (tool)", 1), topic("Pry bars", 0), topic("Staple guns", 0),
    topic("Stud finders", 0), topic("Voltage testers", 1), topic("Calipers", 1), topic("Micrometers", 1),
    topic("Pipe cutters", 0), topic("Tube benders", 0), topic("Tubing cutters", 0), topic("Wire strippers", 0),
    topic("Crimping tools", 1), topic("Clamp meters", 0), topic("Manifold gauges", 0), topic("Vacuum pumps", 0),
    topic("Plumber's snakes", 0), topic("Pipe threading", 1), topic("OBD-II", 1), topic("Impact wrenches", 0),
    topic("Battery chargers", 0), topic("Tire levers", 0), topic("Tire irons", 0), topic("Oil drain pans", 0),
    topic("Concrete mixers", 1), topic("Masonry trowels", 0), topic("Plastering trowels", 0), topic("Tampers", 0),
    topic("Tile cutters", 0), topic("Tile saws", 0), topic("Paint sprayers", 0), topic("Paint rollers", 0),
    topic("Paintbrushes", 1), topic("Putty knives", 0), topic("Taping knives", 0), topic("Ladders", 2),
    topic("Stepladders", 0), topic("Scaffolding", 1), topic("Hand trucks", 1), topic("Pallet jacks", 0),
    topic("Chain hoists", 0), topic("Hoists", 1), topic("Tool belts", 0), topic("Toolboxes", 0),
    topic("Talking tape measures", 0), topic("Tactile tools", 0),
]
HAND_TOOL_KINDS = [
    # hammers
    tool(r"\bclaw hammers?\b", "a claw hammer", "for driving nails; the split claw pulls them out."),
    tool(r"\bball[- ]pe(e)?n hammers?\b", "a ball-peen hammer", "a metalworking hammer with one flat face and one "
                                                                 "rounded."),
    tool(r"\bsledge ?hammers?\b|\bclub hammers?\b|\blump hammers?\b", "a sledgehammer", "a heavy hammer for demolition "
                                                                                       "and driving stakes."),
    tool(r"\bmallets?\b|\bdead[- ]blow\b", "a mallet", "a hammer with a soft or wide head that does not mark the "
                                                       "work."),
    tool(r"\bframing hammers?\b", "a framing hammer", "a heavy claw hammer with a straight claw for building "
                                                      "frames."),
    tool(r"\btack hammers?\b|\bupholstery hammers?\b", "a tack hammer", "a light hammer for small tacks."),
    tool(r"\bmasonry hammers?\b|\bbrick hammers?\b|\bgeologic(al)? hammers?\b|\brock hammers?\b", "a brick hammer",
         "a hammer with a chisel end for cutting bricks and rock."),
    tool(r"\bhammers?\b", "a hammer", "for driving nails and striking."),
    # screwdrivers, keys, wrenches, sockets
    tool(r"\bscrewdriver bits?\b|\bdriver bits?\b|\bbit sets?\b", "screwdriver bits", "short tips that fit a drill or "
                                                                                    "a bit holder, one for each "
                                                                                    "drive type."),
    tool(r"\btorx keys?\b|\bstar keys?\b", "a Torx key", "an L-shaped key with a six-point star tip, for Torx "
                                                         "screws."),
    tool(r"\bhex keys?\b|\ballen keys?\b", "a hex key (Allen key)", "an L-shaped six-sided key for hex socket "
                                                                    "screws."),
    tool(r"\btorque wrench\w*\b", "a torque wrench", "it tightens a nut or bolt to an exact tightness."),
    tool(r"\bpipe wrench\w*\b|\bstillsons?\b", "a pipe wrench", "a heavy adjustable wrench with toothed jaws that grip "
                                                                "round pipe."),
    tool(r"\badjustable (wrench|spanner)\w*\b|\bcrescent wrench\w*\b", "an adjustable wrench", "a wrench whose jaw is "
                                                                                              "opened and closed by "
                                                                                              "a screw."),
    tool(r"\bcombination (wrench|spanner)\w*\b", "a combination wrench", "open at one end and a closed ring at the "
                                                                         "other, both the same size."),
    tool(r"\bbox[- ]end( wrench\w*| spanners?)?\b|\bring spanners?\b|\boffset ring( wrench\w*| spanners?)?\b", "a box-end (ring) wrench", "a closed ring that grips "
                                                                                          "all six sides of a nut."),
    tool(r"\bopen[- ]end(ed)?( wrench\w*| spanners?)?\b", "an open-end wrench", "U-shaped jaws that slip onto a "
                                                                                    "nut from the side."),
    tool(r"\bratchet(ing)? (wrench|spanner)\w*\b|\bratchets? \(tool\)|\bratchet handles?\b", "a ratchet",
         "a handle that turns a socket one way and clicks back freely the other."),
    tool(r"\bsockets? \(tool\)|\bsocket sets?\b|\bimpact sockets?\b", "sockets", "short tubes that fit over a nut, "
                                                                                "turned with a ratchet."),
    tool(r"\bwrench\w*\b|\bspanners?\b", "a wrench (spanner)", "for turning nuts and bolts."),
    tool(r"\bscrewdrivers?\b", "a screwdriver", "for turning screws; its tip matches the screw's drive."),
    # pliers and cutters
    tool(r"\blocking pliers?\b|\bvise[- ]grips?\b|\bmole grips?\b", "locking pliers", "pliers that lock shut on the "
                                                                                     "work."),
    tool(r"\bdiagonal (pliers?|cutters?)\b|\bside cutters?\b|\bwire cutters?\b|\bflush cutters?\b", "diagonal cutters",
         "cutting pliers for wire."),
    tool(r"\blineman'?s pliers?\b|\bcombination pliers?\b", "lineman's pliers", "heavy pliers that grip, twist and cut "
                                                                               "wire."),
    tool(r"\bslip[- ]joint pliers?\b|\btongue[- ]and[- ]groove\b|\bchannel ?locks?\b|\bwater pump pliers?\b",
         "slip-joint (tongue-and-groove) pliers", "pliers whose jaws open to several widths."),
    tool(r"\bneedle[- ]nose\b|\blong[- ]nose\b", "needle-nose pliers", "pliers with long thin jaws for small parts."),
    tool(r"\bwire strippers?\b", "wire strippers", "they cut and pull the insulation off a wire; the holes are marked "
                                                   "with wire sizes."),
    tool(r"\bcrimp(ing|ers?)\b", "a crimping tool", "it squeezes a connector onto the end of a wire."),
    tool(r"\bpliers?\b", "pliers", "for gripping, bending and cutting."),
    tool(r"\bbolt cutters?\b|\bsnips\b|\btin snips\b|\baviation snips\b", "snips", "shears for cutting sheet metal."),
    # saws, planes, files, chisels
    tool(r"\bcoping saws?\b|\bfret ?saws?\b", "a coping saw", "a thin blade in a U-shaped frame for curves."),
    tool(r"\bhacksaws?\b", "a hacksaw", "a fine-toothed blade in a frame, for metal and plastic pipe."),
    tool(r"\bjapanese saws?\b|\bpull saws?\b|\bryoba\b|\bdozuki\b", "a Japanese pull saw", "a thin saw that cuts as it "
                                                                                          "is pulled."),
    tool(r"\bback ?saws?\b|\btenon saws?\b|\bdovetail saws?\b", "a backsaw", "a saw with a stiff spine for fine "
                                                                            "joints."),
    tool(r"\bbow ?saws?\b|\bpruning saws?\b|\bfolding saws?\b", "a bow saw", "a saw for logs and branches."),
    tool(r"\bhand ?saws?\b|\bsaws\b", "a hand saw", "for cutting wood by hand."),
    tool(r"\bhand planes?\b|\bblock planes?\b|\bjack planes?\b|\bplanes \(tool", "a hand plane", "a blade set in a "
                                                                                                "body, pushed along "
                                                                                                "wood to shave it "
                                                                                                "flat."),
    tool(r"\brasps?\b", "a rasp", "a coarse file with separate teeth, for wood."),
    tool(r"\bfiles \(tools?\)|\bmetal files?\b|\bneedle files?\b", "a file", "a hardened steel bar with fine ridges, "
                                                                            "for shaping and smoothing."),
    # clamps, measuring, levels
    tool(r"\bc[- ]clamps?\b|\bg[- ]clamps?\b", "a C-clamp", "a C-shaped frame with a screw that clamps work."),
    tool(r"\bbar clamps?\b|\bpipe clamps?\b|\bf[- ]clamps?\b|\bquick[- ]grip\b|\bsash clamps?\b", "a bar clamp",
         "a long bar with a sliding jaw, for clamping glued work."),
    tool(r"\bspring clamps?\b", "a spring clamp", "a clamp squeezed open by hand, like a large clothes peg."),
    tool(r"\bclamps?\b", "a clamp", "it holds work tight."),
    tool(r"\bspeed squares?\b|\brafter squares?\b", "a speed square", "a triangle for marking angles on lumber."),
    tool(r"\bframing squares?\b|\bcarpenter'?s squares?\b|\bsteel squares?\b", "a framing square", "a large L-shaped "
                                                                                                "steel square."),
    tool(r"\bcombination squares?\b|\btry squares?\b|\bsquares \(tool", "a square", "for marking and checking right "
                                                                                    "angles."),
    tool(r"\blaser levels?\b", "a laser level", "it projects a level line of light onto a wall."),
    tool(r"\bspirit levels?\b|\bbubble levels?\b|\blevels \(instrument|\btorpedo levels?\b", "a spirit level",
         "a bubble in a vial shows when a surface is level."),
    tool(r"\bfolding rules?\b|\bzigzag rules?\b|\bclick rules?\b", "a folding rule", "a measuring rule that folds."),
    tool(r"\btalking tape\b|\btactile (tools?|rules?|levels?)\b|\bbraille (rulers?|tools?)\b",
         "an accessible measuring tool", "made to be read without sight: it speaks, clicks or has raised marks."),
    tool(r"\bdigital calipers?\b|\bvernier calipers?\b|\bdial calipers?\b|\bcalipers?\b", "a caliper",
         "it measures thickness, outside and inside sizes and depth exactly."),
    tool(r"\bmicrometers?\b", "a micrometer", "it measures thickness to a hundredth of a millimetre or a thousandth "
                                              "of an inch."),
    tool(r"\bstud finders?\b|\bstud sensors?\b", "a stud finder", "it finds the wooden or metal studs behind a wall."),
    tool(r"\bnon[- ]contact (voltage )?testers?\b|\bvoltage (testers?|detectors?)\b|\btest pens?\b",
         "a voltage tester", "it shows or beeps when a wire or outlet is live.",
         "Always check the tester on a circuit known to be live before trusting it."),
    tool(r"\bclamp (meters?|ammeters?)\b", "a clamp meter", "jaws close round one wire to measure its current."),
    tool(r"\bfish tapes?\b", "a fish tape", "a long flat steel tape on a reel, pushed through conduit to pull wires."),
    tool(r"\bconduit benders?\b", "a conduit bender", "a curved shoe on a handle that bends metal conduit."),
    tool(r"\bcable pullers?\b|\bwire pullers?\b", "a cable puller", "it pulls wires through conduit."),
    # plumbing and HVAC
    tool(r"\bpipe cutters?\b|\btub(e|ing) cutters?\b", "a tube cutter", "a wheel cuts round copper or plastic pipe as "
                                                                       "the tool turns."),
    tool(r"\btube benders?\b|\bpipe benders?\b", "a tube bender", "it bends copper tube without kinking it."),
    tool(r"\bpipe thread(ing|ers?)\b|\bthreading dies?\b|\bpipe dies?\b", "a pipe threader", "it cuts a thread on the "
                                                                                             "end of steel pipe."),
    tool(r"\bplumber'?s snakes?\b|\bdrain (augers?|snakes?|cleaners?)\b|\btoilet augers?\b", "a drain auger (snake)",
         "a long flexible coil turned down a drain to clear it."),
    tool(r"\bmanifold gauges?\b|\brefrigerant gauges?\b", "a refrigerant manifold gauge set", "gauges and hoses for "
                                                                                             "checking an air "
                                                                                             "conditioner's "
                                                                                             "pressures."),
    tool(r"\bvacuum pumps?\b", "a vacuum pump", "it pumps the air out of an air-conditioning system before it is "
                                                "filled."),
    tool(r"\bpress tools?\b|\bpressing tools?\b", "a pipe press tool", "it squeezes press fittings onto pipe."),
    # automotive
    tool(r"\bjack stands?\b|\baxle stands?\b", "a jack stand", "a stand that holds a lifted vehicle safely.",
         "Never work under a vehicle held only by a jack."),
    tool(r"\bfloor jacks?\b|\btrolley jacks?\b|\bbottle jacks?\b|\bscissor jacks?\b|\bcar jacks?\b|\bjacks \(",
         "a jack", "it lifts a vehicle.", "Never work under a vehicle held only by a jack."),
    tool(r"\bcreepers?\b", "a mechanic's creeper", "a low board on casters for lying under a vehicle."),
    tool(r"\bobd(-ii|2)?( scanners?| readers?| ports?| connectors?)?\b|\bscan tools?\b|\bcode readers?\b", "an OBD scanner (code reader)", "it plugs into the car's "
                                                                                           "diagnostic port and "
                                                                                           "reads fault codes."),
    tool(r"\bimpact (wrench|gun|driver)\w*\b", "an impact wrench", "a power wrench that hammers as it turns, for "
                                                                   "stuck nuts and wheel nuts."),
    tool(r"\bjump starters?\b|\bjumper (cables?|leads?)\b|\bbooster (cables?|packs?)\b", "a jump starter",
         "it starts a car with a flat battery."),
    tool(r"\bbattery chargers?\b", "a battery charger", "it recharges a vehicle battery."),
    tool(r"\btire (levers?|irons?|spoons?)\b|\btyre levers?\b|\blug wrench\w*\b|\bwheel braces?\b", "a tyre tool",
         "for taking wheels and tyres off."),
    tool(r"\boil (drain )?pans?\b|\bdrain pans?\b", "an oil drain pan", "it catches old oil when the oil is "
                                                                        "changed."),
    tool(r"\bengine (hoists?|cranes?)\b|\bshop cranes?\b", "an engine hoist", "a folding crane on wheels that lifts an "
                                                                              "engine out."),
    # masonry, concrete, tile, paint, drywall
    tool(r"\bconcrete mixers?\b|\bcement mixers?\b", "a concrete mixer", "a turning drum that mixes concrete."),
    tool(r"\bgrout floats?\b", "a grout float", "a rubber pad on a handle that presses grout between tiles."),
    tool(r"\bfloats \(tool|\bbull floats?\b|\bmagnesium floats?\b|\bhand floats?\b", "a float", "a flat tool that "
                                                                                               "smooths concrete or "
                                                                                               "plaster."),
    tool(r"\bmasonry trowels?\b|\bbrick trowels?\b|\bpointing trowels?\b|\bplastering trowels?\b|\bfinishing "
         r"trowels?\b|\bnotched trowels?\b", "a trowel", "a flat blade for spreading mortar, plaster or tile "
                                                         "adhesive."),
    tool(r"\btampers?\b|\bplate compactors?\b|\brammers?\b", "a tamper", "it packs down soil, gravel or sand."),
    tool(r"\btile (cutters?|saws?)\b|\bwet saws?\b", "a tile cutter", "it scores and snaps, or saws, tiles."),
    tool(r"\bpaint sprayers?\b|\bairless sprayers?\b|\bspray guns?\b", "a paint sprayer", "it sprays paint in a fine "
                                                                                         "mist."),
    tool(r"\bpaint rollers?\b", "a paint roller", "a roller on a handle for painting walls."),
    tool(r"\bpaint ?brush\w*\b", "a paintbrush", "for painting."),
    tool(r"\btaping knives?\b|\bputty knives?\b|\bjoint knives?\b|\bscrapers?\b", "a putty (taping) knife",
         "a flat blade for spreading filler or drywall compound."),
    tool(r"\bdrywall (lifts?|tools?)\b|\bpanel lifts?\b|\btexture (guns?|sprayers?)\b|\bcorner tools?\b",
         "a drywall tool", "a tool for hanging or finishing plasterboard."),
    # ladders, scaffolding, handling
    tool(r"\bstep ?ladders?\b", "a stepladder", "a folding ladder that stands on its own.", LADDER_LINE),
    tool(r"\bextension ladders?\b", "an extension ladder", "a ladder in two or more sliding sections, leaned against a "
                                                           "wall.", LADDER_LINE),
    tool(r"\bstep stools?\b|\bkick stools?\b", "a step stool", "a low stool with one or two steps.", LADDER_LINE),
    tool(r"\bladders?\b", "a ladder", "for climbing up to reach high places.", LADDER_LINE),
    tool(r"\bscaffold\w*\b", "scaffolding", "a temporary frame with platforms for working high up.",
         "Only work on scaffolding with guard rails, set up by trained people."),
    tool(r"\bhand trucks?\b|\bsack trucks?\b|\bappliance dollies?\b", "a hand truck", "an upright frame on two wheels "
                                                                                    "for moving heavy boxes."),
    tool(r"\bdollies \(equipment\)|\bmoving dollies?\b|\bfurniture dollies?\b|\bplatform trucks?\b", "a dolly",
         "a low platform on casters for moving heavy things."),
    tool(r"\bpallet (jacks?|trucks?)\b", "a pallet jack", "forks on wheels that lift and move a pallet."),
    tool(r"\bcome[- ]alongs?\b|\bcable pullers?\b|\bratchet pullers?\b", "a come-along", "a hand-worked ratchet winch "
                                                                                         "for pulling loads."),
    tool(r"\bchain (hoists?|blocks?)\b|\bhoists?\b", "a hoist", "it lifts heavy loads with a chain or rope.",
         "Never stand under a load being lifted."),
    tool(r"\btool ?belts?\b", "a tool belt", "a belt with pouches for tools and nails."),
    tool(r"\btool ?box\w*\b", "a toolbox", "a box for storing tools."),
    tool(r"\bstaple guns?\b|\bstaplers? \(tool", "a staple gun", "it drives staples into wood or board."),
    tool(r"\bpry bars?\b|\bcrow ?bars?\b|\bwrecking bars?\b", "a pry bar", "a steel bar for levering things apart."),
]


def build_commons_hand_tools_trades(limit):
    """Hand tools by type, automotive shop, HVAC, plumbing and electrical trade tools, masonry, tile, painting and
    drywall tools, ladders and scaffolding, and material handling."""
    return hardware_commons(HAND_TOOL_TOPICS, HAND_TOOL_KINDS, limit, "handtool", "commons_hand_tools_trades",
                            ("material",))


# ----------------------------------------------------------------- commons_power_tools

POWER_TOPICS = [
    topic("Power tools", 2), topic("Cordless drills", 1), topic("Impact drivers", 0), topic("Hammer drills", 0),
    topic("Rotary hammers", 0), topic("Circular saws", 1), topic("Miter saws", 1), topic("Table saws", 1),
    topic("Reciprocating saws", 0), topic("Sanders", 1), topic("Orbital sanders", 0),
    topic("Routers (woodworking)", 1), topic("Angle grinders", 1), topic("Die grinders", 0), topic("Nail guns", 1),
    topic("Oscillating multi-tools", 0), topic("Rotary tools", 1), topic("Dremel", 0), topic("Heat guns", 0),
    topic("Air compressors", 1), topic("Pneumatic tools", 1), topic("Pressure washers", 1),
    topic("Wet/dry vacuums", 0), topic("Shop vacuums", 0), topic("Saw blades", 1), topic("Circular saw blades", 0),
    topic("Drill bits", 2), topic("Router bits", 0), topic("Hole saws", 0), topic("Grinding wheels", 0),
    topic("Chainsaws", 1), topic("String trimmers", 1), topic("Leaf blowers", 1), topic("Tillers", 1),
    topic("Log splitters", 1), topic("Snow blowers", 1), topic("Portable generators", 1), topic("Wood chippers", 1),
    topic("Hedge trimmers", 1),
]
POWER_KINDS = [
    tool(r"\bimpact drivers?\b", "an impact driver", "a compact power driver that hammers as it turns, for long "
                                                     "screws."),
    tool(r"\brotary hammers?\b|\bsds(-| )?(plus|max)?( drills?| hammers?)?\b", "a rotary hammer", "a heavy drill that hammers, for concrete."),
    tool(r"\bhammer drills?\b", "a hammer drill", "a drill with a hammer action for brick and concrete."),
    tool(r"\bcordless drills?\b|\bdrill[- ]drivers?\b|\belectric drills?\b|\bpower drills?\b|\bdrills \(tool",
         "a power drill", "it drills holes and drives screws."),
    tool(r"\bmiter saws?\b|\bmitre saws?\b|\bchop saws?\b", "a mitre saw", "a circular saw on an arm that chops "
                                                                           "boards at exact angles."),
    tool(r"\btable saws?\b", "a table saw", "a circular blade sticking up through a table; the wood is pushed into "
                                            "it.", "Use the blade guard, riving knife and a push stick."),
    tool(r"\bband ?saws?\b", "a band saw", "a thin blade in a loop running over wheels, for curves and resawing."),
    tool(r"\bjig ?saws \(tool|\bjigsaws?\b|\bsabre saws?\b", "a jigsaw", "a hand-held saw with a short up-and-down "
                                                                         "blade, for curves."),
    tool(r"\breciprocating saws?\b|\bsawzall\b", "a reciprocating saw", "a long push-pull blade for demolition."),
    tool(r"\bcircular saws?\b|\bskilsaw\b", "a circular saw", "a hand-held saw with a round spinning blade."),
    tool(r"\bsaw blades?\b|\bcircular saw blades?\b|\bjigsaw blades?\b|\bhole saws?\b", "a saw blade",
         "the cutting part fitted to a saw; its teeth and size are marked on it."),
    tool(r"\brouter bits?\b", "a router bit", "a cutter that shapes edges and grooves in a router."),
    tool(r"\bdrill bits?\b|\btwist drills?\b|\bspade bits?\b|\bforstner\b|\bmasonry bits?\b|\bauger bits?\b",
         "a drill bit", "the cutting tip fitted in a drill; its size is marked on it."),
    tool(r"\bgrinding wheels?\b|\bcut[- ]off wheels?\b|\bflap discs?\b|\bsanding discs?\b", "a grinding or cutting "
         "disc", "it fits an angle grinder or bench grinder."),
    tool(r"\brandom orbit(al)? sanders?\b|\borbital sanders?\b|\bpalm sanders?\b|\bdetail sanders?\b",
         "an orbital sander", "it sands with a pad that moves in small circles."),
    tool(r"\bbelt sanders?\b", "a belt sander", "a loop of sandpaper running fast over rollers."),
    tool(r"\bsanders?\b", "a power sander", "it smooths wood and other surfaces."),
    tool(r"\brouters \(woodworking\)|\bplunge routers?\b|\btrim routers?\b|\bwood routers?\b", "a router",
         "a fast-spinning bit that shapes edges and cuts grooves."),
    tool(r"\bangle grinders?\b", "an angle grinder", "a spinning disc for cutting and grinding metal and stone.",
         "Wear eye protection and keep the guard on."),
    tool(r"\bdie grinders?\b", "a die grinder", "a small, very fast grinder."),
    tool(r"\bnail guns?\b|\bnailers?\b|\bbrad nailers?\b|\bframing nailers?\b", "a nail gun", "it drives nails with "
                                                                                             "air, gas or a "
                                                                                             "battery."),
    tool(r"\boscillating\b|\bmulti[- ]tools?\b", "an oscillating multi-tool", "a blade that moves quickly side to side, "
                                                                              "for plunge cuts and sanding."),
    tool(r"\brotary tools?\b|\bdremel\b", "a rotary tool", "a small, fast hand-held tool for grinding, cutting and "
                                                           "polishing."),
    tool(r"\bheat guns?\b|\bhot air guns?\b", "a heat gun", "it blows very hot air to strip paint or shrink tubing."),
    tool(r"\bair compressors?\b", "an air compressor", "it pumps air into a tank to power air tools and blow up "
                                                       "tyres."),
    tool(r"\bpneumatic (tools?|wrench\w*)\b|\bair (tools?|ratchets?|hammers?)\b", "an air tool", "a tool powered by "
                                                                                                "compressed air."),
    tool(r"\bpressure washers?\b|\bpower washers?\b|\bjet washers?\b", "a pressure washer", "it sprays water at high "
                                                                                           "pressure for cleaning."),
    tool(r"\bwet/dry\b|\bshop (vac\w*|vacuums?)\b|\bwet and dry vacuums?\b", "a wet/dry shop vacuum",
         "a strong vacuum cleaner for dust, debris and water."),
    tool(r"\bchainsaws?\b|\bchain saws?\b", "a chainsaw", "a chain with teeth running round a bar, for cutting trees "
                                                          "and logs.", "Wear chaps, eye and ear protection."),
    tool(r"\bstring trimmers?\b|\bweed (eaters?|whackers?)\b|\bstrimmers?\b|\bline trimmers?\b", "a string trimmer",
         "a spinning nylon line that cuts grass and weeds."),
    tool(r"\bleaf blowers?\b|\bblowers?\b", "a leaf blower", "it blows leaves and debris with a strong air stream."),
    tool(r"\bedgers?\b", "a lawn edger", "it cuts a clean edge along paths and beds."),
    tool(r"\btillers?\b|\brototillers?\b|\bcultivators?\b", "a tiller", "turning tines dig and break up soil."),
    tool(r"\blog splitters?\b|\bwood splitters?\b", "a log splitter", "a hydraulic ram pushes logs onto a wedge."),
    tool(r"\bsnow ?blowers?\b|\bsnow throwers?\b", "a snow blower", "it scoops snow and throws it aside."),
    tool(r"\bgenerators?\b", "a portable generator", "an engine that makes electricity.",
         "Run it only outdoors, far from windows and doors: its exhaust has deadly carbon monoxide."),
    tool(r"\bwood chippers?\b|\bchipper[- ]shredders?\b|\bshredders? \(garden", "a chipper-shredder",
         "it chops branches and garden waste into chips."),
    tool(r"\bhedge trimmers?\b", "a hedge trimmer", "two toothed blades that slide past each other to cut hedges."),
    tool(r"\bbatter(y|ies)\b", "a power tool battery", "a rechargeable battery pack that slides onto cordless tools."),
    tool(r"\bpower tools?\b", "a power tool", "a tool driven by a motor."),
]


def build_commons_power_tools(limit):
    """Drills, saws, sanders, routers, grinders, nail guns and other power tools, blades and bits, compressors,
    pressure washers and outdoor power equipment."""
    return hardware_commons(POWER_TOPICS, POWER_KINDS, limit, "powertool", "commons_power_tools", ("material",))


# ----------------------------------------------------------------- commons_shop_machines

SHOP_TOPICS = [
    topic("Machine tools", 2), topic("Metalworking tools", 1), topic("Woodworking tools", 1),
    topic("Welding equipment", 1), topic("Woodworking machines", 2), topic("Jointers", 0),
    topic("Thickness planers", 0), topic("Table saws", 1), topic("Drill presses", 1), topic("Wood lathes", 1),
    topic("Woodturning tools", 1), topic("Scroll saws", 0), topic("Spindle sanders", 0), topic("Disc sanders", 0),
    topic("Router tables", 0), topic("Dust collectors", 0), topic("Mortisers", 0), topic("Spindle moulders", 0),
    topic("CNC routers", 1), topic("Laser cutters", 1), topic("Workbenches", 1), topic("Vises", 1),
    topic("Woodworking jigs", 1), topic("Pocket-hole jigs", 0), topic("Push sticks", 0), topic("Metal lathes", 1),
    topic("Milling machines", 1), topic("Drill chucks", 0), topic("Boring bars", 0), topic("Surface grinders", 0),
    topic("Bench grinders", 0), topic("Cold saws", 0), topic("Sheet metal brakes", 0), topic("Metal shears", 0),
    topic("Slip rolls", 0), topic("Punch presses", 0), topic("Anvils", 1), topic("Forges", 1), topic("Welding", 1),
    topic("Welding machines", 1), topic("MIG welding", 0), topic("TIG welding", 0),
    topic("Shielded metal arc welding", 0), topic("Oxy-fuel welding and cutting", 1), topic("Plasma cutters", 0),
    topic("Welding helmets", 0), topic("Taps and dies", 1), topic("Taps (tool)", 0), topic("Dial indicators", 0),
    topic("Height gauges", 0), topic("Hydraulic presses", 0), topic("Deburring tools", 0),
    topic("Welding clamps", 0), topic("Welding magnets", 0),
]
SHOP_KINDS = [
    tool(r"\bjointers?\b|\bsurface planers?\b", "a jointer", "spinning knives under a long table flatten one face and "
                                                             "one edge of a board.", "Use push blocks and the guard."),
    tool(r"\bthickness(ing)? planers?\b|\bthicknessers?\b|\bplaners?\b", "a thickness planer", "it shaves a board to an "
                                                                                              "even thickness."),
    tool(r"\bdrill press\w*\b|\bpillar drills?\b|\bbench drills?\b", "a drill press", "a drill on a column that "
                                                                                     "drills straight down into work "
                                                                                     "on a table."),
    tool(r"\bwood ?lathes?\b|\bwood ?turning lathes?\b", "a wood lathe", "it spins wood so it can be shaped with "
                                                                         "turning tools."),
    tool(r"\bwoodturning tools?\b|\bturning (tools?|gouges?|chisels?)\b|\bskew chisels?\b|\bparting tools?\b",
         "a woodturning tool", "a long chisel or gouge held against wood spinning on a lathe."),
    tool(r"\bmetal lathes?\b|\bengine lathes?\b|\bmetalworking lathes?\b", "a metal lathe", "it spins metal work against "
                                                                                       "a cutting tool."),
    tool(r"\bcnc lathes?\b|\bmini lathes?\b|\blathes?\b", "a lathe", "it spins the "
                                                                                                         "work "
                                                                                                         "against a "
                                                                                                         "cutting "
                                                                                                         "tool."),
    tool(r"\bscroll saws?\b", "a scroll saw", "a fine blade moving up and down through a table, for tight curves."),
    tool(r"\bspindle sanders?\b", "a spindle sander", "a sanding drum that turns and moves up and down, for curves."),
    tool(r"\bdisc sanders?\b|\bbelt and disc\b", "a disc sander", "a spinning sanding disc beside a table."),
    tool(r"\brouter tables?\b", "a router table", "a router mounted upside down under a table."),
    tool(r"\bdust (collectors?|extractors?|extraction)\b|\bcyclone separators?\b", "a dust collector", "it sucks "
                                                                                                     "sawdust from "
                                                                                                     "machines."),
    tool(r"\bmortis(er|ing machines?)\b", "a mortiser", "a square chisel with a drill inside, for square holes."),
    tool(r"\bspindle moulders?\b|\bshapers? \(wood|\bwood shapers?\b", "a shaper (spindle moulder)", "a spinning "
                                                                                                    "cutter "
                                                                                                    "shapes "
                                                                                                    "edges of "
                                                                                                    "wood."),
    tool(r"\bcnc (routers?|machines?|mills?)\b|\bcnc\b", "a CNC router", "a computer-controlled cutting machine."),
    tool(r"\blaser (cutters?|engravers?|cutting)\b", "a laser cutter", "a laser beam cuts or engraves wood, acrylic "
                                                                       "or card."),
    tool(r"\bworkbenches?\b|\bwork benches?\b", "a workbench", "a sturdy table for working on."),
    tool(r"\bvi[cs]es?\b|\bvises \(|\bbench vi[cs]es?\b", "a vice", "jaws closed by a screw that hold work "
                                                                    "firmly."),
    tool(r"\bdovetail jigs?\b", "a dovetail jig", "a template that guides a router to cut dovetail joints."),
    tool(r"\bpocket[- ]hole\b|\bkreg\b", "a pocket-hole jig", "it guides a drill at an angle for pocket-screw "
                                                              "joints."),
    tool(r"\bpush sticks?\b|\bpush blocks?\b", "a push stick", "it pushes wood past a blade so fingers stay clear."),
    tool(r"\bfeatherboards?\b", "a featherboard", "a comb of flexible fingers that holds wood against a fence."),
    tool(r"\bjigs?\b", "a woodworking jig", "a guide that holds work or a tool for a repeated cut."),
    tool(r"\bend mills?\b|\bmilling cutters?\b", "an end mill", "a cutter for a milling machine."),
    tool(r"\bmilling machines?\b|\bbridgeport\b|\bmills? \(machine", "a milling machine", "a spinning cutter "
                                                                                         "shapes metal clamped to a "
                                                                                         "moving table."),
    tool(r"\bdrill chucks?\b|\bchucks?\b", "a chuck", "jaws that grip a drill bit or the work."),
    tool(r"\bcollets?\b", "a collet", "a split sleeve that grips a cutter or round work."),
    tool(r"\bboring bars?\b", "a boring bar", "a lathe tool for enlarging holes."),
    tool(r"\bsurface grinders?\b", "a surface grinder", "a grinding wheel that makes metal surfaces flat and smooth."),
    tool(r"\bbench grinders?\b|\bpedestal grinders?\b", "a bench grinder", "two grinding wheels on a motor, for "
                                                                           "sharpening and shaping.",
         "Wear eye protection and keep the tool rest close to the wheel."),
    tool(r"\bcold saws?\b|\babrasive (chop|cut[- ]off) saws?\b|\bmetal chop saws?\b", "a metal-cutting chop saw",
         "a saw for cutting metal bar and tube."),
    tool(r"\bhorizontal band ?saws?\b|\bmetal band ?saws?\b", "a horizontal band saw", "it cuts metal bar to length."),
    tool(r"\bsheet[- ]metal brakes?\b|\bpress brakes?\b|\bbending brakes?\b|\bbox and pan\b", "a sheet-metal brake",
         "it bends sheet metal along a straight line."),
    tool(r"\bmetal shears?\b|\bguillotine shears?\b|\bthroatless shears?\b", "metal shears", "a machine that cuts "
                                                                                             "sheet metal."),
    tool(r"\bslip rolls?\b|\bplate rolls?\b|\bbending rolls?\b", "slip rolls", "rollers that curve sheet metal."),
    tool(r"\bpunch press\w*\b|\bironworkers?\b|\bpunches \(tool|\bhole punch\w*\b", "a punch", "it punches holes in "
                                                                                              "metal."),
    tool(r"\banvils?\b", "an anvil", "a heavy iron block on which hot metal is hammered."),
    tool(r"\bforges?\b|\bsmithing hearths?\b", "a forge", "a hearth that heats metal until it can be shaped.",
         "Keep water and a fire extinguisher close."),
    tool(r"\bplasma cutt\w*\b", "a plasma cutter", "an electric arc and air jet cut through metal.",
         "Wear a shaded face shield or helmet; the arc can burn the eyes."),
    tool(r"\bwelding helmets?\b|\bwelding masks?\b|\bauto[- ]darkening\b", "a welding helmet", "a helmet with a dark "
                                                                                              "lens that protects the "
                                                                                              "eyes and face from the "
                                                                                              "arc.", PPE_LINE),
    tool(r"\boxy[- ](fuel|acetylene)( weld\w*| and cutting| cutting| torch\w*)*\b|\bcutting torch\w*\b|\bwelding torch\w*\b|\bgas welding\b", "an oxy-acetylene "
         "torch", "a torch burning oxygen and acetylene gas, for welding, brazing and cutting.",
         "Keep the gas cylinders upright and chained."),
    tool(r"\bmig( weld\w*)?\b|\bgas metal arc( weld\w*)?\b|\bflux[- ]core\w*( weld\w*)?\b", "a MIG welder", "it feeds a wire through a gun that welds "
                                                                            "with an electric arc.",
         "Wear a welding helmet, gloves and covered skin."),
    tool(r"\btig( weld\w*)?\b|\bgas tungsten arc( weld\w*)?\b", "a TIG welder", "a tungsten electrode makes the arc; filler rod is fed by "
                                                          "hand.", "Wear a welding helmet, gloves and covered skin."),
    tool(r"\bshielded metal arc( weld\w*)?\b|\bstick weld\w*\b|\barc weld\w*\b|\bsmaw\b", "a stick (arc) welder",
         "it welds with a coated electrode held in a clamp.", "Wear a welding helmet, gloves and covered skin."),
    tool(r"\bwelding (machines?|equipment|power sources?)\b|\bwelders?\b|\bwelding\b", "welding equipment",
         "equipment for joining metal by melting it.", "Wear a welding helmet, gloves and covered skin."),
    tool(r"\bwelding (clamps?|magnets?)\b|\bmagnetic squares?\b", "a welding clamp or magnet", "it holds metal parts in "
                                                                                              "place for welding."),
    tool(r"\btaps and dies\b|\btaps \(tool|\btap wrench\w*\b|\bthreading dies?\b|\bdie stocks?\b", "taps and dies",
         "taps cut a thread inside a hole; dies cut a thread on a rod."),
    tool(r"\bdial indicators?\b|\bdial gauges?\b|\bdial test indicators?\b", "a dial indicator", "a dial that shows "
                                                                                               "tiny movements of a "
                                                                                               "probe."),
    tool(r"\bheight gauges?\b", "a height gauge", "it measures and marks heights on a flat surface plate."),
    tool(r"\bdeburring tools?\b|\bdeburrers?\b", "a deburring tool", "a swivel blade that takes sharp edges off cut "
                                                                     "metal."),
    tool(r"\bhydraulic press\w*\b|\bshop press\w*\b|\barbor press\w*\b", "a hydraulic press", "a frame with a "
                                                                                             "hydraulic ram for "
                                                                                             "pressing bearings "
                                                                                             "and bending."),
    tool(r"\bmachine tools?\b", "a machine tool", "a machine for cutting and shaping metal."),
    tool(r"\bwoodworking machines?\b", "a woodworking machine", "a machine for cutting and shaping wood."),
]


def build_commons_shop_machines(limit):
    """Woodshop and metal shop machines, their tooling, welding and cutting equipment, and machinists' measuring
    tools."""
    return hardware_commons(SHOP_TOPICS, SHOP_KINDS, limit, "shop", "commons_shop_machines", ("material",))


# ----------------------------------------------------------------- commons_ppe

PPE_TOPICS = [
    topic("Personal protective equipment", 2), topic("Work gloves", 1), topic("Hard hats", 1),
    topic("Safety equipment", 1), topic("Respirators", 1), topic("N95 respirators", 0), topic("Dust masks", 0),
    topic("Full-face respirators", 0), topic("Powered air-purifying respirators", 0), topic("Gas masks", 0),
    topic("Safety glasses", 1), topic("Safety goggles", 0), topic("Goggles", 0), topic("Face shields", 0),
    topic("Nitrile gloves", 0), topic("Leather gloves", 0), topic("Welding gloves", 0),
    topic("High-visibility clothing", 1), topic("Safety footwear", 1), topic("Steel-toe boots", 0),
    topic("Safety harnesses", 1),
]
PPE_KINDS = [
    kind(r"\b(n95|ffp2|kn95)( respirators?| masks?)?\b", "an N95 respirator", "a fitted mask that filters at least 95 percent of "
                                                            "airborne particles; not for oil mists, gases or "
                                                            "vapours.", line=PPE_LINE),
    kind(r"\b(p100|ffp3)( filters?| respirators?| masks?)?\b", "a P100 respirator filter", "it filters at least 99.97 percent of particles, oil mists "
                                                           "included.", line=PPE_LINE),
    kind(r"\bpowered air[- ]purifying( respirators?)?\b|\bpaprs?\b", "a powered air-purifying respirator (PAPR)", "a battery blower "
                                                                                                "pushes filtered air "
                                                                                                "into a hood or "
                                                                                                "mask.",
         line=PPE_LINE),
    kind(r"\bfull[- ]face (respirators?|masks?)\b|\bgas masks?\b", "a full-face respirator", "it covers the eyes, nose "
                                                                                             "and mouth; its "
                                                                                             "cartridges are chosen "
                                                                                             "for particles or "
                                                                                             "gases.", line=PPE_LINE),
    kind(r"\bhalf[- ]face (respirators?|masks?)\b|\belastomeric\b|\bcartridge respirators?\b", "a half-face "
         "respirator", "a rubber mask over the nose and mouth with replaceable cartridges or filters.", line=PPE_LINE),
    kind(r"\bdust masks?\b|\bnuisance masks?\b", "a dust mask", "a light paper mask for nuisance dust; unless it is "
                                                                "marked N95 it is not a respirator.", line=PPE_LINE),
    kind(r"\brespirators?\b", "a respirator", "a mask that filters the air you breathe.", line=PPE_LINE),
    kind(r"\bearmuffs?\b|\bear defenders?\b", "hearing protection earmuffs", "padded cups over the ears that cut loud "
                                                                             "noise; the NRR number on the label "
                                                                             "tells how much.", line=PPE_LINE),
    kind(r"\bearplugs?\b|\bhearing protection\b", "earplugs", "foam or rubber plugs that cut loud noise.",
         line=PPE_LINE),
    kind(r"\bface shields?\b", "a face shield", "a clear visor that covers the face from flying bits and splashes; "
                                                "wear safety glasses under it.", line=PPE_LINE),
    kind(r"\bsafety goggles?\b|\bgoggles\b", "safety goggles", "goggles that seal round the eyes against dust and "
                                                               "splashes.", line=PPE_LINE),
    kind(r"\bsafety glasses\b|\bsafety spectacles\b|\bprotective eyewear\b", "safety glasses", "impact-resistant "
                                                                                              "glasses (look for "
                                                                                              "Z87 on the frame).",
         line=PPE_LINE),
    kind(r"\bhard hats?\b|\bsafety helmets?\b|\bhard ?hats\b", "a hard hat", "a helmet that protects the head from "
                                                                              "falling objects.", line=PPE_LINE),
    kind(r"\bnitrile gloves?\b|\bdisposable gloves?\b|\blatex gloves?\b", "disposable nitrile gloves", "thin gloves "
                                                                                                     "that protect "
                                                                                                     "against "
                                                                                                     "chemicals and "
                                                                                                     "dirt.",
         line=PPE_LINE),
    kind(r"\bcut[- ]resistant gloves?\b", "cut-resistant gloves", "gloves made to resist cuts from blades and sheet "
                                                                  "metal.", line=PPE_LINE),
    kind(r"\bwelding gloves?\b|\bgauntlets?\b", "welding gloves", "long leather gloves that resist heat and sparks.",
         line=PPE_LINE),
    kind(r"\bleather gloves?\b", "leather work gloves", "tough gloves for rough work.", line=PPE_LINE),
    kind(r"\bgloves?\b", "work gloves", "gloves that protect the hands.", line=PPE_LINE),
    kind(r"\bhigh[- ]visibility\b|\bhi[- ]vis\b|\bsafety vests?\b", "high-visibility clothing", "bright fluorescent "
                                                                                              "clothing with "
                                                                                              "reflective strips, so "
                                                                                              "the wearer is seen.",
         line=PPE_LINE),
    kind(r"\bsteel[- ]toe\w*\b|\bsafety (footwear|boots?|shoes?)\b|\bcomposite[- ]toe\b", "safety boots",
         "boots with protective toe caps.", line=PPE_LINE),
    kind(r"\blanyards?\b|\bself[- ]retracting\b|\blifelines?\b", "a fall protection lanyard", "the line that joins a "
                                                                                             "harness to an anchor "
                                                                                             "point.", line=PPE_LINE),
    kind(r"\bharness\w*\b|\bfall (protection|arrest)\b", "a fall protection harness", "a full-body harness worn when "
                                                                                      "working at height, clipped to "
                                                                                      "an anchor.", line=PPE_LINE),
    kind(r"\bpersonal protective equipment\b|\bppe\b", "personal protective equipment", "clothing and gear that "
                                                                                       "protects the wearer.",
         line=PPE_LINE),
]


def build_commons_ppe(limit):
    """Respirators by class, hearing protection, eye and face protection, hard hats, gloves by type, high-visibility
    clothing, safety boots and fall protection."""
    return hardware_commons(PPE_TOPICS, PPE_KINDS, limit, "ppe", "commons_ppe", ())


# ----------------------------------------------------------------- commons_sewing_food_equipment

SEWING_FOOD_TOPICS = [
    topic("Sewing equipment", 1), topic("Sewing machines", 2), topic("Overlock sewing machines", 0),
    topic("Sergers", 0), topic("Rotary cutters", 0), topic("Pinking shears", 0), topic("Sewing scissors", 0),
    topic("Sewing needles", 0), topic("Thimbles", 0), topic("Pincushions", 0), topic("Seam rippers", 0),
    topic("Bobbins", 0), topic("Meat slicers", 0), topic("Food slicers", 0), topic("Stand mixers", 1),
    topic("Planetary mixers", 0), topic("Sous-vide cookers", 0), topic("Sous-vide", 0), topic("Food processors", 0),
    topic("Meat grinders", 1), topic("Vacuum sealers", 0), topic("Commercial kitchens", 1), topic("Deep fryers", 0),
    topic("Combi steamers", 0), topic("Commercial dishwashers", 0),
]
SEWING_FOOD_KINDS = [
    tool(r"\boverlock\w*\b|\bsergers?\b", "a serger (overlock machine)", "it sews, trims and wraps the edge of fabric "
                                                                         "in one pass."),
    tool(r"\bsewing machines?\b", "a sewing machine", "it sews fabric with a needle and two threads."),
    tool(r"\brotary cutters?\b", "a rotary cutter", "a round blade on a handle for cutting fabric on a mat."),
    tool(r"\bpinking shears?\b", "pinking shears", "scissors with zigzag blades that stop fabric fraying."),
    tool(r"\bsewing scissors\b|\bdressmaking shears?\b|\btailor'?s shears?\b", "dressmaking shears", "long scissors "
                                                                                                   "for cutting "
                                                                                                   "fabric."),
    tool(r"\bseam rippers?\b", "a seam ripper", "a small forked blade that cuts stitches."),
    tool(r"\bthimbles?\b", "a thimble", "a cap on the fingertip for pushing a needle."),
    tool(r"\bpincushions?\b", "a pincushion", "a pad for holding pins and needles."),
    tool(r"\bbobbins?\b", "a bobbin", "a small spool for the lower thread of a sewing machine."),
    tool(r"\bsewing needles?\b|\bneedles\b", "sewing needles", "for sewing by hand or machine."),
    tool(r"\bmeat slicers?\b|\bfood slicers?\b|\bdeli slicers?\b", "a meat slicer", "a round spinning blade that "
                                                                                    "slices meat and cheese thinly.",
         "Its blade is very sharp: keep the guard in place."),
    tool(r"\bplanetary mixers?\b|\bcommercial mixers?\b|\bhobart mixers?\b", "a commercial mixer", "a large mixer for "
                                                                                                  "dough and "
                                                                                                  "batter."),
    tool(r"\bstand mixers?\b|\bkitchenaid\b", "a stand mixer", "a mixer with a bowl and a beater, whisk or dough hook."),
    tool(r"\bsous[- ]vide\b|\bimmersion circulators?\b", "a sous-vide cooker", "it heats a water bath to an exact "
                                                                               "temperature to cook food in sealed "
                                                                               "bags."),
    tool(r"\bfood processors?\b", "a food processor", "a bowl with spinning blades that chop, slice and mix."),
    tool(r"\bmeat grinders?\b|\bmincers?\b", "a meat grinder", "it pushes meat through a turning screw and cutting "
                                                               "plate."),
    tool(r"\bvacuum sealers?\b", "a vacuum sealer", "it sucks the air out of a bag and seals it."),
    tool(r"\bdeep fryers?\b|\bfryers?\b", "a deep fryer", "a tank of hot oil for frying.", "Hot oil burns: keep water "
                                                                                          "away from it."),
    tool(r"\bcombi steamers?\b|\bcombi ovens?\b|\bcommercial ovens?\b", "a combination oven", "a commercial oven that "
                                                                                             "bakes with steam and "
                                                                                             "hot air."),
    tool(r"\bdough sheeters?\b", "a dough sheeter", "rollers that roll dough thin."),
    tool(r"\bcommercial dishwashers?\b", "a commercial dishwasher", "a fast dishwasher for restaurants."),
    tool(r"\bcommercial kitchens?\b", "a commercial kitchen", "a restaurant or canteen kitchen."),
]


def build_commons_sewing_food_equipment(limit):
    """Sewing machines, sergers and sewing tools, and food-preparation equipment."""
    return hardware_commons(SEWING_FOOD_TOPICS, SEWING_FOOD_KINDS, limit, "sewfood", "commons_sewing_food_equipment",
                            ("material",))


# ----------------------------------------------------------------- abo_hardware (Amazon Berkeley Objects)

# The ABO product types of this pack (things_packs abo_products leaves them out: ABO_HARDWARE_TYPES there, which
# must hold the same keys; test_hardware.py checks it).
ABO_HW_TYPES = {
    "HARDWARE_HANDLE": "door and cabinet hardware", "HARDWARE": "hardware", "HARDWARE_HINGE": "hinges",
    "LOCK": "locks", "DOORSTOP": "door stops", "STORAGE_HOOK": "hooks", "HARDWARE_CLAMP_VISE": "clamps",
    "TOOLS": "tools", "WRENCH": "tools", "SCREWDRIVER": "tools", "PLIERS": "tools", "DRILL_BITS": "tools",
    "FASTENER_DRIVE_BIT": "tools", "MULTITOOL": "tools", "UTILITY_KNIFE": "tools", "PORTABLE_TOOL_BOX": "tools",
    "LADDER": "ladders", "FAUCET": "plumbing", "SHOWERHEAD": "plumbing", "VALVE": "plumbing",
    "TOILET_SEAT": "plumbing", "TOWEL_HOLDER": "bathroom hardware", "TOILET_PAPER_HOLDER": "bathroom hardware",
    "CARGO_STRAP": "straps", "EARMUFF": "protective equipment", "EARPLUG": "protective equipment",
    "SAFETY_GLASSES": "protective equipment",
}
# The kind named by the listing's own name (the first that matches), with a short line on what it is for.
ABO_KINDS = [(re.compile(p, re.I), n, u) for p, n, u in [
    (r"\bdeadbolt\b", "a deadbolt", "a door lock with a solid bolt turned by a key or thumb turn"),
    (r"\bkeypad\b.*\block\b|\belectronic\b.*\b(lock|deadbolt)\b|\bsmart lock\b", "an electronic lock",
     "a lock opened with a keypad code"),
    (r"\bpadlock\b", "a padlock", None), (r"\bcable lock\b", "a cable lock", None),
    (r"\bdoor (security|reinforcement) (bar|lock)\b|\bsecurity bar\b", "a door security bar",
     "it braces a door so it cannot be forced open"),
    (r"\bdoor closer\b", "a door closer", "an arm with a spring and oil cylinder that closes the door by itself"),
    (r"\bdoor lever\b|\blever (set|handle)\b|\bpassage lever\b|\bprivacy lever\b", "a door lever handle", None),
    (r"\bdoor ?knob\b|\bpassage knob\b|\bprivacy knob\b", "a doorknob", None),
    (r"\btoilet (tank )?lever\b|\btrip lever\b", "a toilet tank lever", "the handle that flushes the toilet"),
    (r"\bcabinet knob\b|\bdrawer knob\b", "a cabinet knob", None),
    (r"\b(cabinet|drawer|bar|cup|bin|euro bar) (handle|pull)s?\b", "a cabinet or drawer pull", None),
    (r"\bdrawer (slides?|tri-slides?)\b|\bslides?\b", "a drawer slide", "metal runners a drawer slides on"),
    (r"\boverlay\b.*\bhinges?\b|\binset\b.*\bhinges?\b|\bcabinet (door )?hinges?\b", "a cabinet hinge", None),
    (r"\bdoor hinges?\b|\bhinges?\b", "a door hinge", None),
    (r"\bhinge pin door stop\b", "a hinge-pin door stop", "it fits on a door hinge's pin and stops the door hitting "
                                                          "the wall"),
    (r"\bkick door stop\b", "a kick-down door stop", "it holds a door open; kick it down to set it"),
    (r"\bspring door stop\b", "a spring door stop", "a spring on the wall or skirting that stops the door"),
    (r"\bdoor ?stop\b", "a door stop", None),
    (r"\bshelf brackets?\b", "shelf brackets", None), (r"\bwall plate\b", "a wall plate (cover plate)", None),
    (r"\bcoat rack\b", "a wall-mounted coat rack", None), (r"\bhooks?\b", "a hook", None),
    (r"\bpole socket\b", "a closet pole socket", "it holds the end of a clothes rail"),
    (r"\bc-clamp\b|\bclamps?\b", "a clamp", None), (r"\bdead blow hammer\b", "a dead-blow hammer", None),
    (r"\bclaw hammer\b", "a claw hammer", None), (r"\bmallet\b", "a mallet", None), (r"\bhammer\b", "a hammer", None),
    (r"\bratchet\w*\b.*\bscrewdriver\b|\bscrewdriver\b", "a screwdriver set or screwdriver", None),
    (r"\bratchet(ing)? (strap|tie[- ]?down)s?\b|\btie[- ]?downs?\b", "ratchet straps", None),
    (r"\bbit set\b|\bbits?\b", "a set of bits", None),
    (r"\bsocket\b.*\bset\b|\bratchet (wrench|set|handle)\b", "a socket set", None),
    (r"\bwrench\b|\bspanner\b", "a wrench (spanner)", None), (r"\bpliers?\b", "pliers", None),
    (r"\bsnips?\b", "aviation snips", "shears for cutting thin metal"), (r"\butility knife\b", "a utility knife", None),
    (r"\bmulti-?tool\b", "a multi-tool", None), (r"\btool (box|bag|chest)\b", "a tool box", None),
    (r"\bstep stool\b", "a step stool", None), (r"\bladder\b", "a ladder", None),
    (r"\btape measure\b", "a tape measure", None), (r"\blevel\b", "a spirit level", None),
    (r"\bshower ?head\b", "a shower head", None), (r"\bfaucet\b|\btap\b", "a faucet", None),
    (r"\btoilet seat\b", "a toilet seat", None), (r"\btowel (bar|ring|rack|holder)\b", "a towel bar", None),
    (r"\btoilet (paper|tissue|roll) holder\b", "a toilet paper holder", None),
    (r"\bratchet strap\b|\btie[- ]down\b|\bstraps?\b", "a ratchet strap", None),
    (r"\bear ?muffs?\b|\bhearing protect\w*\b", "hearing protection earmuffs", None),
    (r"\bear ?plugs?\b", "earplugs", None), (r"\bsafety glasses\b|\bgoggles\b", "safety glasses", None),
    (r"\bknobs?\b", "a knob", None), (r"\bpulls?\b|\bhandles?\b", "a handle or pull", None),
]]
FINISHES = re.compile(r"\b(satin nickel|brushed nickel|polished nickel|polished chrome|satin chrome|chrome|"
                      r"oil[- ]rubbed bronze|venetian bronze|antique (?:brass|bronze|copper|pewter)|aged bronze|"
                      r"polished brass|satin brass|brass[- ]plated|antique nickel|matte black|flat black|matte white|"
                      r"stainless steel|brushed stainless|satin stainless|polished stainless|white|black|gold|"
                      r"champagne bronze|bronze|copper|pewter|brass)\b", re.I)
ABO_MATERIALS = re.compile(r"\b(zinc alloy|zinc|stainless steel|steel|brass|aluminium|aluminum|fibre ?glass|"
                           r"fiberglass|plastic|nylon|rubber|wood|bamboo|cast iron|iron|alloy steel|chrome vanadium|"
                           r"leather)\b", re.I)
# A number (whole, decimal, a fraction such as 1/4 or a mixed one such as 1-1/4) with a unit, an optional "x" second
# measure, and a word saying what it measures ("diameter", "length", "hole center" ...).
_NUMBER = r"(?:\d+[- ])?\d+/\d+|\d+(?:[.,]\d+)?"
_UNIT = r"(?:inch(?:es)?|in\.|\"|''|cm|mm|m\b|ft\b|feet|foot|lbs?\.?|oz\.?|kg|g\b)"
ABO_SIZE = re.compile(rf"((?<![\d/.])(?:{_NUMBER})\s?(?:-|–)?\s?{_UNIT}(?:\s?x\s?(?:{_NUMBER})\s?{_UNIT})?"
                      r"(?:\s(?:diameter|length|hole cent(?:er|re)|overlay|wide|long))?)", re.I)
NOT_PROTECTION = re.compile(r"\b(ear ?warmers?|winter|faux fur\w*|furry|fleece)\b", re.I)
ABO_PACK = re.compile(r"\b(\d+)[- ]?(?:pack|pk|count|piece|pcs)\b|\bpack of (\d+)\b|\bset of (\d+)\b", re.I)
ABO_HW_CREDIT = ("Amazon Berkeley Objects: data and images by Amazon.com; dataset by Matthieu Guillaumin, Thomas "
                 "Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC "
                 "Berkeley); CC BY 4.0, https://amazon-berkeley-objects.s3.amazonaws.com/index.html; item {item} "
                 "({domain})")


def abo_en(field, country=""):
    """The English value of a listing's language-tagged field (the listing's own country's English first)."""
    values = [v for v in field or [] if isinstance(v, dict) and str(v.get("language_tag", "")).startswith("en")]
    values.sort(key=lambda v: v.get("language_tag") != f"en_{country}")
    return clean(str(values[0].get("value", ""))) if values else ""


def abo_hw_features(listing, name):
    """(finish, material, sizes, pack) as the listing states them: the finish field or a finish named in the name,
    the material field or a material named in the name, the sizes written in the name, and the pack count."""
    country = listing.get("country") or ""
    finish = abo_en(listing.get("finish_type"), country)
    m = FINISHES.search(name)
    if m and (not finish or finish.lower() in m.group(1).lower()):
        finish = m.group(1)
    material = abo_en(listing.get("material"), country)
    if not material:
        mm = ABO_MATERIALS.search(name)
        material = mm.group(1) if mm and (not finish or mm.group(1).lower() not in finish.lower()) else ""
    sizes = [clean(s).replace("''", '"') for s in ABO_SIZE.findall(name)]
    sizes = [s for s in dict.fromkeys(sizes) if not re.match(r"^\d+(\.\d+)?\s?m$", s)]
    pm = ABO_PACK.search(name)
    pack = next((g for g in pm.groups() if g), "") if pm else ""
    return finish, material.replace(";", ", "), sizes, pack


def abo_hw_rows(listing):
    """The rows of one ABO hardware listing, or [] when it is not one of this pack's types or has no English name."""
    code = ((listing.get("product_type") or [{}])[0] or {}).get("value", "")
    if code not in ABO_HW_TYPES:
        return []
    country = listing.get("country") or ""
    name = abo_en(listing.get("item_name"), country)
    if not name or not listing.get("main_image_id"):
        return []
    if NOT_PROTECTION.search(name):
        return []                               # winter ear warmers filed as hearing protection
    brand = abo_en(listing.get("brand"), country)
    named = next(((n, u) for p, n, u in ABO_KINDS if p.search(name)), None)
    finish, material, sizes, pack = abo_hw_features(listing, name)
    by = f" by {brand}" if brand and brand.lower() not in ("generic",) else ""
    if named:
        what, use = named
        verb = "This is" if what.startswith(("a ", "an ")) else "These are"
        first = f"{verb} {what}{by}" + (f": {use}." if use else ".")
    else:
        first = f"This is {ABO_HW_TYPES[code]}{by}."
    answer = f"{first} Its listing calls it: {name.rstrip('.')}."
    if finish:
        answer += f" Finish: {finish.lower()}."
    if material and material.lower() != (finish or "").lower():
        answer += f" Material: {material.lower()}."
    if sizes:
        answer += f" Size (from its listing): {', '.join(sizes)}."
    if pack and int(pack) > 1:
        answer += f" A pack of {int(pack)}."
    rows = [{"question": WHAT_Q, "answer": answer}]
    if finish:
        rows.append({"question": FINISH_Q, "answer": f"Its listing gives the finish as {finish.lower()}."})
    if sizes:
        rows.append({"question": SIZE_Q, "answer": f"Its listing gives the size: {', '.join(sizes)}."})
    return rows


def build_abo_hardware(limit):
    """The ABO hardware pack: reads the 16 listing files and the image list, keeps this pack's product types with an
    English name and a main photo, takes the types in turn (so handles do not fill the pack), then fetches the
    catalogue photos."""
    from things_packs import ABO_LISTINGS, ABO_IMAGES, ABO_PICTURE
    s, rng = session(), pass_random(4441)
    by_type, seen_images = collections.defaultdict(list), set()
    for part in "0123456789abcdef":
        r = s.get(ABO_LISTINGS.format(part), timeout=600)
        r.raise_for_status()
        for line in gzip.decompress(r.content).decode("utf-8").splitlines():
            try:
                listing = json.loads(line)
            except ValueError:
                continue
            rows = abo_hw_rows(listing)
            image = listing.get("main_image_id")
            if not rows or image in seen_images:
                continue
            seen_images.add(image)
            by_type[listing["product_type"][0]["value"]].append((listing, rows))
    say(f"ABO hardware: {sum(len(v) for v in by_type.values())} usable listings in {len(by_type)} product types")
    paths = {}
    r = s.get(ABO_IMAGES, timeout=600)
    r.raise_for_status()
    for row in csv.DictReader(io.StringIO(gzip.decompress(r.content).decode("utf-8"))):
        if row["image_id"] in seen_images:
            paths[row["image_id"]] = row["path"]
    lists = []
    for code in sorted(by_type):
        rng.shuffle(by_type[code])
        lists.append(by_type[code])
    want, items = int(limit * 1.1) + 2, []
    while len(items) < want and any(lists):
        for queue in lists:
            if queue and len(items) < want:
                listing, rows = queue.pop()
                path = paths.get(listing["main_image_id"])
                if not path:
                    continue
                credit = ABO_HW_CREDIT.format(item=listing.get("item_id", ""), domain=listing.get("domain_name", ""))
                place = where(country_named("GB" if listing.get("country") == "UK" else listing.get("country", "")),
                              "market")
                items.append((f"abo-hw-{listing['main_image_id']}.jpg".replace("+", "_"), ABO_PICTURE.format(path),
                              [dict(r, credit=credit, **place) for r in rows]))
    fetched = fetch_all(items, workers=8)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- nmah_hardware_tools (Smithsonian, CC0)

# Object names (the record's "Object Name" or title) of hardware and tools, with the plain name the answer gives.
NMAH_NAMES = [(re.compile(p, re.I), n) for p, n in [
    (r"\bpadlocks?\b", "a padlock"), (r"\bdoor ?locks?\b|\block,? door\b|\brim locks?\b|\bmortise locks?\b",
                                      "a door lock"),
    (r"\bcombination locks?\b", "a combination lock"), (r"\blocks?\b(?! ?(stitch|step|nut))", "a lock"),
    (r"\bkeys?\b(?!board|stone| ?punch)", "a key"), (r"\bhinges?\b", "a hinge"), (r"\blatch(es)?\b", "a latch"),
    (r"\bhasps?\b", "a hasp"), (r"\bdoor ?knockers?\b|\bknocker\b", "a door knocker"),
    (r"\bdoor ?knobs?\b|\bknob,? door\b", "a doorknob"), (r"\bdoor ?handles?\b|\bdoor pulls?\b", "a door handle"),
    (r"\bescutcheons?\b", "an escutcheon"), (r"\bdoor ?bolts?\b", "a door bolt"),
    (r"\bscrewdrivers?\b", "a screwdriver"), (r"\bwrench(es)?\b|\bspanners?\b", "a wrench"),
    (r"\bpliers\b", "pliers"), (r"\bhammers?\b", "a hammer"), (r"\bplanes?,? (wood|block|smoothing|jack|plow|molding|"
                                                              r"rabbet|jointer)\b|\b(wood|block|smoothing|jack|plow|"
                                                              r"molding|rabbet|jointer) planes?\b", "a wood plane"),
    (r"\bchisels?\b", "a chisel"), (r"\bsaws?\b(?! ?mill)", "a saw"), (r"\bbrace,? (bit|carpenter)|\bbit brace\b",
                                                                        "a brace (hand drill)"),
    (r"\bhand drills?\b|\bdrill,? hand\b|\bbreast drills?\b", "a hand drill"), (r"\baugers?\b", "an auger"),
    (r"\bspokeshaves?\b", "a spokeshave"), (r"\bdrawknives?\b|\bdraw knives?\b", "a drawknife"),
    (r"\badzes?\b", "an adze"), (r"\baxes?\b|\bhatchets?\b", "an axe"), (r"\bfiles?,? (metal|wood|hand)\b|\brasps?\b",
                                                                        "a file"),
    (r"\bcalipers?\b|\bcallipers?\b", "a caliper"), (r"\bmicrometers?\b", "a micrometer"),
    (r"\bsquares?,? (try|carpenter|framing)\b|\b(try|carpenter'?s|framing) squares?\b", "a square"),
    (r"\blevels?,? (spirit|carpenter)\b|\bspirit levels?\b", "a spirit level"), (r"\bvises?\b|\bvices?\b", "a vice"),
    (r"\bclamps?\b", "a clamp"), (r"\banvils?\b", "an anvil"), (r"\btongs\b", "tongs"),
    (r"\bscrews?\b(?! ?(press|propeller|cutting))", "a screw"), (r"\bbolts?\b", "a bolt"), (r"\bnails?\b(?! ?polish|"
                                                                                           r" ?file)", "a nail"),
    (r"\brivets?\b", "a rivet"), (r"\bwashers?\b(?! ?machine)", "a washer"), (r"\bnuts?\b(?! ?(cracker|pick))",
                                                                              "a nut"),
]]
NMAH_NOT = re.compile(r"\b(photograph|print|poster|patent model|lithograph|drawing|negative|postcard|stamp|coin|"
                      r"medal|textile|quilt|costume|toy|game|keyboard|piano|telegraph key|typewriter|lock ?step|"
                      r"locket|hair|surgical|dental|medical|weapon|gun|rifle|pistol|sword|bayonet|knife,? (bowie|"
                      r"combat|trench))\b", re.I)
NMAH_WORDS = re.compile(r"lock|key|hinge|latch|hasp|knocker|knob|handle|escutcheon|bolt|screw|wrench|plier|hammer|"
                        r"plane|chisel|saw|brace|drill|auger|spokeshave|drawknife|draw knife|adze|axe|hatchet|file|"
                        r"rasp|caliper|calliper|micrometer|square|level|vise|vice|clamp|anvil|tong|nail|rivet|washer|"
                        r"nut", re.I)


def nmah_row(record):
    """(picture address, rows) for an NMAH record of a hardware part or hand tool with a CC0 picture, or None. The
    answer gives the object's own name, maker, date, place and materials as catalogued."""
    content = record.get("content") or {}
    title = clean(record.get("title") or "")
    free = content.get("freetext") or {}
    names = [clean(o.get("content")) for o in free.get("objectType") or [] if o.get("label") == "Object Name"]
    object_name = names[0] if names else title
    text = f"{object_name} {title}"
    if NMAH_NOT.search(text):
        return None
    plain = next((n for p, n in NMAH_NAMES if p.search(object_name) or p.search(title)), None)
    if not plain:
        return None
    media = ((content.get("descriptiveNonRepeating") or {}).get("online_media") or {}).get("media") or []
    picture = next((m for m in media if (m.get("usage") or {}).get("access") == "CC0" and m.get("type") == "Images"
                    and m.get("content")), None)
    if not picture:
        return None
    makers = [clean(n.get("content")) for n in free.get("name") or [] if "maker" in (n.get("label") or "").lower()
              or "manufacturer" in (n.get("label") or "").lower()]
    makers = [m for m in makers if not re.match(r"^(unknown|unidentified|anonymous)\b", m, re.I)]
    dates = [clean(d.get("content")) for d in free.get("date") or [] if "made" in (d.get("label") or "").lower()]
    places = [clean(p.get("content")) for p in free.get("place") or [] if "made" in (p.get("label") or "").lower()]
    materials = []
    for p in free.get("physicalDescription") or []:
        words = p.get("content") or ""
        if "material" not in words:
            continue
        words = re.sub(r"\s*\((?:overall|\?+|unknown) material\)", "", words)
        words = re.sub(r"\((?:part: )?([a-z ]+?) material\)", r"(\1)", words)
        materials.append(clean(words))
    verb = "This is" if plain.startswith(("a ", "an ")) else "These are"
    answer = f"{verb} {plain}"
    if title and title.lower() not in plain.lower():
        answer += f" (its record calls it \"{title}\")"
    if makers:
        answer += f", made by {makers[0]}"
    if places:
        answer += (" in " if makers else ", made in ") + places[0].replace("United States: ", "")
    if dates:
        answer += f", {dates[0]}"
    answer += "."
    materials = [m for m in materials if m]
    if materials:
        answer += f" Its record gives its materials: {', '.join(materials)}."
    credit = (f"National Museum of American History, Smithsonian Institution, CC0: {title} "
              f"({(content.get('descriptiveNonRepeating') or {}).get('record_ID', '')}), "
              f"{(content.get('descriptiveNonRepeating') or {}).get('guid', '')}")
    rows = [{"question": WHAT_Q, "answer": answer, "credit": credit}]
    if materials:
        rows.append({"question": "What is it made of?", "answer": f"Its record gives its materials: "
                                                                  f"{', '.join(materials)}.",
                     "credit": credit})
    return picture["content"] + "&max=2048", rows


def build_nmah_hardware_tools(limit):
    """The NMAH records of locks, keys, hinges, door hardware, fasteners and hand tools with a CC0 picture, read from
    the Smithsonian open-access bucket (its museum's metadata files, in a fixed shuffled order, a quick word check
    before each record is read), until enough are found or half the time limit is spent."""
    s, items = session(), []
    keys = si_keys("nmah")
    pass_random("nmah-hardware").shuffle(keys)
    for key in keys:
        if listing_out_of_time() or len(items) >= limit * 1.2:
            break
        try:
            text = s.get(f"{SI_BUCKET}/{key}", timeout=300).content.decode("utf-8", "replace")
        except Exception:  # noqa: BLE001 - next file
            continue
        for line in text.splitlines():
            if '"CC0"' not in line or not NMAH_WORDS.search(line[:4000]):
                continue
            try:
                got = nmah_row(json.loads(line))
            except ValueError:
                continue
            if got:
                url, rows = got
                items.append((f"nmah-hw-{len(items):05d}.jpg", url, rows))
        say(f"  NMAH {key.rsplit('/', 1)[-1]}: {len(items)} records so far")
    pass_random("nmah-hardware-order").shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=6, pause=0.1)[:limit])


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below; the kind and features of each part are read from the names of its Commons "
                  "categories. https://commons.wikimedia.org")
HARDWARE_PACKS = {
    "commons_fasteners": (build_commons_fasteners, COMMONS_CREDIT.format(
        what="categories of nails, screws (by kind, head and drive), bolts, nuts, washers, anchors, rivets, staples, "
             "pins, hose clamps, cable ties and thread gauges")),
    "commons_door_hardware": (build_commons_door_hardware, COMMONS_CREDIT.format(
        what="categories of hinges, locks, keys, door furniture, cabinet and furniture hardware and window hardware")),
    "commons_building_hardware": (build_commons_building_hardware, COMMONS_CREDIT.format(
        what="categories of brackets, structural connectors, shelf and wall hardware, hooks, chain, rope and knots, "
             "pulleys, casters, springs, fence, gate and garage door hardware, mailboxes and house numbers")),
    "commons_plumbing_electrical": (build_commons_plumbing_electrical, COMMONS_CREDIT.format(
        what="categories of pipe fittings, valves, traps, faucets, toilet parts, electrical boxes, outlets, switches, "
             "connectors, breakers, panels, cables and NEMA plug types")),
    "commons_building_materials": (build_commons_building_materials, COMMONS_CREDIT.format(
        what="categories of lumber, sheet goods, drywall, pipe materials, tapes, sandpaper, glues and sealants")),
    "commons_hand_tools_trades": (build_commons_hand_tools_trades, COMMONS_CREDIT.format(
        what="categories of hand tools, automotive, HVAC, plumbing, electrical, masonry, painting and drywall tools, "
             "ladders, scaffolding and material handling")),
    "commons_power_tools": (build_commons_power_tools, COMMONS_CREDIT.format(
        what="categories of power tools, blades and bits, air tools, pressure washers and outdoor power equipment")),
    "commons_shop_machines": (build_commons_shop_machines, COMMONS_CREDIT.format(
        what="categories of woodshop and metal shop machines, their tooling, welding and cutting equipment and "
             "machinists' measuring tools")),
    "commons_ppe": (build_commons_ppe, COMMONS_CREDIT.format(
        what="categories of respirators, hearing, eye and face protection, hard hats, gloves, high-visibility "
             "clothing, safety boots and fall protection")),
    "commons_sewing_food_equipment": (build_commons_sewing_food_equipment, COMMONS_CREDIT.format(
        what="categories of sewing machines, sergers, sewing tools and food-preparation equipment")),
    "abo_hardware": (build_abo_hardware,
                     "Amazon Berkeley Objects (ABO), CC BY 4.0, https://amazon-berkeley-objects.s3.amazonaws.com/"
                     "index.html: data and catalogue images by Amazon.com; dataset by Matthieu Guillaumin, Thomas "
                     "Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC "
                     "Berkeley). Answers from each listing's own name, brand, finish, material and the sizes its name "
                     "states."),
    "nmah_hardware_tools": (build_nmah_hardware_tools,
                            "National Museum of American History, Smithsonian Institution: open-access records and "
                            "pictures released as CC0 (https://www.si.edu/openaccess), read from the Smithsonian "
                            "open-access bucket (https://registry.opendata.aws/smithsonian-open-access/). Answers "
                            "from each record's own object name, maker, date, place and materials."),
}

# How many pictures a full build takes from each (Commons answers about one picture a second; its hardware
# categories are small, tens to a few hundred files each).
HARDWARE_LIMITS = {
    "commons_fasteners": 1500,
    "commons_door_hardware": 1500,
    "commons_building_hardware": 1500,
    "commons_plumbing_electrical": 1200,
    "commons_building_materials": 800,
    "commons_hand_tools_trades": 2000,
    "commons_power_tools": 1500,
    "commons_shop_machines": 1500,
    "commons_ppe": 800,
    "commons_sewing_food_equipment": 800,
    "abo_hardware": 1000,            # about 1,100 usable listings with an English name
    "nmah_hardware_tools": 800,
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one hardware and tools pack builder.")
    parser.add_argument("key", choices=sorted(HARDWARE_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = HARDWARE_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
