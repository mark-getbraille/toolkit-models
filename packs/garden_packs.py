"""Picture packs for GARDENING AND LAWN CARE: vegetable, herb and flower gardens, fruit trees and houseplants in pots,
soil and compost, seed packets and plant labels (read only where the file's own words give the plant's name), seed
starting, pruning, lawns, lawn grasses and crabgrass, and leaf symptoms of plant diseases and deficiencies. Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns
[(file name, JPEG bytes or None, row)]. The limit counts pictures.

The owner's request of 2026-11-22 ("life skills"). Plants by species (iNaturalist and GBIF), crops and their
diseases (agml_plant_health, PlantVillage, PlantDoc), weeds (agml_weeds, DeepWeeds), lawn and garden chemicals
(chemical_packs.py), lawn mowers (hardware and device packs; their repair belongs to the home repair helper), and the
garden tools already in other packs (garden forks, trowels, hoses, watering cans, wheelbarrows, shovels, rakes) are
not asked again (packs/test_garden.py checks every Commons category and Open Images label).

Answers say only what the source says: a Commons category's name with a fixed plain line written here, or an Open
Images label people confirmed. A seed packet or plant label is read only where the file's own title or description
names the plant (SEED_PLANT: "a seed packet of 'Brandywine' tomatoes, as the file's own words say"); nothing is read
off the picture (weed killers and fertilisers are chemical_packs', with their label note). Note:
  PLANT_SAFETY   after answers about plants or symptoms: a picture alone cannot confirm a plant disease; local
                 cooperative extension offices can identify it.

The packs (all open: CC0, public domain or CC BY files; Open Images labels CC BY 4.0):
  commons_garden_growing   Commons: vegetable, kitchen, herb, community and flower gardens, flower beds and
                           allotments; fruit and apple trees; houseplants and potted plants; seedlings, planting and
                           transplanting, cold frames, cloches and trellises.
  commons_garden_care      Commons: compost, composting, compost bins and worm composting, soil testing, seed packets
                           and plant labels, pruning and pruned trees, loppers and grafting.
  commons_lawn_care        Commons: lawns, mowing (lawn and grass files only), sod, the common lawn grasses by name
                           (Kentucky bluegrass, perennial ryegrass, zoysia, St. Augustine) and crabgrass.
  commons_plant_problems   Commons: chlorosis, powdery mildew, leaf spot, late blight and sooty mould, each with what
                           it looks like on the leaves.
  open_images_garden       Open Images V7: gardens, lawns and grass, compost, mulch and soil, seedlings, seeds,
                           greenhouses, herbs (basil, rosemary, thyme, sage, parsley, chives, oregano, dill), garden
                           flowers (roses, tulips, sunflowers, hydrangeas), hedges, moss, groundcover, succulents,
                           cacti and bonsai, pruning shears and garden tools, weeds and dandelions, fruit trees.

Commons has no category with free files for raised beds, container gardening, sprinklers, soaker hoses, rain
barrels, lawn weeds, downy mildew, blossom end rot or the USDA zone maps (checked 2026-11-22): the kit's
garden_sources.py lists them; the zone map and soil pages are in the reference library (garden:).

What was looked at and left out (extension service photos, the USDA PLANTS image gallery, Pinterest and others) is
in the kit's garden_sources.py (GARDEN_NOT_INCLUDED).

    python packs/garden_packs.py commons_plant_problems --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import say  # noqa: F401 - kept for the quick check's messages
from gaps_oi_packs import group, build_oi_gap, QUICK

ASK_WHAT = "What is this?"
ASK_PLACE = "What kind of garden or place is this?"
ASK_DOING = "What is happening in this picture?"
ASK_PLANT = "What is wrong with this plant?"

PLANT_SAFETY = ("A picture alone cannot confirm a plant problem; your local cooperative extension office can "
                "identify it.")


def spec(category, words, note="", deeper=True, question=ASK_WHAT, pattern=None):
    """A Commons spec for home_packs.build_commons_topic: (category, deeper, [(question, "This is <words>." and the
    note)]) and an optional pattern of words a file's title or description must have."""
    out = (category, deeper, [(question, f"This is {words}." + (f" {note}" if note else ""))])
    return out + ((pattern,) if pattern is not None else ())


def problem(category, words, looks, deeper=True, pattern=None):
    """A plant problem: "This plant shows <words>: <what it looks like>." and the extension note; pattern: words a
    file's title or description must have (or, written as a negative lookahead, must not have)."""
    out = (category, deeper, [(ASK_PLANT, f"This plant shows {words}: {looks}. {PLANT_SAFETY}")])
    return out + ((pattern,) if pattern is not None else ())


# Chlorosis files that show a plant born without chlorophyll (albino or variegated forms) are not a deficiency.
NOT_ALBINO = re.compile(r"^(?!.*\b(albin\w*|variegat\w*|chimera)\b)", re.I | re.S)


# Broad categories (Soil, Mulch, Turf) hold other things too: only files whose own words say garden, lawn, plant or
# similar.
GARDEN_WORDS = re.compile(r"\b(gardens?|gardening|lawns?|plants?|planting|beds?|pots?|grass|yards?|allotments?|"
                          r"vegetables?|flowers?|seedlings?|compost)\b", re.I)

# ----------------------------------------------------------------- Commons: growing

GROWING = [
    spec("Vegetable gardens", "a vegetable garden", question=ASK_PLACE),
    spec("Kitchen gardens", "a kitchen garden, where vegetables, herbs and fruit are grown for the household",
         question=ASK_PLACE),
    spec("Herb gardens", "a herb garden", question=ASK_PLACE),
    spec("Community gardens", "a community garden, shared by people of the neighbourhood", question=ASK_PLACE),
    spec("Allotments", "an allotment, a rented plot for growing food", question=ASK_PLACE),
    spec("Flower beds", "a flower bed", question=ASK_PLACE),
    spec("Flower gardens", "a flower garden", question=ASK_PLACE),
    spec("Fruit trees", "a fruit tree"),
    spec("Apple trees", "an apple tree"),
    spec("Houseplants", "a houseplant, a plant grown indoors"),
    spec("Potted plants", "a potted plant", deeper=False),
    spec("Seedlings", "seedlings: young plants just grown from seed"),
    spec("Planting", "planting", question=ASK_DOING, pattern=GARDEN_WORDS),
    spec("Transplanting", "transplanting: moving a young plant to its new place", question=ASK_DOING),
    spec("Cold frames", "a cold frame: a low box with a clear lid that protects young plants from cold"),
    spec("Cloches", "a cloche: a clear cover put over a plant to protect it from cold", pattern=GARDEN_WORDS),
    spec("Trellises", "a trellis: a frame that climbing plants grow up"),
]

# ----------------------------------------------------------------- Commons: care

# Seed packets and plant labels: the plant is named only from the file's own words (seed_plant in the module test).
CARE = [
    spec("Compost", "compost: rotted plant waste used to feed the soil", pattern=GARDEN_WORDS),
    spec("Composting", "composting: turning kitchen and garden waste into compost", question=ASK_DOING),
    spec("Compost bins", "a compost bin, where kitchen and garden waste rots down into compost"),
    spec("Vermicomposting", "worm composting: worms turning food scraps into compost"),
    spec("Soil testing", "soil testing: checking the soil's pH and nutrients before planting"),
    spec("Seed packets", "a seed packet: the plant's name, sowing depth and spacing, days to harvest and when to "
                         "sow are usually printed on it"),
    spec("Plant labels", "a plant label (plant tag): it usually gives the plant's name, how much sun it needs, its "
                         "spacing and how tall it grows"),
    spec("Pruning", "pruning: cutting back branches to keep a plant healthy and in shape", question=ASK_DOING),
    spec("Pruned trees", "a pruned tree"),
    spec("Loppers", "loppers: long-handled pruning shears for thicker branches"),
    spec("Grafting", "grafting: joining a cutting of one plant onto the roots of another", question=ASK_DOING),
]

# ----------------------------------------------------------------- Commons: lawns

LAWN_CARE = [
    spec("Lawns", "a lawn", question=ASK_PLACE),
    spec("Mowing", "grass being mown", question=ASK_DOING, pattern=re.compile(r"\b(lawns?|grass|mow\w*|gardens?|"
                                                                            r"parks?|yards?)\b", re.I)),
    spec("Lawn mowing", "a lawn being mown", question=ASK_DOING),
    spec("Sod", "sod (turf): rolls of grass laid to make a new lawn"),
    spec("Poa pratensis", "Kentucky bluegrass (Poa pratensis), a cool-season lawn grass"),
    spec("Lolium perenne", "perennial ryegrass (Lolium perenne), a cool-season lawn grass"),
    spec("Zoysia", "zoysia grass, a warm-season lawn grass"),
    spec("Stenotaphrum secundatum", "St. Augustine grass (Stenotaphrum secundatum), a warm-season lawn grass of warm, "
                                    "humid places"),
    spec("Digitaria sanguinalis", "crabgrass (Digitaria sanguinalis), a common lawn weed"),
]

# ----------------------------------------------------------------- Commons: plant problems

PLANT_PROBLEMS = [
    problem("Chlorosis", "chlorosis", "the leaves turn pale yellow while the veins may stay green, often from a "
                                      "lack of iron or nitrogen or from poor roots", pattern=NOT_ALBINO),
    problem("Powdery mildew", "powdery mildew", "a white, powdery fungal coating on the leaves"),
    problem("Leaf spot", "leaf spot", "brown or black spots on the leaves, from a fungus or bacteria"),
    problem("Phytophthora infestans", "late blight", "dark, greasy-looking patches on tomato or potato leaves and "
                                                     "stems that spread fast in wet weather"),
    problem("Sooty mold", "sooty mould", "a black coating on leaves, growing on the sticky honeydew insects leave"),
]


def build_commons_garden_growing(limit):
    """The commons_garden_growing pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(GROWING, limit, "gardengrow")


def build_commons_garden_care(limit):
    """The commons_garden_care pack (see the module docstring), with the plant named on seed packets and labels
    where the file's own words give it."""
    from home_packs import build_commons_topic
    return with_seed_plants(build_commons_topic(CARE, limit, "gardencare"))


def build_commons_lawn_care(limit):
    """The commons_lawn_care pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(LAWN_CARE, limit, "lawncare")


def build_commons_plant_problems(limit):
    """The commons_plant_problems pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PLANT_PROBLEMS, limit, "plantprob")


# ----------------------------------------------------------------- seed packets: the plant from the file's own words

SEED_Q = "What plant is this seed packet or label for?"
# "Seed packet of Brandywine tomato", "Burpee tomato seeds", "Plant label: Lavandula angustifolia 'Hidcote'"
SEED_PLANT = re.compile(r"(?i:seed (?:packet|package|bag)s? (?:of|for)|plant (?:label|tag)s? (?:of|for)|label:)\s+"
                        r"(?P<plant>[A-Z'\"][\w'\" -]{2,40}?)(?=[.,;(]|\s+(?:seeds?|from|by|at|in)\b|$)"
                        r"|(?P<plant2>[A-Z][\w' -]{2,30}?) (?i:seeds? (?:packet|package)s?)\b")


def seed_plant(words):
    """The plant a seed packet's or label's own words name ("Brandywine tomato"), or ""."""
    m = SEED_PLANT.search(words or "")
    if not m:
        return ""
    plant = (m.group("plant") or m.group("plant2") or "").strip()
    if plant[:1] in "'\"" and plant[-1:] == plant[:1]:          # quoted as a whole: the quotes are not the name
        plant = plant[1:-1].strip()
    return plant if 2 < len(plant) <= 40 and not re.search(r"\d{3,}|IMG|DSC", plant) else ""


def with_seed_plants(entries):
    """entries with one more row for each seed packet or plant label picture whose own description (its "Write a
    short description" row) names the plant."""
    out = list(entries)
    for name, data, row in entries:
        if row.get("question") != build_packs.ALT_TEXT:
            continue
        picture = name or row.get("file", "").replace("pictures/", "", 1)
        if not re.search(r"seed packet|plant label|seed package|plant tag", " ".join(
                r["answer"] for n, _d, r in entries if (n or r.get("file", "").replace("pictures/", "", 1)) == picture
                and r.get("question") != build_packs.ALT_TEXT), re.I):
            continue
        plant = seed_plant(row["answer"])
        if plant:
            out.append((None, None, {"question": SEED_Q, "answer": f"It is for {plant}, as the file's own words say.",
                                     "credit": row.get("credit", ""), "file": f"pictures/{picture}"}))
    return out


# ----------------------------------------------------------------- Open Images

GARDEN_OI = [
    group("What garden things are in this picture?",
          {"Garden": "a garden", "Lawn": "a lawn", "Grass": "grass", "Compost": "compost", "Mulch": "mulch",
           "Soil": "soil", "Seedling": "seedlings", "Seed": "seeds", "Greenhouse": "a greenhouse",
           "Hedge": "a hedge", "Moss": "moss", "Groundcover": "groundcover plants", "Garden tool": "a garden tool",
           "Pruning shears": "pruning shears", "Fruit tree": "a fruit tree"}),
    group("What herbs are in this picture?",
          {"Herb": "herbs", "Basil": "basil", "Rosemary": "rosemary", "Thyme": "thyme", "Sage": "sage",
           "Parsley": "parsley", "Chives": "chives", "Oregano": "oregano", "Dill": "dill", "Kale": "kale",
           "Leaf vegetable": "leafy vegetables"}),
    group("What garden flowers or plants are in this picture?",
          {"Rose": "roses", "Tulip": "tulips", "Sunflower": "sunflowers", "Hydrangea": "hydrangeas",
           "Succulent plant": "succulents", "Cactus": "a cactus", "Bonsai": "a bonsai tree",
           "Perennial plant": "perennial plants", "Annual plant": "annual plants",
           "Herbaceous plant": "herbaceous plants"}),
    group("What weeds are in this picture?", {"Weed": "weeds", "Dandelion": "dandelions", "Clover": "clover"}),
    group("Does this picture show a plant problem?", {"Plant pathology": "a plant disease"}, PLANT_SAFETY),
]


def build_open_images_garden(limit):
    """The open_images_garden pack (see the module docstring)."""
    return build_oi_gap("open_images_garden", GARDEN_OI, limit, 9311)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
GARDEN_PACKS = {
    "commons_garden_growing": (build_commons_garden_growing, COMMONS_LICENCE.format(
        what="vegetable, herb and flower garden, fruit tree, houseplant and seed-starting")),
    "commons_garden_care": (build_commons_garden_care, COMMONS_LICENCE.format(
        what="compost, mulch, soil, seed packet and plant label, watering, pruning and garden tool")),
    "commons_lawn_care": (build_commons_lawn_care, COMMONS_LICENCE.format(what="lawn, lawn grass and lawn weed")),
    "commons_plant_problems": (build_commons_plant_problems, COMMONS_LICENCE.format(
        what="plant disease and leaf symptom")),
    "open_images_garden": (build_open_images_garden, OI_LICENCE),
}
GARDEN_LIMITS = {
    "commons_garden_growing": 1600,    # 17 categories
    "commons_garden_care": 1200,       # 11 categories
    "commons_lawn_care": 800,          # 9 categories
    "commons_plant_problems": 250,     # 5 categories, few free files each
    "open_images_garden": 3000,        # 39 labels
}
GARDEN_COMMONS_KEYS = ("commons_garden_growing", "commons_garden_care", "commons_lawn_care", "commons_plant_problems")


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a garden pack builder.")
    parser.add_argument("key", choices=sorted(GARDEN_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = GARDEN_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
