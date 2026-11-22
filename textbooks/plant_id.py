"""Plant identification for the reference library, in the group "Reference, plant identification" (the owner's
request of 2026-11-22). Keys: plant-id (every book), plantid:<name>.

What this module builds, in plain words, each IN FULL:
  - the US Forest Service's "Celebrating Wildflowers" pages, every page (wildflower viewing, the plant of the week
    with how to recognise each plant, rare plants, invasive plants, ethnobotany, native plant materials, pollinators);
  - NCCIH's "Herbs at a Glance", every herb's page (what the science says about each herb as the source describes
    it, and its safety); no doses are given here, and every notice says to ask a doctor or pharmacist first;
  - the National Invasive Species Information Center's invasive plant profiles (terrestrial and aquatic plants:
    what each looks like, where it came from and why it is a problem);
  - Silvics of North America (USDA Agriculture Handbook 654, 1990), the Forest Service's tree-by-tree book of North
    American trees (the Internet Archive's copy; its hardwoods volume, the one the archive item serves first);
  - old public-domain field guides and botany books (published before 1931; the builder checks each item's year on
    the Internet Archive at every build): How to Know the Wild Flowers (Mrs William Starr Dana, 1913 edition),
    Mathews's Field Book of American Wild Flowers (1902), Keeler's Our Native Trees (1900), Apgar's Trees of the
    Northern United States (1892), Sargent's Manual of the Trees of North America (1905), Parsons's How to Know the
    Ferns (1899), Grout's Mosses with Hand-Lens and Microscope (1900), Marshall's The Mushroom Book (1922 edition),
    Atkinson's Mushrooms: Edible, Poisonous, etc. (1900), Pammel's Weeds of the Farm and Garden (1911) and Manual of
    Poisonous Plants (1911), and Saunders's Useful Wild Plants of the United States and Canada (1920). Each describes
    plants by leaf, bark, flower, fruit, smell and habitat in words, which suits a reader who cannot see the
    pictures; each says what is out of date.
  Every book carries the foraging and poison safety note (SAFETY): never eat a wild plant or mushroom unless an expert
  has confirmed it in person; deadly lookalikes (water hemlock and poison hemlock, death cap and destroying angel);
  poison ivy, oak and sumac; Poison Control 1-800-222-1222; children and pets.

Already in the library and not repeated: the US Army's survival manual with its edible and poisonous plant appendices
(pdf:army_atp_3_50_21_survival), the gardening books and lawn weeds (garden:), the plant and weed picture
collections, and Wikibooks whole in the Kiwix library.

Not built (NOT_INCLUDED, link-only): the USDA PLANTS database (a program-only site: link), the FDA Poisonous Plant
Database (retired), CDC/NIOSH poisonous plant pages (refuse programs), the ASPCA toxic plant list (copyright),
MushroomExpert.com and modern field guides (copyright), state invasive species lists (each state's own).

Run from the repository's folder:
  python3 textbooks/plant_id.py plantid:nccih_herbs_at_a_glance --out build/textbooks --limit 3
  python3 textbooks/plant_id.py --list plant-id
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "plantid"
GROUPS = {GROUP: "Reference, plant identification"}

SAFETY = ("Safety: never eat, taste or use any wild plant or mushroom unless an expert has identified it in person: "
          "deadly plants look like edible ones (water hemlock and poison hemlock look like wild carrot; the death cap "
          "and destroying angel look like edible mushrooms), and a book or picture is never enough. Learn poison ivy, "
          "poison oak and poison sumac, and wash skin and clothes after touching them. Keep children and pets away "
          "from unknown plants. If someone may have eaten a poisonous plant or mushroom, call Poison Control at "
          "1-800-222-1222 (US), or 911 if they are very ill.")
HERB_SAFETY = ("Herbs as medicine: this describes herbs as the source does and gives no doses; herbs can interact with "
               "medicines and are not safe for everyone (pregnancy, children, surgery): ask a doctor or pharmacist "
               "before using one.")
OLD_GUIDE = ("Published in {year}: an old guide. Some plant names have changed, some plants it calls harmless or edible "
             "are now known to be harmful, and its medical uses are not advice; its descriptions of leaves, bark, "
             "flowers, fruit, smell and habitat are why it is here.")
OLD_MUSHROOM = ("Published in {year}: an old mushroom guide. Names and edibility have been revised since and some "
                "mushrooms once thought edible are now known to be poisonous: never use it to decide what to eat.")

GUIDES = [
    K.guide(GROUP, "usfs_celebrating_wildflowers", "Celebrating Wildflowers (US Forest Service)", "Wildflowers",
            "US Forest Service (US Department of Agriculture)",
            ["https://www.fs.usda.gov/wildflowers", "https://www.fs.usda.gov/managing-land/wildflowers"],
            r"^https://www\.fs\.usda\.gov/(wildflowers|managing-land/wildflowers)(/[A-Za-z0-9_.-]+)*$",
            "The Forest Service's wildflower pages, every page: where and how to view wildflowers, the plant of the "
            "week (each plant described: leaves, flowers, fruit, habitat and range), the beauty of wildflowers, rare "
            "plants, invasive plants, ethnobotany (how people have used plants), native plant materials and "
            "pollinators.",
            "From the US Forest Service: a US government work (public domain). " + SAFETY, depth=2,
            follow=r"^https://www\.fs\.usda\.gov/(wildflowers|managing-land/wildflowers)(/[A-Za-z0-9_-]+)*/"
                   r"(index\.(shtml|php))?$",
            units=[(r"plant-of-the-week", "Plant of the week"), (r"invasive", "Invasive plants"),
                   (r"[Rr]are", "Rare plants"), (r"ethnobotany", "Ethnobotany"), (r"pollinator", "Pollinators"),
                   (r".", "Wildflowers")], limit=260),
    K.guide(GROUP, "nccih_herbs_at_a_glance", "Herbs at a Glance (NCCIH, National Institutes of Health)",
            "Medicinal plants", "National Center for Complementary and Integrative Health (NCCIH)",
            "https://www.nccih.nih.gov/health/herbsataglance", r"^https://www\.nccih\.nih\.gov/health/[a-z0-9-]+$",
            "NCCIH's fact sheets on herbs and botanicals, every herb: its common and Latin names, what it has been used "
            "for, what the science says, and its safety (side effects and interactions), as NCCIH describes it.",
            "From NCCIH, part of the National Institutes of Health: a US government work (public domain). " +
            HERB_SAFETY + " " + SAFETY, depth=1, limit=90),
    K.guide(GROUP, "nisic_invasive_plants", "Invasive plant profiles (National Invasive Species Information Center, "
            "USDA)", "Invasive plants", "National Invasive Species Information Center, USDA National Agricultural "
            "Library", ["https://www.invasivespeciesinfo.gov/terrestrial/plants",
                        "https://www.invasivespeciesinfo.gov/aquatic/plants"],
            r"^https://www\.invasivespeciesinfo\.gov/(terrestrial|aquatic)/plants(/[a-z0-9-]+)?$",
            "The USDA's invasive plant profiles, every plant: its names, what it looks like, where it came from, where "
            "it grows in the US and why it harms native plants, with links to state and federal resources.",
            "From the USDA National Agricultural Library: a US government work (public domain). Each state keeps its "
            "own noxious weed list. " + SAFETY, depth=1,
            units=[(r"/aquatic/", "Aquatic plants"), (r".", "Land plants")], limit=150),
]

PDFS = [
    K.us_pdf(GROUP, name="usfs_silvics_north_america", title="Silvics of North America, hardwoods volume (USDA "
             "Agriculture Handbook 654, 1990)", subject="Trees", publisher="US Forest Service (US Department of "
             "Agriculture)", archive="Silvics", published="1990",
             version="1990 edition (Internet Archive item Silvics: the volume it serves first)",
             description="The Forest Service's tree-by-tree reference for North American trees: for each species its "
                         "habitat (range, climate, soils), life history (flowering, fruiting, seeds, growth), "
                         "special uses and genetics, in plain botanical words.",
             notice="A work of the US Forest Service (public domain), read from the Internet Archive's copy. " + SAFETY),
]


def old(name, title, subject, publisher, archive, year, description, note=OLD_GUIDE):
    """One old field guide or botany book of the Internet Archive, with the safety note in its notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=SAFETY)


PDFS += [
    old("dana_how_to_know_wild_flowers", "How to Know the Wild Flowers (Mrs William Starr Dana)", "Wildflowers",
        "Mrs William Starr Dana (Charles Scribner's Sons)", "howtoknowwildflo00parsrich", 1913,
        "A guide to the names, haunts and habits of common North American wildflowers, arranged by flower colour, "
        "each described in words."),
    old("mathews_field_book_wild_flowers", "Field Book of American Wild Flowers (F. Schuyler Mathews, 1902)",
        "Wildflowers", "F. Schuyler Mathews (G. P. Putnam's Sons)", "fieldbookofamer00math", 1902,
        "A pocket field book of the wildflowers of eastern North America, by plant family, with each plant's "
        "leaves, flowers, height, habitat and flowering time."),
    old("keeler_our_native_trees", "Our Native Trees and How to Identify Them (Harriet L. Keeler, 1900)", "Trees",
        "Harriet L. Keeler (Charles Scribner's Sons)", "cihm_94832", 1900,
        "Trees of eastern North America described for identifying them: bark, leaves, flowers, fruit and wood."),
    old("apgar_trees_northern_us", "Trees of the Northern United States (Austin C. Apgar, 1892)", "Trees",
        "Austin C. Apgar (American Book Company)", "treesofnorthernu00apga", 1892,
        "How to study and identify trees: the parts of a tree, leaf shapes and arrangements, buds and twigs, with keys "
        "to the trees of the northern United States."),
    old("sargent_manual_trees_north_america", "Manual of the Trees of North America (Charles Sprague Sargent, 1905)",
        "Trees", "Charles Sprague Sargent (Houghton Mifflin)", "manualoftreesofn00sarg", 1905,
        "Every tree of North America north of Mexico, described species by species by the director of the Arnold "
        "Arboretum."),
    old("parsons_how_to_know_ferns", "How to Know the Ferns (Frances Theodora Parsons, 1899)", "Ferns",
        "Frances Theodora Parsons (Charles Scribner's Sons)", "howtoknowfernsgu00parsrich", 1899,
        "A guide to the common ferns of eastern North America: their fronds, how the spores are borne, and where each "
        "grows."),
    old("grout_mosses_hand_lens", "Mosses with Hand-Lens and Microscope (A. J. Grout, 1900)", "Mosses",
        "A. J. Grout", "mosseswithhandle00grou", 1900,
        "A non-technical handbook of the common mosses of the northeastern United States."),
    old("marshall_mushroom_book", "The Mushroom Book (Nina L. Marshall)", "Mushrooms and fungi",
        "Nina L. Marshall (Doubleday, Page)", "mushroombookpopu00marsrich", 1922,
        "A popular guide to identifying and studying the common fungi of North America.", note=OLD_MUSHROOM),
    old("atkinson_mushrooms", "Mushrooms: Edible, Poisonous, etc. (George F. Atkinson, 1900)", "Mushrooms and fungi",
        "George F. Atkinson (Andrus and Church)", "studiesofamericaf00atki", 1900,
        "Studies of American fungi: how mushrooms grow and how to recognise the common kinds, with the deadly "
        "Amanitas described in detail.", note=OLD_MUSHROOM),
    old("pammel_weeds_farm_garden", "Weeds of the Farm and Garden (L. H. Pammel, 1911)", "Weeds",
        "L. H. Pammel (Orange Judd)", "weedsoffarmgarde00pammrich", 1911,
        "The common weeds of the United States: how to recognise them, how they spread, and the weeds that poison "
        "livestock.", note=OLD_GUIDE + " Its weed killers are out of date: follow current product labels."),
    old("pammel_manual_poisonous_plants", "A Manual of Poisonous Plants (L. H. Pammel, 1911)", "Poisonous plants",
        "L. H. Pammel (Torch Press)", "manualofpoisonou00pammrich", 1911,
        "The poisonous plants of eastern North America, chiefly, and the signs of poisoning in people and animals."),
    old("saunders_useful_wild_plants", "Useful Wild Plants of the United States and Canada (Charles Francis Saunders, "
        "1920)", "Edible wild plants and foraging", "Charles Francis Saunders (Robert M. McBride)",
        "usefulwildplants00saun", 1920,
        "Wild plants that people have used for food, drink, medicine and household needs, described plant by plant.",
        note=OLD_GUIDE + " Never eat a wild plant on the word of a book: an expert must confirm it in person."),
]

COLLECTION = K.Collection("plantid", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"plant-id": lambda: [f"plantid:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "plantid_us": "www.fs.usda.gov, www.nccih.nih.gov and www.invasivespeciesinfo.gov: works of the US government "
                  "(17 U.S.C. 105, checked on govinfo.gov's policies page at every build); robots.txt allows the "
                  "pages, no AI rules (checked 2026-11-22). Silvics of North America is a Forest Service handbook "
                  "read from the Internet Archive's copy (Silvics).",
    "plantid_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, "
                         "so a later reprint is refused); archive.org's robots.txt allows the files (2026-11-22).",
}
NOT_INCLUDED = [
    ("USDA PLANTS Database", "Public domain, but plants.usda.gov is a program-only page (its text comes from a "
     "service the page calls) and has no plain pages to read; link-only. Index: https://plants.usda.gov/"),
    ("FDA Poisonous Plant Database (PLANTOX)", "Public domain, but retired: its address answers \"404\" "
     "(2026-11-22). Pammel's Manual of Poisonous Plants (1911) is built. Index: "
     "https://www.fda.gov/food/science-research-food"),
    ("CDC/NIOSH poisonous plants (outdoor workers)", "Public domain under CDC's terms, but www.cdc.gov answered this "
     "build machine \"403\" (2026-11-22). Link-only. Index: https://www.cdc.gov/niosh/outdoor-workers/about/"
     "poisonous-plants.html"),
    ("ASPCA toxic and non-toxic plants for dogs, cats and horses", "Copyright of the ASPCA; link-only. Index: "
     "https://www.aspca.org/pet-care/animal-poison-control/toxic-and-non-toxic-plants"),
    ("MushroomExpert.com and modern mushroom and foraging field guides (Peterson, Audubon, Samuel Thayer)",
     "Copyright of their authors; link-only. Index: https://www.mushroomexpert.com/"),
    ("State noxious weed and invasive species lists", "Each state's own, and many state works are copyright; the "
     "federal profiles are built (plantid:nisic_invasive_plants). Index: https://www.invasivespeciesinfo.gov/"
     "unitedstates"),
    ("Edible Wild Plants of Eastern North America (Fernald and Kinsey, 1943) and other later foraging books",
     "Published after 1930: copyright; link-only. Index: https://archive.org/search?query=edible+wild+plants"),
    ("The Army survival manual's edible and poisonous plant appendices", "Already in the library: "
     "pdf:army_atp_3_50_21_survival (ATP 3-50.21, 2018). Index: https://archive.org/details/survival-atp-3-50-21"),
    ("Wikibooks plant and mushroom books (CC BY-SA)", "Already whole in the Kiwix library (wikibooks_en_all). Index: "
     "https://en.wikibooks.org/wiki/Subject:Botany"),
    ("NPS park plant pages", "The Park Service's plant subject page answered \"404\" (2026-11-22); individual park "
     "pages are many small pages, not a guide. Link-only. Index: https://www.nps.gov/subjects/plants/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
