"""Pack builders for more openly licensed collections, used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question", "answer",
"credit"} and, when the photo's own title or description on Flickr mentions a child, "child": True (as in
expression_packs.py). The limit counts pictures.

  fashionpedia   Fashionpedia (Cornell and Google, 2020): everyday and fashion-event photos whose clothes were outlined
                 by people and labelled with an ontology made by fashion experts (garments, garment parts, and
                 attributes such as length, fit, pattern, neckline and sleeve type). The labels are CC BY 4.0; the
                 photos are NOT owned by Fashionpedia, so only photos whose own licence (recorded per photo in the
                 annotation file) is CC BY or public domain are used, each with its Flickr photographer named. Photos
                 from Unsplash, Pexels, Burst and Freestocks are left out: their own licences are not on the list of
                 allowed licences. "What is this person wearing?" "This person is wearing a long-sleeved, knee-length
                 floral dress with a V-neck, shoes and a bag." Fashionpedia has no colour labels, so answers name no
                 colours.

Collections looked at and left out, because their licence is not open (checked at the source in November 2026):
  CUB-200-2011 birds  https://www.vision.caltech.edu/datasets/cub_200_2011/ says "We do not own the copyrights to
                      these images. Their use is restricted to non-commercial research and educational purposes."
  PlantVillage        The original release (Hughes and Salathe, arXiv 1511.08060) puts the images under CC BY-SA 3.0
                      "with the clarification that algorithms trained on the data fall under the same license"; the
                      official copy (huggingface.co/datasets/mohanty/PlantVillage) is also CC BY-SA 3.0.
  PlantDoc            The GitHub repository says CC BY 4.0, but its paper (arXiv 1911.10317) says the authors
                      downloaded the images from Google Images and Ecosia: they do not own them, so that licence cannot
                      cover the pictures, and nothing records who does.
  Pl@ntNet-300K       Zenodo says CC BY 4.0 for the dataset, but its per-image list (version 2, Zenodo 10419064,
                      plantnet300K_metadata.csv) gives every one of its 306,087 photos as cc-by-sa, cc-by-nc or
                      cc-by-nc-sa: none is open.
  nocaps              Its images are Open Images (CC BY 2.0), but nocaps.org, its paper (arXiv 1812.08658) and its
                      GitHub pages give no licence for the captions; the "cc-by-2.0" tag on a third-party copy
                      (huggingface.co/datasets/HuggingFaceM4/NoCaps) is not from the authors and its own card says
                      "Licensing Information: More Information Needed". Without a licence the captions cannot be used.
                      (Its test captions are also not public.)

Answers are put together from each collection's own labels with fixed sentences (nothing is written by an AI model).

    python packs/more_open_packs.py fashionpedia --limit 8      (prints a few rows: a quick check of one builder)
"""

import collections
import concurrent.futures
import html
import json
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, say
from build_packs import listing_out_of_time  # noqa: E402
from food_packs import listed, count_pictures
from everyday_packs import RemoteZip, fetch_from_zip, a_or_an, number_word, plural
from expression_packs import mark_child, child_count


# ----------------------------------------------------------------- Fashionpedia

FP = "https://s3.amazonaws.com/ifashionist-dataset/"
# (annotation file, zip of its photos). The validation set comes first: it is small (15 MB), so a quick check needs
# only it; a full build reads the training set too (540 MB of annotations, a 3.3 GB zip read piece by piece).
FP_SETS = ((FP + "annotations/instances_attributes_val2020.json", FP + "images/val_test2020.zip"),
           (FP + "annotations/instances_attributes_train2020.json", FP + "images/train2020.zip"))
# Photo licences that may be used, from the address each licence entry gives: CC BY (any version), CC0 or the
# Public Domain Mark. Never SA, NC or ND, and not the Unsplash, Pexels, Burst or Freestocks licences.
FP_FREE = re.compile(r"creativecommons\.org/(licenses/by/(\d\.\d)/?$|publicdomain/(zero|mark)/)")
# Flickr's own licence numbers, read from the photo page: those that may be used (CC BY 2.0 and 4.0, no known
# copyright, United States Government work, CC0, Public Domain Mark).
FLICKR_FREE = {4, 7, 8, 9, 10, 11}
FP_ASK_ONE = "What is this person wearing?"
FP_ASK_MANY = "What are the people in this picture wearing?"
FP_CREDIT = "{who}, {licence}; clothing labels from Fashionpedia (Jia, Shi et al., 2020), CC BY 4.0"

# The main garments and accessories (category numbers 0-26) as plain words: (one, many).
FP_ITEMS = {
    "shirt, blouse": ("shirt", "shirts"), "top, t-shirt, sweatshirt": ("top", "tops"),
    "sweater": ("jumper (sweater)", "jumpers (sweaters)"), "cardigan": ("cardigan", "cardigans"),
    "jacket": ("jacket", "jackets"), "vest": ("waistcoat (vest)", "waistcoats (vests)"),
    "pants": ("trousers", "pairs of trousers"), "shorts": ("shorts", "pairs of shorts"),
    "skirt": ("skirt", "skirts"), "coat": ("coat", "coats"), "dress": ("dress", "dresses"),
    "jumpsuit": ("jumpsuit", "jumpsuits"), "cape": ("cape", "capes"), "glasses": ("glasses", "pairs of glasses"),
    "hat": ("hat", "hats"), "headband, head covering, hair accessory": ("headband or hair accessory",
                                                                       "headbands or hair accessories"),
    "tie": ("tie", "ties"), "glove": ("gloves", "gloves"), "watch": ("watch", "watches"), "belt": ("belt", "belts"),
    "leg warmer": ("leg warmers", "leg warmers"), "tights, stockings": ("tights", "tights"),
    "sock": ("socks", "socks"), "shoe": ("shoes", "shoes"), "bag, wallet": ("bag", "bags"),
    "scarf": ("scarf", "scarves"), "umbrella": ("umbrella", "umbrellas"),
}
# Words that are said without "a": "trousers", not "a trousers". Gloves, shoes and socks come in pairs, so one
# outlined shoe is still "shoes" (the other is usually hidden).
FP_NO_ARTICLE = {"trousers", "shorts", "glasses", "gloves", "leg warmers", "tights", "socks", "shoes", "jeans",
                 "leggings", "sweatpants", "culottes", "jodhpurs", "bloomers", "trunks", "boardshorts"}
FP_PAIRED = {"glove", "shoe", "sock", "leg warmer", "tights, stockings"}
FP_CLOTHES = {"shirt, blouse", "top, t-shirt, sweatshirt", "sweater", "cardigan", "jacket", "vest", "pants", "shorts",
              "skirt", "coat", "dress", "jumpsuit", "cape"}
# Garments that have sleeves and a neckline: a sleeve or neckline outline is put with the garment only when the
# photo has exactly one of these (the outlines are not linked to their garment).
FP_SLEEVED = {"shirt, blouse", "top, t-shirt, sweatshirt", "sweater", "cardigan", "jacket", "coat", "dress",
              "jumpsuit"}
# The kind of garment ("nickname" attributes) as plain words, where taking the brackets away is not enough.
FP_KINDS = {
    "classic (t-shirt)": "T-shirt", "polo (shirt)": "polo shirt", "ringer (t-shirt)": "ringer T-shirt",
    "raglan (t-shirt)": "raglan T-shirt", "crop (top)": "crop top", "tank (top)": "vest top (tank top)",
    "short (shorts)": "shorts", "dress (coat )": "dress coat", "cheongsams": "cheongsam", "jodhpur": "jodhpurs",
    "hip-huggers (pants)": "hipster trousers", "classic military (jacket)": "military jacket",
    "chanel (jacket)": "Chanel-style jacket", "mao (jacket)": "Mao jacket", "nehru (jacket)": "Nehru jacket",
    "norfolk (jacket)": "Norfolk jacket", "gypsy (skirt)": "tiered peasant skirt",
}
# Lengths, said before the garment ("a knee-length skirt"); for trousers "maxi" means full length.
FP_LENGTHS = {
    "above-the-hip (length)": "waist-length", "hip (length)": "hip-length", "micro (length)": "micro",
    "mini (length)": "mini", "above-the-knee (length)": "above-the-knee", "knee (length)": "knee-length",
    "below the knee (length)": "below-the-knee", "midi": "midi", "maxi (length)": "maxi",
    "floor (length)": "floor-length",
}
FP_SLEEVES = {"sleeveless": "sleeveless", "short (length)": "short-sleeved", "elbow-length": "elbow-length-sleeved",
              "three quarter (length)": "three-quarter-sleeved", "wrist-length": "long-sleeved"}
# Shapes and fits worth saying (symmetrical, regular fit and the like are left out).
FP_SHAPES = {
    "tight (fit)": "tight", "loose (fit)": "loose", "oversized": "oversized", "a-line": "A-line",
    "wide leg": "wide-leg", "flare": "flared", "bootcut": "bootcut", "bell bottom": "bell-bottom", "pencil": "pencil",
    "mermaid": "mermaid", "baggy": "baggy", "peplum": "peplum", "fit and flare": "fit-and-flare",
    "trumpet": "trumpet", "balloon": "balloon", "high low": "high-low",
}
# Waists, said only for trousers, shorts and skirts ("high-waisted jeans").
FP_WAISTS = {"high waist": "high-waisted", "low waist": "low-waisted"}
FP_PATTERNS = {
    "floral": "floral", "stripe": "striped", "check": "checked", "dot": "spotted", "leopard": "leopard-print",
    "camouflage": "camouflage", "geometric": "geometric-patterned", "abstract": "abstract-patterned",
    "paisley": "paisley", "argyle": "argyle", "houndstooth (pattern)": "houndstooth", "chevron": "chevron",
    "herringbone (pattern)": "herringbone", "fair isle": "Fair Isle", "zebra": "zebra-print",
    "cheetah": "cheetah-print", "snakeskin (pattern)": "snakeskin-print", "giraffe": "giraffe-print",
    "peacock": "peacock-print", "toile de jouy": "toile de Jouy", "plant": "leaf-patterned",
    "cartoon": "cartoon-print", "letters, numbers": "lettered", "plain (pattern)": "plain",
}
FP_FINISHES = {
    "distressed": "distressed", "washed": "washed", "quilted": "quilted", "pleat": "pleated", "ruched": "ruched",
    "tiered": "tiered", "frayed": "frayed", "perforated": "perforated", "embossed": "embossed",
    "sequin(a)": "sequinned", "bead(a)": "beaded", "rivet(a)": "studded", "smocking": "smocked",
    "suede": "suede", "crocodile": "crocodile-skin", "snakeskin": "snakeskin", "shearling": "shearling",
}
FP_OPENINGS = {"zip-up": "zip-up", "double breasted": "double-breasted", "lace up": "lace-up", "wrapping": "wrap"}
# Things said after the garment with "with".
FP_WITH = {"fur": "fur", "feather": "feathers", "gem": "gems", "cutout": "cut-outs", "slit": "a slit",
           "applique(a)": "appliqué", "gathering": "gathers"}
# Necklines, with their article.
FP_NECKS = {
    "crew (neck)": "a crew neck", "round (neck)": "a round neck", "v-neck": "a V-neck", "oval (neck)": "an oval neck",
    "u-neck": "a U-neck", "sweetheart (neckline)": "a sweetheart neckline", "boat (neck)": "a boat neck",
    "scoop (neck)": "a scoop neck", "square (neckline)": "a square neckline", "plunging (neckline)": "a plunging "
    "neckline", "halter (neck)": "a halter neck", "high (neck)": "a high neck", "turtle (neck)": "a turtleneck",
    "cowl (neck)": "a cowl neck", "straight across (neck)": "a straight neckline", "off-the-shoulder":
    "an off-the-shoulder neckline", "one shoulder": "one shoulder bare", "keyhole (neck)": "a keyhole neckline",
    "choker (neck)": "a choker neckline", "queen anne (neck)": "a Queen Anne neckline", "crossover (neck)":
    "a crossover neckline", "surplice (neck)": "a wrap-over neckline", "illusion (neck)": "a sheer illusion neckline",
    "asymmetric (neckline)": "an asymmetric neckline",
}
# Garment parts and decorations (not linked to a garment): (one, many).
FP_DETAILS = {
    "hood": ("a hood", "hoods"), "collar": ("a collar", "collars"), "lapel": ("lapels", "lapels"),
    "epaulette": ("epaulettes", "epaulettes"), "pocket": ("a pocket", "pockets"), "buckle": ("a buckle", "buckles"),
    "zipper": ("a zip", "zips"), "applique": ("an appliqué", "appliqués"), "bead": ("beads", "beads"),
    "bow": ("a bow", "bows"), "flower": ("a fabric flower", "fabric flowers"), "fringe": ("fringe", "fringe"),
    "ribbon": ("a ribbon", "ribbons"), "rivet": ("studs", "studs"), "ruffle": ("a ruffle", "ruffles"),
    "sequin": ("sequins", "sequins"), "tassel": ("a tassel", "tassels"),
}


def fp_kind(name, category):
    """The garment's kind from a nickname attribute ("duster (coat)" -> "duster coat")."""
    if name in FP_KINDS:
        return FP_KINDS[name]
    words = " ".join(re.sub(r"[()]", " ", name).split())
    return words.replace(" pants", " trousers") if category == "pants" else words


def fp_garment(category, attrs, n=1, sleeves="", neck=""):
    """One garment (or n alike) in plain words with its article or number, from its category and its attributes
    [(name, kind of attribute)]: "a long-sleeved, knee-length floral dress with a V-neck"."""
    names = [name for name, _ in attrs]
    kinds = [fp_kind(name, category) for name, group in attrs if group == "nickname"]
    one, many = FP_ITEMS[category]
    noun = kinds[0] if kinds else one
    first, middle = [], []
    if "sleeveless" in names:
        sleeves = "sleeveless"
    if sleeves:
        first.append(sleeves)
    length = next((FP_LENGTHS[name] for name in names if name in FP_LENGTHS), "")
    if length == "maxi" and category in ("pants", "shorts"):
        length = "full-length" if category == "pants" and noun not in ("jeans", "leggings", "sweatpants") else ""
    if length and category != "shorts":
        first.append(length)
    # At most one word each for the waist, shape, finish and pattern, so the answer stays easy to listen to.
    if category in ("pants", "shorts", "skirt"):
        middle += [FP_WAISTS[name] for name in names if name in FP_WAISTS][:1]
    middle += [FP_SHAPES[name] for name in names if name in FP_SHAPES][:1]
    middle += [FP_FINISHES[name] for name in names if name in FP_FINISHES][:1]
    middle += [FP_PATTERNS[name] for name in names if name in FP_PATTERNS and name != "plain (pattern)"][:1]
    if len(middle) < 2:
        middle += [FP_OPENINGS[name] for name in names if name in FP_OPENINGS][:1]
    pair = noun in FP_NO_ARTICLE or noun.endswith(("trousers", "shorts", "jeans"))
    if n > 1 and not pair:
        noun = many if noun == one else plural(noun)
    phrase = ", ".join(first) + (" " if first and middle else "") + " ".join(middle)
    phrase = f"{phrase} {noun}".strip()
    extras = [FP_WITH[name] for name in names if name in FP_WITH]
    if neck:
        extras.insert(0, neck)
    if extras:
        phrase += " with " + listed(extras)
    if n > 1:
        return f"{number_word(n)} " + (f"pairs of {phrase}" if pair else phrase)
    return phrase if pair else f"{a_or_an(phrase)} {phrase}"


def fp_answer(objects):
    """(question, answer) for one photo from its outlines [(category name, [(attribute name, kind of
    attribute)])], or None when no garment or accessory is outlined. A photo with two garments of the same kind
    (two skirts) shows more than one person and is asked about "the people"."""
    counts = collections.Counter(c for c, _ in objects)
    many = any(n > 1 for c, n in counts.items() if c in FP_CLOTHES)
    sleeved = [c for c in counts if c in FP_SLEEVED]
    sleeves, neck = "", ""
    if len(sleeved) == 1 and counts[sleeved[0]] == 1:
        lengths = {FP_SLEEVES[a] for c, attrs in objects if c == "sleeve" for a, _ in attrs if a in FP_SLEEVES}
        if len(lengths) == 1:
            sleeves = next(iter(lengths))
        necks = {FP_NECKS[a] for c, attrs in objects if c == "neckline" for a, _ in attrs if a in FP_NECKS}
        if len(necks) == 1:
            neck = next(iter(necks))
    alike = collections.Counter((c, tuple(attrs)) for c, attrs in objects if c in FP_CLOTHES)
    clothes = [fp_garment(c, attrs, n, *((sleeves, neck) if c in sleeved else ("", "")))
               for (c, attrs), n in alike.items()]
    others = []
    for category, n in counts.items():
        if category in FP_ITEMS and category not in FP_CLOTHES:
            one, several = FP_ITEMS[category]
            if category in FP_PAIRED or n == 1:
                others.append(one if one in FP_NO_ARTICLE else f"{a_or_an(one)} {one}")
            else:
                others.append(f"{number_word(n)} {several}")
    if not clothes and not others:
        return None
    who = "The people are" if many else "This person is"
    # Shoes, bags and other accessories come in a sentence of their own, so "a dress with a V-neck, a bag" is not
    # heard as a dress that has a bag.
    if clothes:
        answer = f"{who} wearing {listed(clothes)}."
        if others:
            answer += f" They also have {listed(others)}."
    else:
        answer = f"{who} wearing {listed(others)}."
    question = FP_ASK_MANY if many else FP_ASK_ONE
    details = [one if counts[c] == 1 else several for c, (one, several) in FP_DETAILS.items() if counts.get(c)]
    if details:
        garments = [c for c in counts if c in FP_CLOTHES]
        if not many and len(garments) == 1:
            noun = FP_ITEMS[garments[0]][0]
            answer += f" The {noun} {'have' if noun in FP_NO_ARTICLE else 'has'} {listed(details[:5])}."
        else:
            answer += f" The clothes have {listed(details[:5])}."
    return question, answer


def fp_licence_name(url):
    """ "CC BY 2.0", "CC0" or "Public Domain Mark" for a licence address, or "" when it may not be used."""
    m = FP_FREE.search(url or "")
    if not m:
        return ""
    if m.group(2):
        return f"CC BY {m.group(2)}"
    return "CC0" if m.group(3) == "zero" else "Public Domain Mark"


def flickr_id(url):
    """The Flickr photo number in a static picture address, or ""."""
    m = re.search(r"staticflickr\.com/\d+/(\d+)_[0-9a-f]+", url or "")
    return m.group(1) if m else ""


def flickr_page(s, photo):
    """What the photo's Flickr page says: {"page", "owner", "licence" (Flickr's number or None), "text" (title and
    description, used only to see whether a child is shown)}, or {} when the page cannot be read (the photo was
    deleted, or Flickr refused)."""
    for attempt in range(3):
        try:
            r = s.get(f"https://www.flickr.com/photo.gne?id={photo}", timeout=60)
            if r.status_code == 404:
                return {}
            if r.status_code == 200 and "/photos/" in r.url:
                page = r.text
                owner = re.search(r'data-track="attributionNameClick">(?:By: )?([^<]+)<', page)
                licence = re.search(r'"license":(\d+)', page)
                title = re.search(r'<meta property="og:title" content="([^"]*)"', page)
                about = re.search(r'<meta property="og:description" content="([^"]*)"', page)
                return {"page": r.url.split("?")[0], "owner": clean(owner.group(1)) if owner else "",
                        "licence": int(licence.group(1)) if licence else None,
                        "text": " ".join(html.unescape(m.group(1)) for m in (title, about) if m)}
            if r.status_code not in (429, 500, 502, 503):
                return {}
        except Exception:  # noqa: BLE001 - network trouble: wait and try again
            pass
        time.sleep(5 * (attempt + 1))
    return {}


def fp_candidates(s, annotations, zip_url):
    """[(photo record, licence name, zip address, question, answer)] for one annotation file's photos whose own
    licence may be used and that have a garment or accessory outlined."""
    data = s.get(annotations, timeout=1800).json()
    free = {l["id"]: fp_licence_name(l.get("url")) for l in data["licenses"]}
    categories = {c["id"]: c["name"] for c in data["categories"]}
    attributes = {a["id"]: (a["name"], a.get("supercategory", "")) for a in data["attributes"]}
    objects = collections.defaultdict(list)
    for a in data["annotations"]:
        objects[a["image_id"]].append((categories[a["category_id"]],
                                       [attributes[t] for t in sorted(a.get("attribute_ids") or [])
                                        if t in attributes]))
    out, kept = [], collections.Counter()
    for image in data["images"]:
        licence = free.get(image.get("license"), "")
        kept[licence or "not open"] += 1
        if not licence or image["id"] not in objects:
            continue
        got = fp_answer(objects[image["id"]])
        if got:
            out.append((image, licence, zip_url) + got)
    say(f"Fashionpedia {annotations.rsplit('/', 1)[-1]}: {len(data['images'])} photos, by licence {dict(kept)}; "
        f"{len(out)} usable")
    return out


def build_fashionpedia(limit):
    """The Fashionpedia pack's pictures: [(name, JPEG, row)]. Reads the validation annotations (and the training
    annotations when the validation set has too few photos), keeps photos whose own licence is CC BY or public
    domain, checks each photo's Flickr page (the photographer's name, and that the photo is still under a free
    licence there) and reads the photos from the dataset's zips piece by piece."""
    s, candidates = session(), []
    for annotations, zip_url in FP_SETS:
        candidates += fp_candidates(s, annotations, zip_url)
        if len(candidates) >= limit * 1.4 + 10:
            break
    random.Random(61).shuffle(candidates)
    candidates = candidates[:int(limit * 1.3) + 4]

    def credited(candidate):
        """The candidate with its credit and child mark, or None when Flickr now shows a licence that is not free."""
        image, licence, zip_url, question, answer = candidate
        if listing_out_of_time():          # half the time is gone: keep the photos already checked, fetch them
            return None
        photo = flickr_id(image.get("original_url"))
        info = flickr_page(s, photo) if photo else {}
        if info.get("licence") is not None and info["licence"] not in FLICKR_FREE:
            return None
        if info.get("owner"):
            who = f"Photo by {info['owner']} ({info['page']})"
        elif photo:
            who = f"Flickr photo {photo} (https://www.flickr.com/photo.gne?id={photo})"
        else:
            who = f"Photo {image.get('original_url') or image['file_name']}"
        row = {"question": question, "answer": answer, "credit": FP_CREDIT.format(who=who, licence=licence)}
        return image, zip_url, mark_child(row, info.get("text", ""))

    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        checked = [c for c in pool.map(credited, candidates) if c]
    say(f"Fashionpedia: {len(checked)} of {len(candidates)} photos still free on Flickr (or no longer there)")
    out = []
    for _, zip_url in FP_SETS:
        wanted = [(image, row) for image, z, row in checked if z == zip_url]
        if not wanted:
            continue
        zipped = RemoteZip(zip_url)
        where = {name.rsplit("/", 1)[-1]: (offset, size, method) for name, offset, size, method in zipped.entries()}
        items = [(f"fashionpedia-{image['file_name']}", where[image["file_name"]], row) for image, row in wanted
                 if image["file_name"] in where]
        out += fetch_from_zip(zipped, items, workers=6)
    random.Random(62).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- the packs

MORE_OPEN_PACKS = {
    "fashionpedia": (build_fashionpedia, "Fashionpedia (Menglin Jia, Mengyun Shi, Mikhail Sirotenko, Yin Cui, Claire "
                                         "Cardie, Bharath Hariharan, Hartwig Adam and Serge Belongie, 'Fashionpedia: "
                                         "Ontology, Segmentation, and an Attribute Localization Dataset', ECCV 2020): "
                                         "annotations and ontology CC BY 4.0, https://fashionpedia.github.io/home/ "
                                         "(terms: https://fashionpedia.github.io/home/data_license.html). Fashionpedia "
                                         "does not own the photos: only photos under CC BY or public domain are "
                                         "included, each credited below with its photographer and Flickr page. "
                                         "Answers written from the labels with fixed sentences; the labels give no "
                                         "colours."),
}

# How many pictures a full build takes from each collection (about what each offers after the licence checks).
MORE_OPEN_LIMITS = {
    "fashionpedia": 5000,             # about 13% of 46,800 photos are CC BY 2.0 (about 6,000), fewer after Flickr checks
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one of the more open pack builders.")
    parser.add_argument("key", choices=sorted(MORE_OPEN_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = MORE_OPEN_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} marked child")
    return 0


if __name__ == "__main__":
    sys.exit(main())
