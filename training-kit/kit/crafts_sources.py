"""ARTS AND CRAFTS (not textiles) for the Picture Model Training Kit (the owner's request of 2026-11-22). Pottery and
ceramics, and jewellery making and beading, are collections of their own (POTTERY_KIT_KEYS, JEWELLERY_KIT_KEYS), as
the owner asked. This file lists:
  - the ready-made packs built in packs/crafts_packs.py (group "permissive"; the kit downloads them with
    prepare_pack): Commons pottery, jewellery and beading, paper crafts and calligraphy, candles and soap, glass and
    carving, art supplies, models and resin; the Cleveland Museum of Art and Art Institute of Chicago ceramics,
    jewellery and glass records (CC0); Open Images crafts;
  - the share-alike Commons files of the main pottery, jewellery and craft categories (group "share-alike");
  - what was looked at and left out (CRAFTS_NOT_INCLUDED) and the sign-up and research collections
    (CRAFTS_SIGN_UP).

Nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the user's own computer,
only when the user ticks its choice. Answers say only what the Commons category, the file's own words, the museum's
record or the Open Images labels say. Safety notes (kilns, clay dust, lye, wax, glass and lead, torches, resin,
blades, pigments) are the packs' own words. Records and files that name a nude are left out.

Picture-making (CRAFTS_PICTURE_MAKING_OK): the museum objects and the Commons art supplies, paper crafts and models
(things, not people) may be used; sources.py puts every other key in NOT_FOR_PICTURE_MAKING.

    python -c "import sources, crafts_sources"      (from the kit folder: checks the file loads)
"""

import os

from home_sources import commons_sa_items
from more_sources import fetch_shared
from sources import Source, prepare_pack

COMMONS_OPEN = "Pictures CC0, public domain or CC BY (credited in CREDITS.txt); captions CC0"
COMMONS_CREDIT = "Wikimedia Commons contributors (credited in CREDITS.txt), https://commons.wikimedia.org"
OI_OPEN = ("Labels CC BY 4.0 (Open Images V7); each photo CC BY, CC0 or Public Domain Mark (credited in "
           "CREDITS.txt)")
OI_CREDIT = ("Google Open Images V7 (labels CC BY 4.0) and the photographers credited in CREDITS.txt, "
             "https://storage.googleapis.com/openimages/web/index.html")
MUSEUM_OPEN = ("CC0 pictures and records (the Cleveland Museum of Art Open Access; the Art Institute of Chicago's "
               "public-domain works); Chicago's descriptions CC BY 4.0 where used (credited in CREDITS.txt)")
MUSEUM_CREDIT = ("The Cleveland Museum of Art (https://www.clevelandart.org, CC0) and the Art Institute of Chicago "
                 "(https://www.artic.edu, CC0 and CC BY 4.0), each object credited in CREDITS.txt")
SA_TERMS = "https://creativecommons.org/licenses/by-sa/4.0/"
SA_SUMMARY = "CC BY-SA (or GFDL): use with credit, and anything made from it keeps the same licence."
SA_LICENCE = "Each file CC BY-SA or GFDL (its Commons page); captions CC0"
SA_CREDIT = "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org"

KILN_NOTE = ("Safety: kilns get extremely hot and give off fumes while firing: keep one in a ventilated space away "
             "from anything that burns, and never open a hot kiln without heat-resistant gloves and eye protection.")
CLAY_NOTE = ("Safety: dry clay and glaze dust contains silica, which harms the lungs: clean up wet with a sponge or "
             "mop, never sweep, and wear a respirator when mixing dry materials.")
LYE_NOTE = ("Safety: soap making uses lye (sodium hydroxide), which burns skin and eyes: wear goggles and gloves, "
            "always add lye to water, never water to lye, work with ventilation, and keep it away from children and "
            "pets.")
TORCH_NOTE = ("Safety: torches, hot glass and hot metal burn: work on a fireproof surface with ventilation and eye "
              "protection made for the job.")
GLASS_NOTE = ("Safety: cut glass is sharp, and the lead came and solder of stained glass contain lead: wear eye "
              "protection, wash your hands, and do not eat or drink while working.")
BLADE_NOTE = ("Safety: carving tools and craft knives are very sharp: cut away from yourself and wear a "
              "cut-resistant glove on the hand that holds the work.")


def thing(category, words, note="", deeper=True):
    """(category, question, answer, deeper) for home_sources.commons_sa_items: "This is <words>." and the note."""
    return (category, "What is this?", f"This is {words}." + (f" {note}" if note else ""), deeper)


POTTERY_SA = [
    thing("Pottery wheels", "a potter's wheel, a spinning wheel on which clay is shaped by hand", CLAY_NOTE),
    thing("Throwing (pottery)", "throwing: shaping clay on a potter's wheel", CLAY_NOTE),
    thing("Kilns", "a kiln, the oven in which pottery is fired", KILN_NOTE, deeper=False),
    thing("Raku", "raku: pottery taken red-hot from the kiln and cooled in the open or in sawdust", KILN_NOTE),
    thing("Stoneware", "stoneware, pottery fired hot until it is hard and watertight", deeper=False),
    thing("Earthenware", "earthenware, pottery fired at a lower heat, porous unless glazed", deeper=False),
    thing("Ceramic glazes", "ceramic glaze, the glassy coating fired onto pottery", CLAY_NOTE),
]
JEWELLERY_SA = [
    thing("Jewellery making", "jewellery making", TORCH_NOTE),
    thing("Beadwork", "beadwork", deeper=False),
    thing("Glass beads", "glass beads"),
    thing("Wire wrapping", "wire-wrapped jewellery, made by winding wire round stones or beads"),
    thing("Cabochons", "a cabochon, a stone polished smooth and domed, not faceted"),
    thing("Lapidary", "lapidary work: cutting and polishing stones"),
]
CRAFTS_SA = [
    thing("Origami", "origami: paper folded into a shape without cuts or glue", deeper=False),
    thing("Bookbinding", "bookbinding", deeper=False),
    thing("Western calligraphy", "Western calligraphy, decorative handwriting with a broad pen"),
    thing("Soap making", "soap making", LYE_NOTE),
    thing("Stained glass making", "stained glass being made", GLASS_NOTE),
    thing("Glassblowing", "glassblowing: shaping molten glass by blowing through a pipe", TORCH_NOTE),
    thing("Whittling", "whittling: carving wood with a knife", BLADE_NOTE),
    thing("Easels", "an easel, a stand that holds a painting or drawing"),
    thing("Plastic model kits", "a plastic model kit"),
]


def prepare_pottery_commons_sa(source, data_dir, work, cap):
    """Commons pottery, kiln and glaze categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(POTTERY_SA, cap, source.test, "pottery-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_jewellery_commons_sa(source, data_dir, work, cap):
    """Commons jewellery making, bead and lapidary categories, files under CC BY-SA or GFDL."""
    items = commons_sa_items(JEWELLERY_SA, cap, source.test, "jewellery-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


def prepare_crafts_commons_sa(source, data_dir, work, cap):
    """Commons paper craft, calligraphy, soap, glass, carving, art supply and model categories, files under CC BY-SA
    or GFDL."""
    items = commons_sa_items(CRAFTS_SA, cap, source.test, "crafts-sa")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


CRAFTS_SOURCES = [
    Source("commons_pottery_ceramics", "Pottery and ceramics: potter's wheels and throwing, kilns, raku, glazes, "
                                       "stoneware, earthenware, slip casting, hand-building, tools and clay, with "
                                       "kiln and clay-dust notes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 320 MB"),
    Source("museum_ceramics", "Ceramics in museums: pottery, stoneware, porcelain and earthenware with the museum's "
                              "own description (Cleveland Museum of Art and Art Institute of Chicago, ready-made "
                              "pack)", MUSEUM_OPEN, MUSEUM_CREDIT, "permissive", 2000, 20, prepare_pack,
           "about 400 MB"),
    Source("commons_jewellery_beading", "Jewellery making and beading: workshops, goldsmiths and silversmiths, beads, "
                                        "findings, wire wrapping, lost-wax casting, cabochons and gem cutting, "
                                        "jewellers' tools, enamelling (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1500, 15, prepare_pack, "about 320 MB"),
    Source("museum_jewellery", "Jewellery, enamels and beads in museums, with the museum's own description "
                               "(Cleveland Museum of Art and Art Institute of Chicago, ready-made pack)",
           MUSEUM_OPEN, MUSEUM_CREDIT, "permissive", 1200, 15, prepare_pack, "about 240 MB"),
    Source("commons_paper_crafts", "Paper crafts and calligraphy: origami, kirigami, paper models, quilling, "
                                   "papier-mache, scrapbooking, cards, bookbinding, marbling, papermaking, "
                                   "calligraphy, dip pens, block printing and linocut (Wikimedia Commons, ready-made "
                                   "pack)", COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1800, 20, prepare_pack,
           "about 380 MB"),
    Source("commons_candle_soap", "Candle and soap making, with the lye and hot-wax safety notes (Wikimedia Commons, "
                                  "ready-made pack)", COMMONS_OPEN, COMMONS_CREDIT, "permissive", 400, 10,
           prepare_pack, "about 90 MB"),
    Source("commons_glass_carving", "Stained glass, fused glass, glassblowing, lampworking and mosaics; woodcarving, "
                                    "whittling, chip and relief carving, pyrography (Wikimedia Commons, ready-made "
                                    "pack)", COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1200, 15, prepare_pack,
           "about 260 MB"),
    Source("commons_art_supplies", "Painting and drawing supplies: palettes, easels, watercolour, oil and acrylic "
                                   "paints, palette knives, coloured pencils, pastels, charcoal, sketchbooks and "
                                   "brushes (Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 1000, 10, prepare_pack, "about 210 MB"),
    Source("commons_models_resin", "Scale models, model kits, dioramas, model railways, miniatures and resin casting "
                                   "(Wikimedia Commons, ready-made pack)",
           COMMONS_OPEN, COMMONS_CREDIT, "permissive", 800, 10, prepare_pack, "about 170 MB"),
    Source("museum_glass_crafts", "Glass, lacquer, calligraphy and bookbinding in museums, with the museum's own "
                                  "description (Cleveland Museum of Art and Art Institute of Chicago, ready-made "
                                  "pack)", MUSEUM_OPEN, MUSEUM_CREDIT, "permissive", 1000, 10, prepare_pack,
           "about 200 MB"),
    Source("open_images_crafts", "Pottery, beads, earrings, pendants and gemstones, origami and calligraphy, paints, "
                                 "palettes and sketches, sculpture, stained glass and mosaics (Open Images, "
                                 "ready-made pack)", OI_OPEN, OI_CREDIT, "permissive", 2500, 25, prepare_pack,
           "about 500 MB"),
    Source("pottery_commons_sa", "Wikimedia Commons: potter's wheels, throwing, kilns, raku, stoneware, earthenware "
                                 "and glazes, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 600, 10, prepare_pottery_commons_sa, "about 130 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("jewellery_commons_sa", "Wikimedia Commons: jewellery making, beadwork, glass beads, wire wrapping, "
                                   "cabochons and lapidary work, files under CC BY-SA or GFDL (share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 500, 10, prepare_jewellery_commons_sa, "about 110 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
    Source("crafts_commons_sa", "Wikimedia Commons: origami, bookbinding, calligraphy, soap making, stained glass, "
                                "glassblowing, whittling, easels and model kits, files under CC BY-SA or GFDL "
                                "(share-alike)",
           SA_LICENCE, SA_CREDIT, "share-alike", 800, 10, prepare_crafts_commons_sa, "about 170 MB of pictures",
           terms=SA_TERMS, terms_summary=SA_SUMMARY),
]
CRAFTS_PACK_KEYS = ("commons_pottery_ceramics", "museum_ceramics", "commons_jewellery_beading", "museum_jewellery",
                    "commons_paper_crafts", "commons_candle_soap", "commons_glass_carving", "commons_art_supplies",
                    "commons_models_resin", "museum_glass_crafts", "open_images_crafts")
# The two collections the owner asked for by name.
POTTERY_KIT_KEYS = ("commons_pottery_ceramics", "museum_ceramics", "pottery_commons_sa")
JEWELLERY_KIT_KEYS = ("commons_jewellery_beading", "museum_jewellery", "jewellery_commons_sa")
# Things, not people: museum objects, art supplies, paper crafts and models.
CRAFTS_PICTURE_MAKING_OK = {"museum_ceramics", "museum_jewellery", "museum_glass_crafts", "commons_art_supplies",
                            "commons_paper_crafts", "commons_models_resin"}

CRAFTS_SIGN_UP = {
    "Smithsonian Cooper Hewitt collection pictures":
        "its API needs a key, and its pictures are not in the Smithsonian open-access bucket (hardware_sources.py); "
        "the records are CC0 but each picture's rights are its own. Recorded only.",
    "Europeana craft records (English, open rights)":
        "Europeana's open API with the public test key (as drinks_packs uses) could add historic pottery and "
        "jewellery; not built in this first version.",
    "Kaggle and Hugging Face pottery, jewellery and origami sets":
        "most need an account and give no licence or a non-commercial one, with photos scraped from shops; the "
        "owner can use the own-pictures folder for personal use.",
}

CRAFTS_NOT_INCLUDED = {
    "The Metropolitan Museum of Art's ceramics and jewellery (CC0)":
        "already reachable through the kit's met and met_collection entries (every department); not repeated.",
    "Ravelry, Etsy, Pinterest, Instructables and YouTube":
        "their terms forbid copying their pictures by program; not read.",
    "Commons nudes in craft categories and museum nudes":
        "files and records whose words name a nude are left out (the nudity packs have the fine-art nudes).",
    "Open Images craft labels with no checked photos (November 2026)":
        "Airbrush, Palette knife, Resin, Toy craft kit: no human-checked labels; left out. Labels already asked "
        "elsewhere (Pottery, Vase, Jewellery, Necklace, Bracelet, Ring, Candle, Soap, Drawing, Pencil, Crayon, Pen, "
        "Paper, Book, Toy) are never asked twice.",
    "Textile crafts (sewing, knitting, crochet, quilting, embroidery, weaving, macrame, spinning, dyeing, "
    "upholstery, leatherwork) and furniture refinishing":
        "another collection's (the home repair and textile crafts packs); not here.",
}
