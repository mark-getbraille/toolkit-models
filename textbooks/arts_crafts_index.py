"""The guide to arts and crafts in the reference library: one index book, arts:index, in the group "Reference, arts and
crafts" (the owner's request of 22 November 2026: arts and crafts is a top-level section, and that group is its one
home in the library). Keys: arts:index; request word arts-crafts (the index with every craft book it lists).

What this module builds, in plain words:
  - arts:index, the toolkit's own facts and links (CC0, nothing downloaded): one page per craft, listing the books by
    key, the manual collections, the picture packs and the link-only sources. Its book lists are made from the craft
    modules themselves, so a craft book added there is listed here too:
      the textile craft books of home_crafts.py (the entries in the arts and crafts group: quilting, embroidery,
        weaving, spinning, dyeing, tatting, macramé, needlework and knitting, upholstery, leatherwork),
      the sewing, knitting and needlework books of thin_topics.py (thin:sewing, keys pdf:<name>),
      the pottery, jewellery, paper, bookbinding, calligraphy, glass, carving, painting, soap and candle books of
        crafts_books.py,
      and the photography collection (another helper is adding it; it is named here only by its request word).
  The home repair, pest and mending books stay in "Reference, home repair and pests" (home_crafts.py) and are not
  listed; the making books (3D printing, CNC) stay in their own group, with make:index linked for cutting machines.

The keys of the listed books did not change when they moved into the arts and crafts group. The index's left_out names
any listed key the library no longer has (practical_index.index_maker).

Run from the repository's folder:
  python3 textbooks/arts_crafts_index.py arts:index --out build/textbooks
  python3 textbooks/arts_crafts_index.py --list arts-crafts
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import crafts_books as CB  # noqa: E402
import home_crafts as HC  # noqa: E402
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
import thin_topics as TT  # noqa: E402

GROUP = CB.GROUP                       # "crafts": "Reference, arts and crafts" (named in crafts_books.py's GROUPS)
GROUPS = {}

# The photography collection's request word (the photography helper's branch; said generally until it is merged).
PHOTOGRAPHY_WORD = "photography"

# Which crafts_books.py subjects go on which page of the index (a subject not named here goes on "Other crafts").
CB_PAGES = {
    "Pottery and ceramics": ("Pottery",),
    "Jewellery and metalwork": ("Jewellery",),
    "Paper, books and lettering": ("Paper folding", "Bookbinding", "Calligraphy"),
    "Glass, carving and painting": ("Stained glass", "Woodcarving", "Whittling", "Painting"),
    "Soap and candles": ("Soap and candle",),
}


def textile_books():
    """("key", key, title) entries of the textile craft books: home_crafts.py's arts and crafts group entries, then
    thin_topics.py's sewing, knitting and needlework books."""
    rows = [("key", f"craft:{g['name']}", g["title"]) for g in HC.GUIDES + HC.PDFS if g["group"] == GROUP]
    rows += [("key", f"pdf:{e['name']}", e["title"]) for e in TT.SEWING]
    return rows


def crafts_books_page(page):
    """("key", key, title) entries of crafts_books.py for one index page (by the book's subject); "Other crafts"
    takes every book no page names."""
    named = [s for starts in CB_PAGES.values() for s in starts]
    rows = []
    for g in CB.GUIDES + CB.PDFS:
        starts = CB_PAGES.get(page)
        fits = any(g["subject"].startswith(s) for s in starts) if starts else \
            not any(g["subject"].startswith(s) for s in named)
        if fits:
            rows.append(("key", f"craft:{g['name']}", g["title"]))
    return rows


def sections():
    """The index's parts: (part title, intro, entries), as practical_index.index_maker reads them."""
    return [
        ("Textile crafts", "Knitting, crochet, lace, tatting and macramé, quilting, embroidery, weaving, spinning and "
                           "dyeing, sewing and needlework, upholstery and leatherwork.",
         textile_books() + [
             ("manuals", "sewing_textile", "Sewing machines, sergers and embroidery machines"),
             ("manuals", "textile_craft_tools", "Knitting machines, looms, spinning wheels and other textile tools"),
             ("pack", "commons_knit_crochet_lace", "Knitting, crochet, lace and tatting"),
             ("pack", "commons_quilt_embroidery_weaving", "Quilts, embroidery, needlepoint and weaving"),
             ("pack", "commons_sewing_mending", "Sewing patterns, notions, seams and mending"),
             ("pack", "commons_upholstery_leather_shoes", "Upholstery, leatherwork and shoemaking"),
             ("pack", "commons_fabrics_fibres", "Fabrics and fibres by name"),
             ("pack", "open_images_textile_crafts", "Crochet, cross-stitch, embroidery, quilts and lace in photos"),
             ("pack", "nmah_textiles_sewing", "Museum quilts, samplers, lace and historic sewing machines")]),
        ("Pottery and ceramics", "Clay, the wheel, glazes, kilns and firing, and pottery marks.",
         crafts_books_page("Pottery and ceramics") + [
             ("manuals", "pottery_kilns", "Kilns and potter's wheels"),
             ("pack", "commons_pottery_ceramics", "Potters, wheels, kilns, raku and stoneware"),
             ("pack", "museum_ceramics", "Ceramics in museums")]),
        ("Jewellery and metalwork", "Jewellery making, beading, wire work and enamels.",
         crafts_books_page("Jewellery and metalwork") + [
             ("manuals", "jewellery_tools", "Jewellery tools: rotary tools, torches, tumblers and kilns"),
             ("pack", "commons_jewellery_beading", "Jewellery making and beading"),
             ("pack", "museum_jewellery", "Jewellery, enamels and beads in museums")]),
        ("Paper, books and lettering", "Origami and paper cutting, bookbinding, calligraphy and lettering.",
         crafts_books_page("Paper, books and lettering") + [
             ("pack", "commons_paper_crafts", "Origami, kirigami, paper models, quilling and calligraphy")]),
        ("Glass, carving and painting", "Stained glass, woodcarving and whittling, and painters' materials.",
         crafts_books_page("Glass, carving and painting") + [
             ("manuals", "art_craft_supplies", "Art and craft supplies: safety data and labels"),
             ("pack", "commons_glass_carving", "Stained glass, glassblowing, mosaics and woodcarving"),
             ("pack", "commons_art_supplies", "Palettes, easels, paints and brushes"),
             ("pack", "museum_glass_crafts", "Glass, lacquer, calligraphy and bookbinding in museums")]),
        ("Soap and candles", "Soap and candle making, with the lye and hot-wax safety notes.",
         crafts_books_page("Soap and candles") + [
             ("pack", "commons_candle_soap", "Beeswax candles, wicks and soap")]),
        ("Other crafts", "Models and resin, and the crafts that fit no page above.",
         crafts_books_page("Other crafts") + [
             ("pack", "commons_models_resin", "Scale models, dioramas, model railways and resin casting"),
             ("pack", "open_images_crafts", "Pottery, beads, origami, paints and craft supplies in photos")]),
        ("Craft cutting machines and heat presses", "Cricut, Silhouette and other vinyl and paper cutters, heat "
                                                    "presses and heat-transfer vinyl.", [
             ("key", "make:index", "Home manufacturing and making: a guide (its cutting machine and heat press "
                                   "part)"),
             ("manuals", "craft_machines", "Cricut, Silhouette, Brother ScanNCut and Sizzix machines"),
             ("manuals", "heat_press_vinyl", "Heat presses, vinyl cutters and sublimation printers"),
             ("pack", "commons_cutting_lasers", "Vinyl cutters, cutting machines, heat presses and screen printing")]),
        ("Photography", "Cameras, taking pictures and photo technique.", [
             ("word", PHOTOGRAPHY_WORD, "The photography collection's books")]),
    ]


SECTIONS = sections()
INDEX = X.index_maker("arts", GROUP, "Arts and crafts: a guide to the library", "Arts and crafts",
                      "A guide to the library for arts and crafts: textile crafts, pottery, jewellery, paper and "
                      "books, glass, carving and painting, soap and candles, models, craft cutting machines and "
                      "photography, with the books, manuals and picture packs of each.", SECTIONS)
MAKERS = {"index": INDEX}


def every_key():
    """arts:index and every book key the index lists (the request word arts-crafts)."""
    return ["arts:index"] + [what for _p, _i, entries in SECTIONS for kind, what, *_r in entries if kind == "key"
                             and what != "make:index"]


COLLECTION = K.Collection("arts", GROUP, makers=MAKERS, words={"arts-crafts": every_key})

LICENCE_LINES = {
    "arts_index": "The arts and crafts index (arts:index) is the toolkit's own facts and links, CC0; each book it "
                  "lists has its own licence, shown in that book.",
}
NOT_INCLUDED = []


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
