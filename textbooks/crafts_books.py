"""Arts and crafts (not textiles) for the reference library, in the group "Reference, arts and crafts" (the owner's
request of 2026-11-22; pottery and jewellery are named collections inside it: the request words pottery-books and
jewellery-books). Keys: crafts (every book), craft:<name>.

What this module builds, each IN FULL:
  - Wikibooks' Origami and Bookbinding (CC BY-SA 4.0, share-alike), every page;
  - old public-domain craft books (published before 1931; the builder checks each Internet Archive item's year):
      pottery     Charles F. Binns, The Potter's Craft (1910); William Burton and Francis Hobson, Handbook of Marks
                  on Pottery and Porcelain (1909); Pottery Decorating (1907);
      jewellery   Augustus F. Rose and Antonio Cirino, Jewelry Making and Design (1917);
      paper and books  Douglas Cockerell, Bookbinding and the Care of Books (1901); Edward Johnston, Writing and
                  Illuminating, and Lettering (1906, calligraphy); paper folding and cutting (1892) and Fun with
                  Paper Folding (1928, origami);
      glass, carving, painting  C. W. Whall, Stained Glass Work (1905); Easy Lessons in Practical Wood Carving
                  (1905); Elementary Sloyd and Whittling (1906); A. P. Laurie, The Painter's Methods and Materials
                  (1926);
      soap and candles  A Practical Treatise on the Manufacture of Soap and Candles (1888), with the lye warning
                  first.
    They are OLD: their methods, safety advice and materials (lead glazes and pigments, lye handling, open flames)
    are out of date, and the machine-read text has the scanner's mistakes; each notice says so and gives today's
    safety note first.

Not built (NOT_INCLUDED, each with its index address): the Met's and other museums' craft publications (copyright),
Ravelry, Instructables, Pinterest and YouTube, and modern craft books (copyright).

Run from the repository's folder:
  python3 textbooks/crafts_books.py craft:binns_potters_craft_1910 --out build/textbooks --limit 5
  python3 textbooks/crafts_books.py --list crafts
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from electronics_books import wikibook  # noqa: E402

GROUP = "crafts"
GROUPS = {GROUP: "Reference, arts and crafts"}

KILN_NOTE = ("Safety today: kilns get extremely hot and give off fumes: fire them with ventilation, away from "
             "anything that burns; dry clay and glaze dust contains silica (clean up wet), and old books' lead "
             "glazes are not safe for food.")
LYE_NOTE = ("Safety today: lye (sodium hydroxide) burns skin and eyes: wear goggles and gloves, always add lye to "
            "water, never water to lye, keep children and pets away; hot wax catches fire: use a double boiler.")
TORCH_NOTE = ("Safety today: torches, pickling acids and hot metal burn: work on a fireproof surface with "
              "ventilation and eye protection; old books' cyanide and mercury methods must never be used.")
GLASS_NOTE = ("Safety today: cut glass is sharp and lead came and solder contain lead: wear eye protection, wash your "
              "hands and do not eat while working.")
BLADE_NOTE = ("Safety today: carving tools are very sharp: cut away from yourself and wear a cut-resistant glove on "
              "the hand holding the wood.")
PIGMENT_NOTE = ("Safety today: many old pigments (lead white, vermilion, emerald green) are poisonous: use modern "
                "labelled paints, and do not eat or drink while working.")
GENERAL_NOTE = "Safety today: keep craft knives and tools sharp and stored safely."

OLD = dict(group=GROUP, country="United States", licence="Public domain (published before 1931)",
           licence_url="https://www.copyright.gov/help/faq/faq-duration.html", old_public_domain=True,
           level="reference", changes="its scanned pages' machine-read text (with the scanner's mistakes) made into "
                                      "web pages, one per chapter")


def old_book(name, title, subject, publisher, archive, year, description, safety, country="United States",
             collection=""):
    """An old public-domain craft book from the Internet Archive as a PDF entry, today's safety note first."""
    return dict(OLD, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                published=str(year), country=country, collection=collection,
                description=description + f" Published in {year}: an old book whose methods, materials and safety "
                                          "advice are out of date, kept for its explanations and history.",
                notice=f"{safety} This is an old book (published in {year}); its machine-read text has the "
                       "scanner's mistakes.")


PDFS = [
    old_book("binns_potters_craft_1910", "The Potter's Craft (Charles F. Binns, 1910)", "Pottery", "Charles F. Binns "
             "(D. Van Nostrand)", "potterscraftprac00binn", 1910,
             "A practical guide for the studio and workshop by the first director of the New York State School of "
             "Clayworking: clays and bodies, throwing and turning on the wheel, building by hand, moulds and "
             "casting, glazes and colours, kilns and firing, and faults and their remedies.", KILN_NOTE,
             collection="pottery"),
    old_book("burton_hobson_marks_pottery_porcelain_1909", "Handbook of Marks on Pottery and Porcelain (William "
             "Burton and Francis Hobson, 1909)", "Pottery marks", "William Burton and Francis Hobson (Macmillan)",
             "handbookofmarkso00burt", 1909,
             "A handbook of the makers' marks found on the bottom of pottery and porcelain from Europe, Britain, "
             "America and Asia, with what each mark means, for telling who made a piece and when.", KILN_NOTE,
             country="United Kingdom", collection="pottery"),
    old_book("pottery_decorating_1907", "Pottery Decorating: All the Processes for Decorating Pottery and Porcelain "
             "(1907)", "Pottery decoration", "R. Hainbach (Scott, Greenwood and Son)", "gri_33125001154091", 1907,
             "A description of the ways pottery and porcelain are decorated: painting, printing and transfers, "
             "gilding, lustres, glazes and colours, and firing.", KILN_NOTE, country="United Kingdom",
             collection="pottery"),
    old_book("rose_cirino_jewelry_making_1917", "Jewelry Making and Design (Augustus F. Rose and Antonio Cirino, "
             "1917)", "Jewellery making", "Augustus F. Rose and Antonio Cirino (Metal Crafts Publishing)",
             "JewelryMakingAndDesign", 1917,
             "An illustrated textbook for students and craftworkers: tools and the workbench, soldering, piercing "
             "and sawing, setting stones, rings, brooches, pendants and chains, enamelling, chasing and repousse, "
             "and design.", TORCH_NOTE, collection="jewellery"),
    old_book("cockerell_bookbinding_1901", "Bookbinding, and the Care of Books (Douglas Cockerell, 1901)",
             "Bookbinding", "Douglas Cockerell (John Hogg)", "bookbindingcareo00cockrich", 1901,
             "A handbook for amateurs, bookbinders and librarians: folding and sewing, backing, boards and covering, "
             "leather and cloth bindings, finishing and tooling, and how to care for books.", GENERAL_NOTE,
             country="United Kingdom"),
    old_book("johnston_writing_illuminating_lettering_1906", "Writing and Illuminating, and Lettering (Edward "
             "Johnston, 1906)", "Calligraphy and lettering", "Edward Johnston (John Hogg)", "writingilluminat00john_0",
             1906, "The classic handbook of calligraphy: cutting and holding the broad pen, the alphabets and their "
             "forms, spacing and layout, capitals and versals, illumination with gold and colour, and lettering.",
             GENERAL_NOTE, country="United Kingdom"),
    old_book("ball_paper_folding_cutting_1892", "Paper Folding and Cutting (Katherine M. Ball, 1892)",
             "Paper folding (origami)", "Katherine M. Ball", "paperfoldingcutt00ball", 1892,
             "A series of foldings and cuttings for kindergartens and schools: folds from a square, simple figures "
             "and patterns cut from folded paper.", GENERAL_NOTE),
    old_book("murray_fun_with_paper_folding_1928", "Fun with Paper Folding (William D. Murray and Francis J. Rigney, "
             "1928)", "Paper folding (origami)", "William D. Murray and Francis J. Rigney (Fleming H. Revell)",
             "funwithpaperfold00murr", 1928,
             "A book of paper folding (origami) models with step-by-step instructions: boxes, boats, birds, animals, "
             "hats and toys.", GENERAL_NOTE),
    old_book("whall_stained_glass_work_1905", "Stained Glass Work (C. W. Whall, 1905)", "Stained glass",
             "C. W. Whall (John Hogg)", "stainedglasswo00whal", 1905,
             "A textbook for students and workers in glass: tools, cutting glass, painting and firing, leading up, "
             "cementing and fixing windows, and design.", GLASS_NOTE, country="United Kingdom"),
    old_book("hodgson_easy_lessons_wood_carving_1905", "Easy Lessons in the Art of Practical Wood Carving (Fred T. "
             "Hodgson, 1905)", "Woodcarving", "Fred T. Hodgson (Frederick J. Drake)", "easylessonsinart00hodg", 1905,
             "Lessons in wood carving for carpenters, joiners and amateurs: the tools and their sharpening, woods, "
             "chip carving, relief and carving in the round.", BLADE_NOTE),
    old_book("larsson_elementary_sloyd_whittling_1906", "Elementary Sloyd and Whittling (Gustaf Larsson, 1906)",
             "Whittling", "Gustaf Larsson (Silver, Burdett)", "elementarysloydw00lars", 1906,
             "A school course in whittling and simple woodwork with the knife: holding and using the knife safely, "
             "and graded projects with working directions.", BLADE_NOTE),
    old_book("laurie_painters_methods_materials_1926", "The Painter's Methods and Materials (A. P. Laurie, 1926)",
             "Painting materials", "A. P. Laurie (Seeley, Service)", "paintersmethodsm00lauruoft", 1926,
             "How pigments behave in oil, tempera, watercolour and fresco: grounds and canvases, brushes, mediums "
             "and varnishes, colours and their permanence, and the methods of the old masters.", PIGMENT_NOTE,
             country="United Kingdom"),
    old_book("brannt_soap_candles_1888", "A Practical Treatise on the Manufacture of Soap and Candles (William T. "
             "Brannt, 1888)", "Soap and candle making", "William T. Brannt (Henry Carey Baird)",
             "practicaltreatis00bran", 1888,
             "The chemistry and manufacture of soap and candles: fats and oils, lye, saponification, kinds of soap, "
             "tallow, wax and stearin candles, wicks and moulds.", LYE_NOTE),
]

GUIDES = [
    wikibook(GROUP, "wikibooks_origami", "Origami", "Origami (Wikibooks)", "Paper folding (origami)",
             "Wikibooks' open book on origami: paper, the basic folds and bases, symbols of origami diagrams, and "
             "models step by step."),
    wikibook(GROUP, "wikibooks_bookbinding", "Bookbinding", "Bookbinding (Wikibooks)", "Bookbinding",
             "Wikibooks' open book on bookbinding: tools and materials, folding and sewing signatures, case and "
             "Coptic bindings, and repairs."),
]


def collection_keys(name):
    """The keys of one named collection of this module ("pottery", "jewellery")."""
    return [f"craft:{p['name']}" for p in PDFS if p.get("collection") == name]


COLLECTION = K.Collection("craft", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"crafts": lambda: [f"craft:{g['name']}" for g in GUIDES + PDFS],
                                 "pottery-books": lambda: collection_keys("pottery"),
                                 "jewellery-books": lambda: collection_keys("jewellery")})

LICENCE_LINES = {
    "crafts_old_books": "Internet Archive scans of craft books published before 1931: public domain in the US (the "
                        "item's year is checked at every build, build_textbooks.archive_year). Books first published "
                        "in the UK are kept under the same US rule and marked with their country.",
}
NOT_INCLUDED = [
    ("Modern pottery, jewellery and craft books on the Internet Archive", "In copyright (lending-only copies); only "
     "books published before 1931 are built. Index: https://archive.org/search?query=subject%3Apottery"),
    ("The Metropolitan Museum of Art's and other museums' craft publications", "The Met's MetPublications are free "
     "to read but copyright; not openly licensed. Link-only. Index: https://www.metmuseum.org/met-publications"),
    ("Ravelry, Instructables, Pinterest and YouTube craft tutorials", "Copyright; their terms forbid copying by "
     "program. Index: https://www.instructables.com/craft/"),
    ("Wikibooks books on pottery, jewellery, calligraphy, soap or candle making", "No such book exists on Wikibooks "
     "(checked 2026-11-22); Origami and Bookbinding are built. Index: https://en.wikibooks.org/wiki/Subject:Crafts"),
    ("Project Gutenberg's copies of these craft books", "Already in the Kiwix library (gutenberg_en_lcc-t and "
     "gutenberg_en_lcc-n); the books are built here from the Internet Archive's scans. Index: "
     "https://www.gutenberg.org/ebooks/bookshelf/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
