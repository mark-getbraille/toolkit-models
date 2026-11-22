"""Picture packs for ARTS AND CRAFTS other than textiles: pottery and ceramics, jewellery making and beading (the
owner asked for these two as collections of their own, so each has its own Commons and museum packs), paper crafts
(origami, kirigami, paper models, quilling, papier-mache, scrapbooking, card making, bookbinding, marbling,
papermaking), calligraphy, candle and soap making, glass (stained glass, fusing, glassblowing, lampworking) and
mosaics, woodcarving and whittling, painting and drawing supplies, model making, miniatures and resin. Used by
build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row)
rows naming the same picture. The limit counts pictures.

The owner's request of 2026-11-22 (with packs/electronics_packs.py and packs/building_packs.py; the Commons builder,
build_commons_facts, is electronics_packs'). Textile crafts (sewing, knitting, crochet, quilting, embroidery,
weaving, macrame, spinning and dyeing, upholstery, leatherwork) and furniture refinishing are another collection's.

WHAT THE ANSWERS SAY. A fixed sentence from the Commons category a file sits in ("It shows a kiln, the oven in which
pottery is fired."), with the file's own description; the museum packs give the museum's own record (title, maker,
date, materials, its description) as museum_rows writes it. Nothing is guessed from the picture: no glaze, metal,
stone or value is named unless the source names it. Files and records whose words name a nude are left out (the
museum crafts searches can turn up fine-art nudes; the nudity packs have those), and the safety rules of
gaps_collection_packs.marked_rows apply. Safety notes, in the drinks distilling warning's style:
  KILN_NOTE    kilns and firing (heat, fumes, ventilation, never open hot);
  CLAY_NOTE    dry clay and glaze dust (silica; wet-clean, never sweep);
  LYE_NOTE     soap making (lye burns: goggles and gloves, lye into water never water into lye, children and pets);
  WAX_NOTE     candle making (hot wax burns and catches fire: double boiler, never unattended);
  GLASS_NOTE   stained glass and glass cutting (sharp edges, lead came and solder: wash hands, no food);
  TORCH_NOTE   glassblowing, lampworking and jewellery soldering (flame, hot glass and metal, ventilation);
  RESIN_NOTE   epoxy and casting resins (skin and lungs: gloves, ventilation, the label);
  BLADE_NOTE   carving tools and craft knives (cut away from yourself, a cut-resistant glove);
  PIGMENT_NOTE some artists' paints and pastels contain toxic pigments (cadmium, cobalt, lead): read the label.

The packs (CRAFTS_PACKS):
  commons_pottery_ceramics     potter's wheels, potters at work and wheel-thrown pottery, kilns (pottery kilns and
                               the anagama), raku, stoneware, earthenware, terracotta, crystalline and tin glazes,
                               sgraffito, modelling and polymer clay.
  museum_ceramics              the Cleveland Museum of Art (type Ceramic) and the Art Institute of Chicago (ceramics,
                               stoneware, porcelain, earthenware) open-access records, CC0, with the museum's own words.
  commons_jewellery_beading    jewellery making, goldsmiths, silversmiths and jewellers at work, beadwork, seed,
                               glass and wooden beads, jump rings and clasps, wire wrapping, lost-wax casting,
                               cabochons, gem cutting and lapidary, jewellers' tools, enamelling and cloisonne,
                               chainmail jewellery.
  museum_jewellery             Cleveland (type Jewelry and Enamel) and Chicago (jewelry, enamel, bead) records, CC0.
  commons_paper_crafts         origami (modular, birds), kirigami, paper models and papercraft, paper cutting,
                               quilling, papier-mache, scrapbooking, greeting cards, bookbinding and its tools,
                               Coptic binding, marbled paper, papermaking and handmade paper, calligraphy and
                               calligraphers, dip pens, pen nibs, brush pens and inkwells, block printing, linocut,
                               rubber stamps, decoupage.
  commons_candle_soap          beeswax candles and candle wicks (WAX_NOTE) and Aleppo soap (finished soap: no lye
                               note); Commons has no category for candle or soap making (checked 2026-11-22), so
                               LYE_NOTE is kept for the kit and the books on soap making.
  commons_glass_carving        a stained-glass window being made, fused glass, glassblowing and glassblowers,
                               lampworking, glass art, mosaic making; woodcarving and woodcarvers, whittling, chip
                               and relief carving, carving tools, pyrography.
  commons_art_supplies         painting tools, painting palettes, easels, watercolour, oil and acrylic paint,
                               gouache, coloured pencils, pastels, sketchbooks, drawing tools, art materials,
                               painters at work.
  commons_models_resin         scale models, plastic models, dioramas, model railways and aircraft, resin casting.
  museum_glass_crafts          Cleveland (type Glass, Lacquer, Calligraphy) and Chicago (glass, book) records, CC0.
  open_images_crafts           Open Images labels no other pack asks about: pottery and ceramics (ceramic, clay,
                               earthenware, porcelain, potter's wheel), jewellery and stones (bead, earring, pendant,
                               brooch, gemstone, diamond, gold, silver, jewellery making), paper crafts (origami,
                               scrapbooking, calligraphy, tissue paper), painting and drawing (paint, painting,
                               palette, sketch, pastel, watercolour, fountain pen, marker pen, compass), sculpture,
                               stained glass and mosaic.

Not repeated here: home_packs (rings, earrings, jewellery, candles), things_packs (candles, vases, kitchen clay pots),
hardware_packs (paintbrushes, soldering, carving chisels, jewellers' bench tools as hardware), culture_packs (beads in
culture), people_activity_packs (people making pottery), gaps_collection_packs' aic_collection and
cleveland_collection (the museums' every department, a few from each; the craft packs here take only the craft
types, so a picture is seldom in both) and the kit's art_institute collection (Chicago works with the museum's own
alt text: aic_item leaves those to it). What was looked at and left out is in the kit's crafts_sources.py.

    python packs/crafts_packs.py commons_pottery_ceramics --limit 8      (prints a few rows: a quick check)
"""

import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, say, pass_random
from gaps_oi_packs import group, build_oi_gap, QUICK
from electronics_packs import build_commons_facts

WHAT_Q = "What is this?"

KILN_NOTE = ("Safety: kilns get extremely hot and give off fumes while firing: keep one in a ventilated space away "
             "from anything that burns, and never open a hot kiln without heat-resistant gloves and eye protection.")
CLAY_NOTE = ("Safety: dry clay and glaze dust contains silica, which harms the lungs: clean up wet with a sponge or "
             "mop, never sweep, and wear a respirator when mixing dry materials.")
LYE_NOTE = ("Safety: soap making uses lye (sodium hydroxide), which burns skin and eyes: wear goggles and gloves, "
            "always add lye to water, never water to lye, work with ventilation, and keep it away from children and "
            "pets.")
WAX_NOTE = ("Safety: hot wax burns and can catch fire: melt it in a double boiler, never over a direct flame, and "
            "never leave it unattended.")
GLASS_NOTE = ("Safety: cut glass is sharp, and the lead came and solder of stained glass contain lead: wear eye "
              "protection, wash your hands, and do not eat or drink while working.")
TORCH_NOTE = ("Safety: torches, hot glass and hot metal burn: work on a fireproof surface with ventilation and eye "
              "protection made for the job.")
RESIN_NOTE = ("Safety: epoxy and other casting resins can irritate skin and lungs: wear nitrile gloves, work with "
              "ventilation, and follow the label.")
BLADE_NOTE = ("Safety: carving tools and craft knives are very sharp: cut away from yourself and wear a "
              "cut-resistant glove on the hand that holds the work.")
PIGMENT_NOTE = ("Some artists' paints and pastels contain toxic pigments (such as cadmium, cobalt or lead): read the "
                "label, and do not eat or drink while working.")


def thing(category, words, note="", deeper=True):
    """A Commons spec: "What is this?" -> "It shows <words>." and the note after."""
    return (category, deeper, [(WHAT_Q, f"It shows {words}." + (f" {note}" if note else ""))])


# ----------------------------------------------------------------- Commons: pottery and ceramics

POTTERY = [
    thing("Pottery wheels", "a potter's wheel, a spinning wheel on which clay is shaped by hand", CLAY_NOTE),
    thing("Kilns", "a kiln, the oven in which pottery is fired", KILN_NOTE, deeper=False),
    thing("Pottery kilns", "a pottery kiln", KILN_NOTE),
    thing("Raku", "raku: pottery taken red-hot from the kiln and cooled in the open or in sawdust", KILN_NOTE),
    thing("Stoneware", "stoneware, pottery fired hot until it is hard and watertight", deeper=False),
    thing("Earthenware", "earthenware, pottery fired at a lower heat, porous unless glazed", deeper=False),
    thing("Terracotta", "terracotta, reddish-brown unglazed earthenware", deeper=False),
    thing("Modelling clay", "modelling clay"),
    thing("Polymer clay", "polymer clay, a coloured clay hardened in a home oven"),
    thing("Sgraffito", "sgraffito: a design scratched through a coloured layer of clay or glaze"),
    thing("Potters", "a potter at work", CLAY_NOTE, deeper=False),
    thing("Wheel-thrown pottery", "wheel-thrown pottery, shaped on a potter's wheel"),
    thing("Crystalline glaze", "a crystalline glaze, in which crystals grow in the glaze as the kiln cools"),
    thing("Tin-glazing", "tin-glazed pottery, with an opaque white glaze painted in colours"),
    thing("Anagama kiln", "an anagama, a long wood-fired tunnel kiln built up a slope", KILN_NOTE),
]

# ----------------------------------------------------------------- Commons: jewellery making and beading

JEWELLERY = [
    thing("Jewellery making", "jewellery making", TORCH_NOTE),
    thing("Silversmiths", "a silversmith at work", TORCH_NOTE),
    thing("Silversmithing", "silversmithing", TORCH_NOTE),
    thing("Beadwork", "beadwork", deeper=False),
    thing("Seed beads", "seed beads, tiny glass beads"),
    thing("Glass beads", "glass beads"),
    thing("Wooden beads", "wooden beads"),
    thing("Jump rings", "jump rings, small split metal rings that join jewellery parts"),
    thing("Clasps", "a clasp, which fastens a necklace or bracelet"),
    thing("Wire wrapping", "wire-wrapped jewellery, made by winding wire round stones or beads"),
    thing("Lost-wax casting", "lost-wax casting: a wax model is covered in plaster, melted out and replaced with "
                              "metal", TORCH_NOTE),
    thing("Cabochons", "a cabochon, a stone polished smooth and domed, not faceted"),
    thing("Gem cutting", "gem cutting (faceting)"),
    thing("Lapidary", "lapidary work: cutting and polishing stones"),
    thing("Enamelling", "enamelling: powdered glass fused onto metal", TORCH_NOTE),
    thing("Cloisonné", "cloisonne: enamel set between thin wire walls on metal"),
    thing("Chainmail jewellery", "chainmail jewellery, made of linked metal rings"),
    thing("Goldsmiths", "a goldsmith at work", TORCH_NOTE, deeper=False),
    thing("Jewellers", "a jeweller at work", TORCH_NOTE, deeper=False),
    thing("Jewellery tools", "jewellers' tools"),
]

# ----------------------------------------------------------------- Commons: paper crafts and calligraphy

PAPER = [
    thing("Origami", "origami: paper folded into a shape without cuts or glue", deeper=False),
    thing("Modular origami", "modular origami, many folded units fitted together"),
    thing("Kirigami", "kirigami: paper folded and cut"),
    thing("Paper models", "a paper model"),
    thing("Papercraft", "papercraft"),
    thing("Paper cutting", "paper cutting, a picture cut from paper", BLADE_NOTE),
    thing("Quilling", "quilling: strips of paper rolled and shaped into designs"),
    thing("Papier-mâché", "papier-mache: paper and paste moulded and dried hard"),
    thing("Scrapbooking", "scrapbooking: photos and keepsakes arranged on decorated pages"),
    thing("Bookbinding", "bookbinding", deeper=False),
    thing("Bookbinding tools", "bookbinding tools (bone folder, awl, needle, thread, press)"),
    thing("Coptic binding", "Coptic binding, with the sewing showing on an open spine"),
    thing("Marbled paper", "marbled paper, patterned by floating colours on liquid"),
    thing("Papermaking", "papermaking by hand"),
    thing("Handmade paper", "handmade paper"),
    thing("Western calligraphy", "Western calligraphy, decorative handwriting with a broad pen"),
    thing("Calligraphy tools", "calligraphy tools"),
    thing("Calligraphers", "a calligrapher at work"),
    thing("Dip pens", "a dip pen, a nib on a holder dipped in ink"),
    thing("Brush pens", "a brush pen"),
    thing("Inkwells", "an inkwell"),
    thing("Block printing", "block printing: a carved block inked and pressed onto paper or cloth"),
    thing("Linocut", "a linocut, a print from a carved block of linoleum", BLADE_NOTE),
    thing("Rubber stamps", "rubber stamps"),
    thing("Decoupage", "decoupage: paper cut-outs glued on and varnished"),
    thing("Origami birds", "an origami bird"),
    thing("Greeting cards", "a greeting card"),
    thing("Pen nibs", "pen nibs, the metal points of dip pens"),
]

# ----------------------------------------------------------------- Commons: candles and soap

CANDLE_SOAP = [
    thing("Beeswax candles", "beeswax candles"),
    thing("Candle wicks", "candle wicks", WAX_NOTE),
    thing("Aleppo soap", "Aleppo soap, a traditional soap made from olive and laurel oils"),
]

# ----------------------------------------------------------------- Commons: glass, mosaics and carving

GLASS_CARVING = [
    thing("Fused glass", "fused glass: pieces of glass melted together in a kiln", KILN_NOTE),
    thing("Glassblowing", "glassblowing: shaping molten glass by blowing through a pipe", TORCH_NOTE),
    thing("Glassblowers", "a glassblower at work", TORCH_NOTE),
    thing("Lampworking", "lampworking: shaping glass rods in a torch flame, often to make beads", TORCH_NOTE),
    thing("Glass art", "glass art", deeper=False),
    thing("Mosaic making", "a mosaic being made from small pieces of tile or glass", GLASS_NOTE),
    thing("Woodcarving", "woodcarving", BLADE_NOTE, deeper=False),
    thing("Whittling", "whittling: carving wood with a knife", BLADE_NOTE),
    thing("Chip carving", "chip carving: patterns cut by removing small chips of wood", BLADE_NOTE),
    thing("Relief carving", "relief carving: a picture carved so it stands out from a flat background", BLADE_NOTE),
    thing("Wood carving tools", "wood carving tools (gouges, chisels and knives)", BLADE_NOTE),
    thing("Pyrography", "pyrography: designs burned into wood with a hot tool", "Safety: the tip is hot enough to "
          "burn; work with ventilation."),
    thing("Making a stained-glass window", "a stained-glass window being made", GLASS_NOTE),
    thing("Woodcarvers", "a wood carver at work", BLADE_NOTE),
]

# ----------------------------------------------------------------- Commons: painting and drawing supplies

ART_SUPPLIES = [
    thing("Painting tools", "painting tools"),
    thing("Easels", "an easel, a stand that holds a painting or drawing"),
    thing("Gouache", "gouache, an opaque watercolour"),
    thing("Colored pencils", "coloured pencils"),
    thing("Pastels", "pastels, sticks of pigment", PIGMENT_NOTE, deeper=False),
    thing("Sketchbooks", "a sketchbook"),
    thing("Drawing tools", "drawing tools"),
    thing("Art materials", "art materials", deeper=False),
    thing("Painters at work", "a painter at work", deeper=False),
    thing("Watercolor paint", "watercolour paint"),
    thing("Oil paint", "oil paint", PIGMENT_NOTE),
    thing("Acrylic paint", "acrylic paint"),
    thing("Painting palettes", "an artist's palette, for mixing paint"),
]

# ----------------------------------------------------------------- Commons: models, miniatures and resin

MODELS_RESIN = [
    thing("Scale models", "a scale model, a small copy of a real thing", deeper=False),
    thing("Dioramas", "a diorama, a small scene built as a model"),
    thing("Model railways", "a model railway", deeper=False),
    thing("Model aircraft", "a model aircraft", deeper=False),
    thing("Resin casting", "resin casting: liquid resin poured into a mould", RESIN_NOTE),
    thing("Plastic models", "a plastic model kit or a model built from one"),
]


def build_commons_pottery_ceramics(limit):
    """The commons_pottery_ceramics pack (see the module docstring)."""
    return build_commons_facts(POTTERY, limit, "pottery")


def build_commons_jewellery_beading(limit):
    """The commons_jewellery_beading pack (see the module docstring)."""
    return build_commons_facts(JEWELLERY, limit, "jewelmake")


def build_commons_paper_crafts(limit):
    """The commons_paper_crafts pack (see the module docstring)."""
    return build_commons_facts(PAPER, limit, "papercraft")


def build_commons_candle_soap(limit):
    """The commons_candle_soap pack (see the module docstring)."""
    return build_commons_facts(CANDLE_SOAP, limit, "candlesoap")


def build_commons_glass_carving(limit):
    """The commons_glass_carving pack (see the module docstring)."""
    return build_commons_facts(GLASS_CARVING, limit, "glasscarve")


def build_commons_art_supplies(limit):
    """The commons_art_supplies pack (see the module docstring)."""
    return build_commons_facts(ART_SUPPLIES, limit, "artsupply")


def build_commons_models_resin(limit):
    """The commons_models_resin pack (see the module docstring)."""
    return build_commons_facts(MODELS_RESIN, limit, "modelresin")


# ----------------------------------------------------------------- museums: Cleveland and Chicago craft records

MUSEUM_SETS = {
    "museum_ceramics": (("Ceramic",), ("ceramics", "stoneware", "porcelain", "earthenware"), "museumpottery"),
    "museum_jewellery": (("Jewelry", "Enamel"), ("jewelry", "enamel", "bead"), "museumjewel"),
    "museum_glass_crafts": (("Glass", "Lacquer", "Calligraphy"), ("glass", "book"), "museumglass"),
}


def renamed(item, prefix):
    """A museum item (name, picture address, rows, ...) under this pack's own file prefix (so it is not mistaken for
    the same object in aic_collection or cleveland_collection)."""
    name = item[0]
    return (f"{prefix}-{name.split('-', 1)[1]}",) + tuple(item[1:])


def cma_craft_items(types, prefix, want, s=None):
    """(name, picture address, rows) for Cleveland CC0 records of these object types, the same number from each,
    from random places in each type's list; only records whose words describe the object (gaps_collection_packs.
    cma_item: not CC0, no picture or a nude are left out)."""
    from gaps_collection_packs import CMA, cma_item
    from museum_general_packs import get_json
    s = s or session()
    rng = pass_random(prefix + "-cma")
    per = max(2, want // max(1, len(types)) + 1)
    items = []
    for kind in types:
        first = get_json(s, CMA, params={"cc0": 1, "has_image": 1, "limit": 1, "type": kind}) or {}
        total = (first.get("info") or {}).get("total") or 0
        starts = list(range(0, max(1, total), 100))
        rng.shuffle(starts)
        found = 0
        for skip in starts[:30]:
            if found >= per or build_packs.listing_out_of_time():
                break
            time.sleep(1)
            data = get_json(s, CMA, params={"cc0": 1, "has_image": 1, "limit": 100, "skip": skip, "type": kind}) or {}
            for a in data.get("data") or []:
                got = cma_item(a)
                if got and got[3] and found < per:
                    name, picture, rows, _described = renamed(got, prefix)
                    items.append((name, picture, rows))
                    found += 1
        say(f"  Cleveland {kind}: {found} usable of {total}")
    return items


def aic_craft_items(classes, prefix, want, s=None):
    """(name, picture address, rows) for Art Institute of Chicago public-domain records of these classifications,
    from random result pages (the search gives at most 1,000 results a query); gaps_collection_packs.aic_item leaves
    out works with the museum's own alt text (the kit's art_institute collection has those) and nudes."""
    from gaps_collection_packs import AIC_FIELDS, aic_post, aic_item
    s = s or session()
    s.headers["AIC-User-Agent"] = s.headers["User-Agent"]
    rng = pass_random(prefix + "-aic")
    per = max(2, want // max(1, len(classes)) + 1)
    items = []
    for kind in classes:
        base = [{"term": {"is_public_domain": True}}, {"term": {"classification_titles.keyword": kind}},
                {"exists": {"field": "image_id"}}]
        pages = list(range(1, 11))
        rng.shuffle(pages)
        found = 0
        for page in pages:
            if found >= per or build_packs.listing_out_of_time():
                break
            data = aic_post(s, {"query": {"bool": {"filter": base}}, "fields": AIC_FIELDS, "limit": 100,
                                "page": page})
            for a in data.get("data") or []:
                got = aic_item(a)
                if got and got[3] and found < per:
                    name, picture, rows, _described = renamed(got, prefix)
                    items.append((name, picture, rows))
                    found += 1
        say(f"  Art Institute of Chicago {kind}: {found} usable")
    return items


def build_museum_crafts(key, limit):
    """One museum craft pack (MUSEUM_SETS): half from Cleveland, half from Chicago, the pictures fetched (Chicago's
    with the header its picture server asks for)."""
    from food_packs import with_twins
    from gaps_collection_packs import shared_finish, aic_fetch
    types, classes, prefix = MUSEUM_SETS[key]
    half = int(limit * 0.6) + 2
    cleveland = shared_finish(key, cma_craft_items(types, prefix, half), limit // 2 + 1, workers=3, pause=0.3)
    got = sum(1 for _, data, _ in cleveland if data)
    chicago = aic_craft_items(classes, prefix, half)
    pass_random(prefix + "-order").shuffle(chicago)
    fetched = aic_fetch(chicago[:int((limit - got) * 1.2) + 2])[:max(0, limit - got)]
    return cleveland + with_twins(fetched)


def build_museum_ceramics(limit):
    """The museum_ceramics pack (see the module docstring)."""
    return build_museum_crafts("museum_ceramics", limit)


def build_museum_jewellery(limit):
    """The museum_jewellery pack (see the module docstring)."""
    return build_museum_crafts("museum_jewellery", limit)


def build_museum_glass_crafts(limit):
    """The museum_glass_crafts pack (see the module docstring)."""
    return build_museum_crafts("museum_glass_crafts", limit)


# ----------------------------------------------------------------- Open Images

CRAFTS_OI = [
    group("What pottery or ceramics are in this picture?",
          {"Ceramic": "ceramics", "Clay": "clay", "Earthenware": "earthenware", "Porcelain": "porcelain",
           "Blue and white porcelain": "blue and white porcelain", "Potter's wheel": "a potter's wheel"}),
    group("What jewellery or stones are in this picture?",
          {"Bead": "beads", "Earring": "an earring", "Pendant": "a pendant", "Brooch": "a brooch",
           "Gemstone": "a gemstone", "Diamond (Gemstone)": "a diamond", "Gold": "gold", "Silver": "silver",
           "Jewelry making": "jewellery being made", "Body jewelry": "body jewellery"}),
    group("What paper crafts are in this picture?",
          {"Origami": "origami", "Origami paper": "origami paper", "Scrapbooking": "scrapbooking",
           "Calligraphy": "calligraphy", "Tissue paper": "tissue paper", "Art paper": "art paper",
           "Rice paper": "rice paper", "Construction paper": "construction paper", "Craft": "a craft",
           }),
    group("What paints are in this picture?",
          {"Paint": "paint", "Watercolor paint": "watercolour paint", "Acrylic paint": "acrylic paint",
           "Pastel (Art)": "pastels", "Palette": "a palette"}, PIGMENT_NOTE),
    group("What drawing or writing things are in this picture?",
          {"Sketch": "a sketch", "Sketch pad": "a sketch pad", "Fountain pen": "a fountain pen",
           "Marker pen": "a marker pen", "Compass (Drawing Instrument)": "a drawing compass", "Easel": "an easel",
           "Canvas": "a canvas"}),
    group("What other crafts are in this picture?",
          {"Painting": "a painting", "Sculpture": "a sculpture", "Stained glass": "stained glass", "Mosaic": "a mosaic",
           "Stone carving": "stone carving", "Chainsaw carving": "chainsaw carving", "Scale model": "a scale model",
           "Model car": "a model car", "Model aircraft": "a model aircraft",            "Wood stain": "wood stain"}),
]


def build_open_images_crafts(limit):
    """open_images_crafts (see the module docstring)."""
    return build_oi_gap("open_images_crafts", CRAFTS_OI, limit, 9303)


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
OI_LICENCE = ("Google Open Images V7 (https://storage.googleapis.com/openimages/web/index.html): labels CC BY 4.0; "
              "each photo under its own licence (CC BY, CC0 or the Public Domain Mark, checked photo by photo), "
              "photographer credited below.")
MUSEUM_LICENCE = ("The Cleveland Museum of Art Open Access (CC0, https://openaccess-api.clevelandart.org) and the Art "
                  "Institute of Chicago's public API (https://api.artic.edu/docs/): public-domain works, CC0 pictures; "
                  "Chicago's descriptions CC BY 4.0 where used. {what} records, each credited below.")
CRAFTS_PACKS = {
    "commons_pottery_ceramics": (build_commons_pottery_ceramics, COMMONS_LICENCE.format(
        what="pottery, kiln, glaze and clay")),
    "museum_ceramics": (build_museum_ceramics, MUSEUM_LICENCE.format(what="Ceramic, stoneware, porcelain and "
                                                                          "earthenware")),
    "commons_jewellery_beading": (build_commons_jewellery_beading, COMMONS_LICENCE.format(
        what="jewellery making, bead, finding, gem cutting and enamelling")),
    "museum_jewellery": (build_museum_jewellery, MUSEUM_LICENCE.format(what="Jewellery, enamel and bead")),
    "commons_paper_crafts": (build_commons_paper_crafts, COMMONS_LICENCE.format(
        what="origami, paper craft, scrapbooking, card, bookbinding, papermaking, calligraphy and printmaking")),
    "commons_candle_soap": (build_commons_candle_soap, COMMONS_LICENCE.format(what="candle and soap making")),
    "commons_glass_carving": (build_commons_glass_carving, COMMONS_LICENCE.format(
        what="stained glass, glassblowing, mosaic, woodcarving and whittling")),
    "commons_art_supplies": (build_commons_art_supplies, COMMONS_LICENCE.format(
        what="painting and drawing supply")),
    "commons_models_resin": (build_commons_models_resin, COMMONS_LICENCE.format(
        what="scale model, miniature and resin")),
    "museum_glass_crafts": (build_museum_glass_crafts, MUSEUM_LICENCE.format(what="Glass, lacquer, calligraphy and "
                                                                                  "bookbinding")),
    "open_images_crafts": (build_open_images_crafts, OI_LICENCE),
}
CRAFTS_LIMITS = {
    "commons_pottery_ceramics": 1200,       # 15 categories
    "museum_ceramics": 2000,                # Cleveland about 3,000 CC0 ceramics; Chicago about 9,000
    "commons_jewellery_beading": 1200,      # 20 categories
    "museum_jewellery": 1200,               # Cleveland about 1,200 jewellery and enamel; Chicago about 900
    "commons_paper_crafts": 1600,           # 28 categories
    "commons_candle_soap": 100,             # 3 categories, few open files
    "commons_glass_carving": 1000,          # 14 categories
    "commons_art_supplies": 900,            # 13 categories
    "commons_models_resin": 500,            # 6 categories
    "museum_glass_crafts": 1000,            # Cleveland about 600; Chicago about 2,500
    "open_images_crafts": 2500,             # 47 labels
}
CRAFTS_COMMONS_KEYS = ("commons_pottery_ceramics", "commons_jewellery_beading", "commons_paper_crafts",
                       "commons_candle_soap", "commons_glass_carving", "commons_art_supplies", "commons_models_resin")
# The pottery and jewellery collections the owner asked for by name (each also a topic group in the kit).
POTTERY_KEYS = ("commons_pottery_ceramics", "museum_ceramics")
JEWELLERY_KEYS = ("commons_jewellery_beading", "museum_jewellery")
CRAFTS_SPECS = POTTERY + JEWELLERY + PAPER + CANDLE_SOAP + GLASS_CARVING + ART_SUPPLIES + MODELS_RESIN


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try an arts and crafts pack builder.")
    parser.add_argument("key", choices=sorted(CRAFTS_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--quick", action="store_true", help="Open Images: the validation and test sets only")
    args = parser.parse_args(argv)
    QUICK["on"] = args.quick
    entries = CRAFTS_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
