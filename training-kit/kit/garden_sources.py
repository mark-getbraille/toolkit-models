"""GARDENING AND LAWN CARE for the Picture Model Training Kit (the owner's request of 2026-11-22). This file lists:
  - the ready-made packs built in packs/garden_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): commons_garden_growing, commons_garden_care, commons_lawn_care, commons_plant_problems,
    open_images_garden;
  - the share-alike Commons files of the main garden categories (garden_commons_sa: only with the share-alike
    choice, --with-wikipedia; an add-on trained with them is CC BY-SA);
  - the sources looked at and left out, with the reason (GARDEN_NOT_INCLUDED).

Already in the kit and not repeated: plants, mushrooms and animals by species (inaturalist, gbif_species and the US
and Canadian iNaturalist entries), crops and their diseases (agml_plant_health, plantvillage, plantdoc), weeds
(agml_weeds, the soybean, growth-stage and CropAndWeed entries), Pl@ntNet, plant seedlings, lawn and garden
chemicals (commons_household_chemicals, chemical_commons_sa) and the farm equipment packs.

Answers say only what the source says; plant problems end with PLANT_SAFETY (the packs' words). Every licence was
checked at its source in November 2026; nothing here is re-shared by the kit's makers.

Picture-making (GARDEN_PICTURE_MAKING_OK): the Commons garden packs and the share-alike entry may be used (gardens,
plants and tools; people are not their subject); the Open Images photos may not (people garden in many of them).

    python -c "import sources, garden_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

PLANT_SAFETY = ("A picture alone cannot confirm a plant problem; your local cooperative extension office can "
                "identify it.")
COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"

# The main categories of packs/garden_packs.py (category, question, answer, also its subcategories).
GARDEN_SA = [
    ("Vegetable gardens", "What kind of garden or place is this?", "This is a vegetable garden.", True),
    ("Herb gardens", "What kind of garden or place is this?", "This is a herb garden.", True),
    ("Allotments", "What kind of garden or place is this?", "This is an allotment, a rented plot for growing food.",
     True),
    ("Houseplants", "What is this?", "This is a houseplant, a plant grown indoors.", True),
    ("Seedlings", "What is this?", "This is seedlings: young plants just grown from seed.", True),
    ("Compost bins", "What is this?", "This is a compost bin, where kitchen and garden waste rots down into compost.",
     True),
    ("Seed packets", "What is this?", "This is a seed packet: the plant's name, sowing depth and spacing, days to "
                                      "harvest and when to sow are usually printed on it.", True),
    ("Plant labels", "What is this?", "This is a plant label (plant tag): it usually gives the plant's name, how much "
                                      "sun it needs, its spacing and how tall it grows.", True),
    ("Pruning", "What is happening in this picture?", "This is pruning: cutting back branches to keep a plant healthy "
                                                      "and in shape.", True),
    ("Lawns", "What kind of garden or place is this?", "This is a lawn.", True),
    ("Powdery mildew", "What is wrong with this plant?", "This plant shows powdery mildew: a white, powdery fungal "
                                                         "coating on the leaves. " + PLANT_SAFETY, True),
    ("Chlorosis", "What is wrong with this plant?", "This plant shows chlorosis: the leaves turn pale yellow while the "
                                                    "veins may stay green, often from a lack of iron or nitrogen or "
                                                    "from poor roots. " + PLANT_SAFETY, True),
]


def prepare_garden_commons_sa(source, data_dir, work, cap):
    """Commons garden, lawn and plant-problem categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(GARDEN_SA, cap, source.test, "garden-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


GARDEN_SOURCES = [
    Source("commons_garden_growing", "Gardens and growing: vegetable, herb, kitchen, community and flower gardens, "
                                     "allotments, fruit and apple trees, houseplants and potted plants, seedlings, "
                                     "planting, cold frames, cloches and trellises (Wikimedia Commons, ready-made "
                                     "pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1600, 20, prepare_pack, "about 350 MB"),
    Source("commons_garden_care", "Garden care: compost and worm bins, soil testing, seed packets and plant labels "
                                  "(the plant named only from the file's own words), pruning, loppers and grafting "
                                  "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack, "about 260 MB"),
    Source("commons_lawn_care", "Lawns, mowing, sod, the common lawn grasses by name (Kentucky bluegrass, perennial "
                                "ryegrass, zoysia, St. Augustine) and crabgrass (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 170 MB"),
    Source("commons_plant_problems", "Leaf symptoms: chlorosis, powdery mildew, leaf spot, late blight and sooty "
                                     "mould, with what each looks like (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 250, 5, prepare_pack, "about 50 MB"),
    Source("open_images_garden", "Gardens, lawns, compost, mulch and soil, seedlings, greenhouses, herbs, garden "
                                 "flowers, hedges, succulents and bonsai, pruning shears, weeds and dandelions, "
                                 "plant disease (Open Images, ready-made pack)",
           OI_OPEN, OI_CREDIT, "permissive", 3000, 30, prepare_pack, "about 600 MB"),
    Source("garden_commons_sa", "Wikimedia Commons: vegetable and herb gardens, allotments, houseplants, seedlings, "
                                "compost bins, seed packets, plant labels, pruning, lawns, powdery mildew and "
                                "chlorosis, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 1200, 12, prepare_garden_commons_sa, "about 260 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]

GARDEN_PICTURE_MAKING_OK = {"commons_garden_growing", "commons_garden_care", "commons_lawn_care",
                            "commons_plant_problems", "garden_commons_sa"}

GARDEN_NOT_INCLUDED = {
    "USDA PLANTS Database images (plants.usda.gov)":
        "each image carries its own credit and copyright line (many are the photographers' or herbaria's, \"all "
        "rights reserved\" or \"used with permission\"), and no program-readable licence per image was found; not "
        "taken. Plants by species are already in the iNaturalist and GBIF entries.",
    "USDA ARS and NRCS image galleries":
        "ARS's gallery is already the usda_ars pack (land_industry_packs.py) and NRCS's field photos are "
        "farm_usda_nrcs (work_farm_mech_packs.py); not repeated.",
    "Cooperative Extension photos (university extension services)":
        "each university's copyright (\"All rights reserved\" on the sites checked, or AI readers shut out); their "
        "guides are linked from the reference library's garden collection.",
    "PlantVillage and PlantDoc":
        "already in the kit (plantvillage: share-alike; plantdoc: personal use); not repeated.",
    "Commons categories that do not exist or hold no files under the names tried (November 2026)":
        "Raised bed gardening, Raised beds, Container gardening, Compost heaps, Seed trays, Row covers, Tomato "
        "cages, Garden sprinklers, Lawn sprinklers, Soaker hoses, Rain barrels, Grass clippings, Lawn aeration, "
        "Turf, Lawn weeds, Crabgrass (Digitaria sanguinalis is used), Leaf chlorosis, Downy mildew, Late blight "
        "(Phytophthora infestans is used), Blossom end rot, Leaf scorch, Nutrient deficiencies in plants, Tomato "
        "plants, Dibbers, Hand cultivators, Gardening gloves, Potting soil, Garden soil, Soil pH, USDA plant "
        "hardiness zone maps; Espalier, Festuca arundinacea, Weeding, Weeds, Soil and Plant diseases are empty.",
    "Commons garden categories other packs already use":
        "Mulch, Secateurs, Hoes, Rakes, Spades, Wheelbarrows, Watering cans, Garden forks, Garden trowels, Garden "
        "hoses, Hydroponics, Lawn mowers and Gardening are other packs' (never asked twice).",
    "Open Images garden labels already asked elsewhere":
        "Houseplant, Flowerpot, Watering can, Garden hose, Rake, Shovel, Wheelbarrow, Gardening, Lawn mower, "
        "Vegetable and the vegetables and fruits by name are other packs'.",
    "Pinterest, YouTube gardening videos, Instructables, Reddit and garden forums":
        "not read (the owner's rule: their terms forbid scraping or the pictures are their users' own).",
}
