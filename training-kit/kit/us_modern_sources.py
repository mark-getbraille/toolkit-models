"""MODERN AMERICA collections for the Picture Model Training Kit (roughly the 1990s to today: everyday places, controls,
holidays, eating out, getting around, public services, medicines and forms) that cannot be ready-made packs because
of their licence. The open ones (US agency photos, controls and machines, holidays, eating out, getting around,
public places, blank federal forms and ImageInWords) are packs in packs/us_modern_packs.py.

As in us_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it, only when the user ticks the matching choice. Every
licence was checked at its source in November 2026 (the link and the exact terms line are in each entry).

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia).
  "research"       terms that allow research use only, or that conflict: personal use only (--personal-research
                   with --accept-research-terms).

Answers are fixed sentences from each source's own records (a Commons category's name, the C3PI record's drug name,
strength, imprint, colour and shape), never written by an AI model.

Safety (packs/SOURCE-RULES.md): no sexual content (files whose words name nudity, underwear or swimwear are left
out); children only in everyday clothed scenes, and every row whose words name a child is marked "child"; graduations
are adults only and school cafeterias are not taken (as in the packs).

The collections (US_MODERN_SOURCES):
  share-alike
    commons_us_modern_sa   Wikimedia Commons: the categories of the six open Commons packs of us_modern_packs.py
                           (controls and machines, holidays, eating out, getting around, public places), files under
                           CC BY-SA or GFDL, with the category's question and the file's own caption.
  research
    c3pi_pills             NLM's Computational Photography Project for Pill Identification (C3PI, 2009-2018;
                           https://data.lhncbc.nlm.nih.gov/public/Pills/): consumer-grade phone and camera photos and
                           segmented reference photos of US prescription pills, with each record's drug name and
                           strength, imprint, colour, shape and labeler. "What pill is this?" -> "This is Labetalol
                           Hydrochloride Tablets USP (labetalol hydrochloride): a yellow, round tablet with "4364" and
                           "TEVA" pressed into it, from Teva." / "What is written on this pill?" Its data.gov record
                           (https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-
                           c3pi) gives the licence "http://opendefinition.org/licenses/odc-odbl/" AND says "Images and
                           metadata are for research and development purposes only."; the photos were taken by
                           Medicos Consultants LLC for NLM ("<Attribution>Medicos Consultants LLC.</Attribution>" in
                           every record). The stricter line wins: research, personal use only.

Needing sign-up (US_MODERN_SIGN_UP has the links and the free key or secret each needs), looked at and not included
(US_MODERN_NOT_INCLUDED, with the reason of each) and the owners to ask for permission
(US_MODERN_PERMISSION_CANDIDATES: the organisation, what they have, their terms line and contact page).

US_MODERN_PICTURE_MAKING_OK holds the collections without people: c3pi_pills. Not the Commons entry (people in
restaurants, stations and at holidays).

    python kit/us_modern_sources.py c3pi_pills --cap 8     (a quick check; prints a few rows)
"""

import json
import os
import random
import re
import urllib.parse
import xml.etree.ElementTree as ET

from extra_sources import USER_AGENT, per_label, research, say
from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, clean

WHAT_Q = "What is this?"
PLACE_Q = "What kind of place is this?"
HAPPENING_Q = "What is happening here?"
PILL_Q = "What pill is this?"
IMPRINT_Q = "What is written on this pill?"
NOT_SHOWN = re.compile(r"\b(swim\w*|bikini\w*|bathing suits?|underwear|lingerie|bras?|nude|naked|topless|sexy|"
                       r"sexual\w*|erotic\w*|crime scenes?|evidence photo\w*|mug ?shots?|high school|kindergarten|"
                       r"elementary school)\b", re.I)


# ----------------------------------------------------------------- share-alike: Commons modern-America categories

# (category, question, answer, also its subcategories) - the categories of packs/us_modern_packs.py.
US_MODERN_SA = (
    [(c, WHAT_Q, a, True) for c, a in (
        ("Dishwashers", "This is a dishwasher."), ("Clothes dryers", "This is a clothes dryer."),
        ("Electric ovens", "This is an electric oven."), ("Television remote controls", "This is a TV remote control."),
        ("Supermarket self-checkouts", "This is a self-checkout in a supermarket."),
        ("Payment terminals", "This is a card payment terminal (card reader)."),
        ("Vending machines in the United States", "This is a vending machine in the USA."),
        ("Keypads", "This is a keypad."), ("Light switches", "This is a light switch."),
        ("Smoke detectors", "This is a smoke detector."),
        ("Pedestrian signals in the United States", "This is a pedestrian signal in the USA."),
        ("Pedestrian signal push buttons in the United States", "This is a pedestrian push button at a US "
                                                                "crossing."),
        ("Parking meters in the United States", "This is a parking meter in the USA."),
        ("Curb cuts in the United States", "This is a curb cut (curb ramp) in the USA."))]
    + [(c, HAPPENING_Q, a, True) for c, a in (
        ("Thanksgiving in the United States", "This is Thanksgiving in the USA."),
        ("Halloween in the United States", "This is Halloween in the USA."),
        ("Independence Day (United States)", "This is the Fourth of July, Independence Day in the USA."),
        ("Christmas lights in the United States", "These are Christmas lights in the USA."),
        ("Tailgate parties", "This is a tailgate party before a game."),
        ("State fairs in the United States", "This is a state fair in the USA."),
        ("Parades in the United States", "This is a parade in the USA."),
        ("Farmers' markets in the United States", "This is a farmers market in the USA."),
        ("Voting in the United States", "This is voting in an election in the USA."))]
    + [(c, PLACE_Q, a, True) for c, a in (
        ("Diners in the United States", "This is an American diner."),
        ("Interiors of fast food restaurants", "This is the inside of a fast-food restaurant."),
        ("Food trucks in the United States", "This is a food truck in the USA."),
        ("Coffee shops in the United States", "This is a coffee shop in the USA."),
        ("Supermarket aisles", "This is a supermarket aisle."),
        ("New York City Subway", "This is the New York City Subway."),
        ("Washington Metro stations", "This is a Washington Metro station."),
        ("Bus stops in the United States", "This is a bus stop in the USA."),
        ("Interiors of airports in the United States", "This is the inside of an airport in the USA."),
        ("Gas stations in the United States", "This is a gas station in the USA."),
        ("Interiors of post offices in the United States", "This is the inside of a US post office."),
        ("Pharmacies in the United States", "This is a pharmacy in the USA."),
        ("Laundromats in the United States", "This is a laundromat in the USA."),
        ("Interiors of libraries in the United States", "This is the inside of a library in the USA."),
        ("Hotel lobbies in the United States", "This is a hotel lobby in the USA."))])


def prepare_commons_us_modern_sa(source, data_dir, work, cap):
    """Wikimedia Commons modern-America categories, files under CC BY-SA or GFDL (home_sources.commons_sa_items:
    the categories share the cap; rows whose words name a child are marked "child"). Files whose words name
    swimwear, underwear, evidence photos or school graduations are left out too."""
    items = commons_sa_items(US_MODERN_SA, cap, source.test, "usmodern-sa")
    left_out = {i[0] for i in items if NOT_SHOWN.search(f"{i[0]} {i[2]['answer']}")}    # every row of that file
    items = [i for i in items if i[0] not in left_out]
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- research: C3PI pill photos (NLM)

C3PI = "https://data.lhncbc.nlm.nih.gov/public/Pills/"
C3PI_RECORD = "https://catalog.data.gov/dataset/computational-photography-project-for-pill-identification-c3pi"
C3PI_DISCS = 110                      # PillProjectDisc1 ... PillProjectDisc110, one ALLXML/<disc>.xml each
# The kinds of picture taken: consumer-grade photos (JPEG, about 0.2 to 1 MB) and the segmented reference photos
# (PNG, about 3 MB); not the raw camera files (CR2), the videos (WMV) or the 100 MB calibrated PNGs.
C3PI_KINDS = {"C3PI_Test": "a consumer-grade photo", "MC_CHALLENGE_V1.0": "a consumer-grade photo",
              "MC_C3PI_REFERENCE_SEG_V1.6": "a reference photo"}
C3PI_MOST_BYTES = 12_000_000
IMPRINT_KIND = {"DEBOSSED": "pressed into it", "EMBOSSED": "raised on it", "PRINTED": "printed on it",
                "ENGRAVED": "engraved on it"}
SHAPES = {"ROUND": "round", "OVAL": "oval", "CAPSULE": "capsule-shaped", "TRIANGLE": "triangular",
          "SQUARE": "square", "RECTANGLE": "rectangular", "DIAMOND": "diamond-shaped", "PENTAGON": "five-sided",
          "HEXAGON": "six-sided", "OCTAGON": "eight-sided", "TEAR": "teardrop-shaped", "FREEFORM": "irregular",
          "BULLET": "bullet-shaped", "SEMI-CIRCLE": "half-round", "TRAPEZOID": "trapezoid-shaped",
          "DOUBLE CIRCLE": "double-circle-shaped", "CLOVER": "clover-shaped", "GEAR": "gear-shaped",
          "HEART": "heart-shaped", "KIDNEY": "kidney-shaped", "RIGHT TRIANGLE": "triangular"}


def drug_name(text):
    """A record's drug name as said in a sentence: "STRATTERA 10MG" -> "Strattera 10 mg"; "LABETALOL HYDROCHLORIDE
    Tablets USP" -> "Labetalol Hydrochloride Tablets USP"."""
    words = []
    for w in clean(text).split():
        if re.fullmatch(r"(USP|ER|XR|SR|XL|CR|DR|ODT|HCL|HCT|EC|IR|LA|CD|DS)", w.upper()):
            words.append(w.upper())
        elif re.match(r"^[\d.,/]+(MG|MCG|G|ML|%|UNITS?)$", w.upper()):
            words.append(re.sub(r"(?i)([\d.,/]+)(mg|mcg|g|ml|%|units?)", lambda m: f"{m.group(1)} "
                                f"{m.group(2).lower()}", w))
        elif w.upper() in ("MG", "MCG", "ML"):
            words.append(w.lower())
        else:
            words.append(w[:1].upper() + w[1:].lower())
    return re.sub(r"(\d) (%)", r"\1\2", " ".join(words))


def imprint_words(imprint):
    """ "E;720;E;720" -> ["E", "720"]: the imprint's parts (one per line or side), each once."""
    return list(dict.fromkeys(p.strip() for p in (imprint or "").split(";") if p.strip()))


def pill_answer(record, name):
    """ "This is Strattera 10 mg (atomoxetine hydrochloride): a blue and white capsule with "Lilly" and "3227"
    printed on it, from Eli Lilly." from a C3PI record (dict of its fields; "Color" is a list)."""
    generic = clean(record.get("GenericName"))
    text = f"This is {name}"
    if generic and generic.lower().split()[0] not in name.lower():
        text += f" ({generic.lower()})"
    colours = [c.lower() for c in record.get("Color") or [] if c]
    shape = record.get("Shape", "").upper()
    form = "capsule" if shape == "CAPSULE" else "tablet"
    look = " and ".join(colours)
    shape_word = "" if shape == "CAPSULE" else SHAPES.get(shape, "")
    describe = ", ".join(x for x in (look, shape_word) if x)
    text += f": {'an' if describe[:1] in 'aeiou' and describe else 'a'} {describe + ' ' if describe else ''}{form}"
    parts = imprint_words(record.get("Imprint"))
    if parts:
        how = IMPRINT_KIND.get(record.get("ImprintType", "").upper(), "on it")
        text += " with " + " and ".join(f'"{p}"' for p in parts[:4]) + f" {how}"
    labeler = clean(record.get("LabeledBy")).rstrip(".,")
    if labeler:
        text += f", from {drug_name(labeler)}"
    return text + "."


def c3pi_records(xml_text):
    """[dict] for the pictures of one ALLXML disc file: each Image's fields (Color as a list, File's Name, Type and
    Size flattened)."""
    out = []
    root = ET.fromstring(xml_text)
    for image in root.iter("Image"):
        record = {"Color": []}
        for child in image:
            if child.tag == "Color":
                record["Color"].append(clean(child.text))
            elif child.tag == "File":
                for f in child:
                    record["File" + f.tag] = clean(f.text)
            else:
                record[child.tag] = clean(child.text)
        out.append(record)
    return out


def c3pi_names(work):
    """{image path: the drug name and strength} from the project's directory of images (16 MB, kept in work)."""
    import requests
    path = os.path.join(work, "c3pi_directory_of_images.txt")
    if not os.path.exists(path):
        r = requests.get(C3PI + "directory_of_images.txt", timeout=300, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    names = {}
    with open(path, encoding="latin-1") as f:
        for line in f:
            parts = line.rstrip("\n").split("|")
            if len(parts) >= 5:
                names[parts[2].split("/")[-1]] = parts[4]
    return names


def c3pi_rows(record, disc, names):
    """[(file name, address, row)] for one C3PI record, or [] when it is not a picture this entry takes."""
    kind = C3PI_KINDS.get(record.get("Class") or record.get("Layout") or "")
    file_name = record.get("FileName", "")
    if not kind or record.get("FileType") not in ("JPG", "PNG") or not file_name:
        return []
    if int(record.get("FileSize") or 0) > C3PI_MOST_BYTES:
        return []
    name = drug_name(names.get(file_name) or record.get("ProprietaryName") or record.get("GenericName") or "")
    if not name:
        return []
    url = f"{C3PI}{disc}/images/{urllib.parse.quote(file_name, safe='!')}"
    credit = (f"C3PI, US National Library of Medicine (photo by Medicos Consultants LLC for NLM), NDC "
              f"{record.get('NDC11', '')}, {kind}; research and development use only ({C3PI_RECORD})")
    base = {"split": "", "credit": credit, "place": "USA", "place_kind": "origin"}
    local = "c3pi-" + re.sub(r"[^\w-]", "_", file_name.rsplit(".", 1)[0]) + ".jpg"
    rows = [(local, url, dict(base, question=PILL_Q, answer=pill_answer(record, name)))]
    parts = imprint_words(record.get("Imprint"))
    readable = record.get("RatingImprint", "Clear") in ("Clear", "Partial", "")
    if parts and readable:
        how = IMPRINT_KIND.get(record.get("ImprintType", "").upper(), "on it")
        rows.append((local, url, dict(base, question=IMPRINT_Q, answer="It has " + " and ".join(
            f'"{p}"' for p in parts[:4]) + f" {how}.")))
    return rows


def prepare_c3pi_pills(source, data_dir, work, cap):
    """C3PI pill photos: discs chosen at random (one XML of about 1.2 MB each), an even share of pictures from each,
    one picture per drug and kind of photo at most per disc."""
    import requests
    names = c3pi_names(work)
    want = int((cap + source.test) * 1.15)
    discs = [f"PillProjectDisc{n}" for n in range(1, C3PI_DISCS + 1)]
    random.Random(2009).shuffle(discs)
    use = discs[:max(4, min(len(discs), want // 40 + 1))]
    per_disc = per_label(want, len(use))
    items = []
    for disc in use:
        try:
            r = requests.get(f"{C3PI}ALLXML/{disc}.xml", timeout=300, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()
            records = c3pi_records(r.content)
        except Exception as e:  # noqa: BLE001 - that disc is left out
            say(f"  C3PI {disc}: could not be read ({type(e).__name__})")
            continue
        random.Random(disc).shuffle(records)
        got, seen = 0, set()
        for record in records:
            if got >= per_disc:
                break
            key = (record.get("NDC11"), record.get("Class") or record.get("Layout"))
            rows = c3pi_rows(record, disc, names) if key not in seen else []
            if rows:
                seen.add(key)
                items += rows
                got += 1
        say(f"  C3PI {disc}: {got} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=3)


# ----------------------------------------------------------------- the table

US_MODERN_SOURCES = [
    # ---- share-alike
    Source("commons_us_modern_sa", "Wikimedia Commons: modern American controls, holidays, eating out, getting "
                                   "around and public places, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2500, 25, prepare_commons_us_modern_sa, "about 350 MB of pictures",
           terms="https://creativecommons.org/licenses/by-sa/4.0/",
           terms_summary="CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."),
    # ---- research
    Source("c3pi_pills", "US prescription pills: name, strength, imprint, colour and shape (NLM C3PI, personal use)",
           "ODbL listed on data.gov, and 'Images and metadata are for research and development purposes only' "
           f"({C3PI_RECORD}); photos by Medicos Consultants LLC for NLM",
           "Computational Photography Project for Pill Identification (C3PI), US National Library of Medicine; "
           "photos by Medicos Consultants LLC, https://data.lhncbc.nlm.nih.gov/public/Pills/", "research", 3000, 30,
           prepare_c3pi_pills, "about 2 GB (pictures fetched one by one)", terms=C3PI_RECORD,
           terms_summary=research("NLM (data.gov record): 'Images and metadata are for research and development "
                                  "purposes only.' Licence listed: ODbL.")),
]

# The collections a picture-making model may learn from: pill photos without people.
US_MODERN_PICTURE_MAKING_OK = {"c3pi_pills"}

US_MODERN_SIGN_UP = {
    "Flickr API: US federal agencies' photostreams (USDA, FEMA, NPS, Interior, DOT, NIH, VA, HUD, the White House, "
    "Census, NASA)":
        "https://www.flickr.com/services/apps/create/ : a FREE non-commercial Flickr API key exists (repository "
        "secret FLICKR_API_KEY), but Flickr's API terms (https://www.flickr.com/services/api/tos/) say you shall "
        "not 'Cache or store any Flickr user photos other than for reasonable periods in order to provide the "
        "service you are providing to Flickr users', which a training pack does. So no Flickr builder was made; "
        "the same agencies' photos come from their Commons copies (packs/us_modern_packs.py commons_us_agencies). "
        "Flickr (SmugMug) is in US_MODERN_PERMISSION_CANDIDATES.",
    "ImageInWords DCI_Test (112 human descriptions of SA-1B photos)":
        "https://ai.meta.com/datasets/segment-anything-downloads/ : the photos are Meta's SA-1B, downloaded after "
        "accepting the 'SA-1B Dataset Research License' (research only); the descriptions are CC BY 4.0 "
        "(https://github.com/google/imageinwords/tree/main/datasets/DCI_Test). Match each 'image' (sa_*.jpg) to "
        "its SA-1B file and use the own-pictures folder.",
    "DOT and FHWA photo libraries, NIH Image Gallery, VA and Census photos":
        "Most of these agencies publish their photos only on Flickr (free API key, see above) or on sites that "
        "refused this machine; none has its own open bulk API.",
    "ORBIT, VizWiz, Ego4D, Charades, Mapillary, YFCC100M (already in the kit)":
        "Not repeated: they are entries in sources.py, extra_sources.py, personal_sources.py, people_activity_"
        "sources.py and things_sources.py.",
}

US_MODERN_NOT_INCLUDED = {
    "Flickr API copies of agency photos": "Flickr's API terms forbid storing the photos beyond 'reasonable periods "
                                          "in order to provide the service you are providing to Flickr users' (see "
                                          "US_MODERN_SIGN_UP); the Commons copies are used instead.",
    "FEMA multimedia library, USDA media pages, SSA, USCIS, State Department passport and DOL forms":
        "public domain (US government works), but www.fema.gov, www.usda.gov/media, www.ssa.gov, www.uscis.gov, "
        "travel.state.gov and www.dol.gov refused this machine (403) in November 2026; FEMA and USDA photos come "
        "from their Commons copies, and the forms can be added to us_modern_packs.FORMS when their sites answer.",
    "USPS forms (about.usps.com/forms)":
        "the Postal Service is not covered by 17 U.S.C. 105 the way the federal departments are (it may hold "
        "copyright in its own works), and no open licence for its forms was found; ask USPS first "
        "(US_MODERN_PERMISSION_CANDIDATES).",
    "DailyMed package and label images (dailymed.nlm.nih.gov)":
        "labeling is 'submitted to the Food and Drug Administration (FDA) by companies' and 'NLM does not review "
        "any SPL content prior to publication' (https://dailymed.nlm.nih.gov/dailymed/about-dailymed.cfm); the "
        "package art is the companies' copyright, and NLM's copyright page says 'Transmission or reproduction of "
        "copyrighted items (beyond that allowed by fair use ...) requires the written permission of the copyright "
        "holders' (https://www.nlm.nih.gov/web_policies.html). In US_MODERN_PERMISSION_CANDIDATES.",
    "White House photo stream (Commons 'Photographs by White House photographers')":
        "public domain, but nearly every photo shows named politicians at official events, not everyday life.",
    "DOCUMERICA (EPA, 1971-1977)": "public domain, but from the 1970s; this collection is about 1990 onwards "
                                   "(loc_fsa and nara cover older America).",
    "School cafeterias and school-lunch trays (Commons 'School cafeterias')":
        "nearly every photo shows schoolchildren's faces; left out by the owner's rule (no children's faces).",
    "Classrooms in the United States (Commons)": "mostly schoolchildren; left out for the same reason.",
    "Open Images labels for remote controls, microwaves, ovens, dishwashers, gas stoves and washing machines":
        "already taken by everyday_packs.open_images_objects and home_packs.open_images_home (not repeated).",
    "Commons thermostats, microwave ovens, washing machines, elevator buttons, ATMs, ticket and check-in machines, "
    "gas cookers, dashboards and warning lights, tactile paving":
        "already home_packs.commons_appliances, commons_kitchen, mechanical_packs and disability_packs (not "
        "repeated).",
    "Commons categories for stove knobs, oven controls, microwave and washing-machine control panels, accessible "
    "pedestrian signals, DMV offices, rideshare pickup areas, baggage claim":
        "Commons has no such categories (searched in November 2026); the nearest ones are used.",
}

US_MODERN_PERMISSION_CANDIDATES = {
    "Flickr (SmugMug, Inc.)":
        "Has: the photostreams of most US federal agencies (USDA, FEMA, NPS, BLM, DOT, NIH, VA, HUD, the White "
        "House), mostly 'United States Government Work' or public domain. Terms line "
        "(https://www.flickr.com/services/api/tos/): you shall not 'Cache or store any Flickr user photos other "
        "than for reasonable periods in order to provide the service you are providing to Flickr users.' Ask "
        "(whether the public-domain government photos may be stored to teach a describer for blind people): "
        "https://www.flickr.com/help/contact (API support) or https://www.flickr.com/services/developer/.",
    "US National Library of Medicine (C3PI)":
        "Has: 133,000 pill photos with their records (the kit's c3pi_pills entry, research only). Terms: the "
        "data.gov record lists ODbL but says 'Images and metadata are for research and development purposes only.' "
        "Ask (whether training a describer for blind people, shared freely, is a use NLM agrees to): "
        "custserv@nlm.nih.gov (the record's contact point).",
    "DailyMed labelers (drug companies) and NLM":
        "Has: package and label photos of every US drug. Terms: the companies' copyright (see "
        "US_MODERN_NOT_INCLUDED). Ask: NLM, https://support.nlm.nih.gov/ (DailyMed), and the makers.",
    "United States Postal Service":
        "Has: PS forms (certified mail, change of address, customs) blind people receive. Terms: "
        "https://about.usps.com/termsofuse.htm (not read from this machine; to check before writing). Ask: "
        "https://about.usps.com/who/contact/ (USPS Office of the General Counsel, copyright permissions).",
}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import tempfile
    parser = argparse.ArgumentParser(description="Try one modern-America collection.")
    parser.add_argument("key", choices=[s.key for s in US_MODERN_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in US_MODERN_SOURCES if s.key == args.key)
    source.test = 0
    source.cap = args.cap
    data = args.data or tempfile.mkdtemp(prefix="usmodern-")
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
