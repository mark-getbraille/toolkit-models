"""Toys and children's products for the reference library, in the group "Reference, parenting and family" (the
owner's request of 2026-11-22). Keys: toys (every book), toys:<name>.

What this module builds, in plain words:
  - toys:index, a guide to the library for choosing toys and checking them for safety (the toolkit's own facts and
    links, CC0): choosing toys by age, choking and small parts, magnets, button batteries, riding toys and
    playgrounds, nursery products, recalls, and accessible and tactile toys, with the books by key, the picture packs,
    the manual collection and the CPSC's own pages as LINKS (cpsc.gov refuses programs);
  - IN FULL, two US Consumer Product Safety Commission publications read from the Internet Archive's copies of their
    ERIC microfiche (US government works, in the public domain):
      toys:cpsc_which_toy_for_which_child   Which Toy for Which Child (1997, CPSC publications 285 and 286): toys
                                            for each age from birth to twelve and the safety points for each age;
      toys:cpsc_public_playground_handbook  Handbook for Public Playground Safety (1997, CPSC publication 325):
                                            surfacing, use zones, equipment and the public playground checklist.
  Every book carries TOY_SAFETY in its notice (the picture packs' notes, written for a book).

Already in the library and not repeated: the CPSC's child safety guides (parent:cpsc_child_safety: safe sleep, toys,
magnets, water beads, button batteries, tip-overs), the CPSC recall books (request word recalls) and the parenting and
early childhood books (parenting, early-childhood).

Not built (NOT_INCLUDED, link-only): the CPSC's current pages (cpsc.gov refuses programs), the Strong Museum and the V&A
Museum of Childhood (no open licence), the makers' toy pages (copyright), and the American Foundation for the Blind's and
APH's accessible toy guides (copyright).

Run from the repository's folder:
  python3 textbooks/toys_books.py toys:cpsc_which_toy_for_which_child --out build/textbooks --limit 3
  python3 textbooks/toys_books.py --list toys
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "parenting"                    # "Reference, parenting and family" (parenting.py)
GROUPS = {}

# The same advice as the picture packs' notes (packs/toys_packs.py), written for a book.
TOY_SAFETY = ("Toy safety (CPSC): follow the age on the label; toys with small parts are not for children under 3, "
              "and small balls, marbles and balloons are choking hazards. Strong magnets and button or coin batteries "
              "that are swallowed are emergencies: go to the emergency room at once (a button battery can burn the "
              "throat in two hours). Keep battery doors screwed shut. Use a helmet on riding toys, look for soft "
              "surfacing under play equipment, and check SaferProducts.gov for recalls.")
OLD_NOTE = ("Published in 1997 and read from the Internet Archive's microfiche scan (the machine-read text has the "
            "scanner's mistakes): check the CPSC's current advice and recalls, which have changed since.")


def cpsc_pdf(name, title, subject, archive, description, version):
    """A CPSC publication read whole from the Internet Archive's copy of its ERIC microfiche."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject,
                    publisher="US Consumer Product Safety Commission (CPSC)", archive=archive, published="1997",
                    version=version, description=f"{description} {OLD_NOTE}",
                    notice=f"A work of the US Consumer Product Safety Commission (public domain), read from the "
                           f"Internet Archive's copy of its ERIC microfiche. {TOY_SAFETY}")


PDFS = [
    cpsc_pdf("cpsc_which_toy_for_which_child", "Which Toy for Which Child: a consumer's guide for selecting suitable "
             "toys, birth to twelve (CPSC, 1997)", "Choosing toys", "micro_IA41153403_0909",
             "The CPSC's two booklets on choosing toys: for young and older infants, toddlers, preschoolers and "
             "school children up to twelve, what a child of each age can do and likes, the toys that suit them "
             "(active, manipulative, make-believe, creative and learning play), and the safety points for each age.",
             "1997, CPSC publications 285 and 286 (Internet Archive item micro_IA41153403_0909, ERIC ED416999)"),
    cpsc_pdf("cpsc_public_playground_handbook", "Handbook for Public Playground Safety (CPSC, 1997)",
             "Playground safety", "micro_IA41153451_0274",
             "The CPSC's handbook for public playgrounds: surfacing under and around equipment, use zones, layout, "
             "installation and maintenance, general hazards (entrapment, sharp edges, protrusions), and the major "
             "kinds of equipment (climbers, merry-go-rounds, seesaws, slides, swings, spring rockers), with the "
             "public playground safety checklist for parents.",
             "1997, CPSC publication 325 (Internet Archive item micro_IA41153451_0274, ERIC ED427507)"),
]

CPSC = "https://www.cpsc.gov"
CPSC_WHY = "public information, but cpsc.gov refuses programs; open it in a browser"
SECTIONS = [
    ("Choosing toys by age", "What suits a child of each age, and the age label.", [
        ("key", "toys:cpsc_which_toy_for_which_child", "Which Toy for Which Child (CPSC, 1997)"),
        ("key", "parent:cpsc_child_safety", "Child safety at home, with toy safety (CPSC)"),
        ("pack", "commons_toys_by_type", "Toys by type: vehicles, blocks, dolls, plush, puppets, construction sets"),
        ("pack", "open_images_toys", "LEGO, toy vehicles, figures, dolls, plush, baby and bath toys"),
        ("pack", "commons_toys_sports_music", "Teddy bears, dolls, toy trains, LEGO, jigsaws, kites, board games"),
        ("link", "CPSC Toy Safety Business Guidance and consumer toy safety", CPSC + "/Safety-Education/"
                                                                                     "Safety-Education-Centers/Toys",
         CPSC_WHY)]),
    ("Choking, small parts, magnets and button batteries", "The dangers to watch for and what to do.", [
        ("key", "parent:cpsc_child_safety", "Magnets, water beads and button batteries (CPSC)"),
        ("link", "CPSC Button Cell and Coin Battery Information Center", CPSC + "/Safety-Education/"
         "Safety-Education-Centers/Button-Cell-Coin-Battery-Information-Center", CPSC_WHY),
        ("link", "CPSC magnets", CPSC + "/Safety-Education/Safety-Education-Centers/Magnets", CPSC_WHY),
        ("link", "Poison Help", "https://poisonhelp.hrsa.gov/", "call 1-800-222-1222 in the US; open it in a "
                                                                 "browser")]),
    ("Riding toys and playgrounds", "Tricycles, wagons, swings, slides and the ground under them.", [
        ("key", "toys:cpsc_public_playground_handbook", "Handbook for Public Playground Safety (CPSC, 1997)"),
        ("pack", "commons_ride_ons_playgrounds", "Rocking horses, tricycles, pedal cars and playground equipment"),
        ("link", "CPSC Public Playground Safety Handbook (current edition)", CPSC + "/Safety-Education/"
         "Safety-Guides/Playgrounds", CPSC_WHY)]),
    ("Nursery products", "Walkers, cradles, changing tables and the baby things.", [
        ("pack", "commons_nursery_more", "Baby walkers, changing tables, cradles, diapers and toy chests"),
        ("pack", "commons_baby_products", "Bottles, car seats, cribs, high chairs, gates, strollers"),
        ("manuals", "baby_gear", "Baby gear and toy manuals (Fisher-Price, Hasbro, Graco, VTech) at the Internet "
                                 "Archive"),
        ("word", "early-childhood", "Child care, newborns and infant feeding books")]),
    ("Recalls", "Is this toy recalled?", [
        ("word", "recalls", "The CPSC recall books by product type, with children's products and toys"),
        ("link", "SaferProducts.gov (search recalls and report an unsafe product)", "https://www.saferproducts.gov/",
         "a CPSC site; open it in a browser")]),
    ("Old toys in museums", "Antique toys, dolls and rattles.", [
        ("pack", "commons_museum_toys", "Antique toys and toys in museums"),
        ("pack", "met_toys", "Dolls, toys and rattles at the Met"),
        ("link", "The Strong National Museum of Play", "https://www.museumofplay.org/", "no open licence for its "
                                                                                       "collection images found"),
        ("link", "Young V&A (the V&A Museum of Childhood)", "https://www.vam.ac.uk/young", "the V&A's images are for "
                                                                                           "non-commercial use")]),
    ("Accessible and tactile toys", "Toys for children who are blind or have low vision.", [
        ("word", "vision-living", "The vision collection's books, with APH and NLS resources"),
        ("link", "APH (American Printing House for the Blind) products", "https://www.aph.org/",
         "copyright; open it in a browser")]),
]
INDEX = X.index_maker("toys", GROUP, "Toys and children's products: a guide to the library", "Toys and toy safety",
                      "A guide to the library for toys: choosing toys by age, choking, magnets and button batteries, "
                      "riding toys and playgrounds, nursery products, recalls, old toys in museums and accessible "
                      "toys.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("toys", GROUP, pdfs=PDFS, makers=MAKERS,
                          words={"toys": lambda: ["toys:index"] + [f"toys:{p['name']}" for p in PDFS]})

LICENCE_LINES = {
    "toys_cpsc": "The CPSC's Which Toy for Which Child and Handbook for Public Playground Safety (1997) are US "
                 "government works (17 U.S.C. 105, checked on govinfo.gov's policies page at every build), read from "
                 "the Internet Archive's copies of their ERIC microfiche (micro_IA41153403_0909, "
                 "micro_IA41153451_0274); archive.org's robots.txt allows the files (checked 2026-11-22).",
    "toys_index": "The index (toys:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("CPSC toy safety, button battery, magnet and playground pages, and the current playground handbook",
     "Public information, but www.cpsc.gov refuses programs (403, robots.txt included, checked 2026-11-22); the "
     "1997 editions are built from the Internet Archive and the current pages are links in toys:index. Index: "
     "https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Toys"),
    ("The Strong National Museum of Play (collections and the Toy Hall of Fame)", "No open licence was found for its "
     "online collection images and text (checked 2026-11-22). Link-only. Index: https://www.museumofplay.org/"),
    ("V&A Museum of Childhood (Young V&A) collection", "The V&A's images and text are for non-commercial use (the "
     "kit's vam collection is personal use). Link-only here. Index: https://www.vam.ac.uk/young"),
    ("Toy makers' safety and age guides (Fisher-Price, LEGO, Hasbro, Mattel)", "The makers' copyright; their "
     "manuals are in the baby_gear manual collection at the Internet Archive. Index: https://www.toyassociation.org/"),
    ("Accessible and tactile toy guides (APH, AFB, Perkins, Paths to Literacy)", "Copyright of each organisation; "
     "link-only. Index: https://www.aph.org/ and https://www.perkins.org/resources/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
