"""Edible wild plants and foraging for the reference library, in the group "Reference, foraging and edible wild plants"
(the owner's request of 2026-11-22). Keys: foraging (every book), forage:<name>.

A sibling of plant_id.py (plantid:, "Reference, plant identification"): that module already builds the wildflower,
tree, fern, poisonous plant and mushroom field guides and Saunders's Useful Wild Plants (1920); this one goes deeper
into eating wild food and LINKS those books (and the survival manuals' edible plant chapters) instead of repeating
them.

What this module builds, in plain words:
  - forage:index, a guide to foraging in the library (the toolkit's own facts and links, CC0), one page per part:
    wild greens, berries and fruit, nuts, roots, flowers and seaweeds by region and season; mushrooms; the deadly
    lookalikes of each common wild food; harvesting ethically and legally (park rules, permits, protected species,
    sprayed and polluted ground); preparing and cooking wild food (with the cookbooks); foraging by touch, smell and
    texture for people with low vision; and foraging outside the US (UK, Canada, Australia, New Zealand). It lists
    the books by key, the picture packs, the manual collections and the copyright books and sites as links only;
  - IN FULL, works of governments:
      the National Park Service's own pages on gathering plants, berries and mushrooms in the parks (Shenandoah's
      collecting rules, Indiana Dunes's rules for natural items, Klondike Gold Rush's hunting and gathering policy,
      Catoctin Mountain Park's ban on digging ramps and Grand Teton's mushroom notice): each park sets its own rules
      in its superintendent's compendium (36 CFR 2.1), which these pages show by example;
      the UK Food Standards Agency's Guidance for safe foraging (GOV.UK, Open Government Licence v3.0, a non-US
      source: UK law and species);
      Food Plants of the North American Indians (USDA Miscellaneous Publication 237, Elias Yanovsky, 1936), the
      USDA's list of more than a thousand wild plants used for food, by family;
      the US Army's 1957 Survival manual (FM 21-76), the older edition with its chapters on wild plant food (the 1992
      edition and ATP 3-50.21 are already in the library), judged by the release rule for military publications;
  - old public-domain books (published before 1931; the builder checks each item's year on the Internet Archive at
    every build): Charles McIlvaine's One Thousand American Fungi (1902 printing), Charles H. Peck's Mushrooms and
    their Use (1897), W. Hamilton Gibson's Our Edible Toadstools and Mushrooms (1895), M. E. Hard's The Mushroom,
    Edible and Otherwise (1908), Güssow and Odell's Mushrooms and Toadstools of Canada (1927, Canada's Department of
    Agriculture) and Minnie Reed's The Economic Seaweeds of Hawaii and their Food Value (1907). Each says plainly
    what is out of date: McIlvaine in particular ate mushrooms now known to be poisonous.
  Every book carries FORAGE_SAFETY in its notice: never eat a wild plant or mushroom unless an expert has confirmed
  it in person; deadly lookalikes; Poison Control 1-800-222-1222; never taste to identify; permission, protected
  species and sprayed or polluted ground.

Already in the library and not repeated (linked from the index): the plant identification books (plant-id: the
Forest Service's wildflower pages with their ethnobotany pages on food plants, Saunders's Useful Wild Plants,
Marshall's and Atkinson's mushroom books, Pammel's poisonous plants), the survival manuals with their edible and
poisonous plant chapters (ATP 3-50.21, FM 21-76 of 1992, AFH 10-644), the cookbooks and outdoor cooking books, and the
USDA Farmers' Bulletins (pub:usda_farmers_bulletins, with Bulletin 796 on common edible and poisonous mushrooms).

Not built (NOT_INCLUDED, link-only): Medsger's Edible Wild Plants (1939) and Fernald and Kinsey's Edible Wild Plants
of Eastern North America (1943), both with their copyright renewed; Euell Gibbons, Samuel Thayer and other modern
books (copyright); the USDA PLANTS database (a program-only site); iNaturalist's website (never read: its pictures come
only through GBIF and the open-data bucket); extension foraging guides (each university's copyright or non-commercial
terms); New Zealand, Canadian and Australian government pages whose reuse terms were not confirmed.

Run from the repository's folder:
  python3 textbooks/foraging.py forage:fsa_safe_foraging_uk --out build/textbooks --limit 3
  python3 textbooks/foraging.py --list foraging
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

GROUP = "foraging"
GROUPS = {GROUP: "Reference, foraging and edible wild plants"}

# The safety notice every book carries (packs/foraging_preserving_packs.py says the same in FORAGE_NOTE and
# MUSHROOM_NOTE, written for a picture).
FORAGE_SAFETY = ("Foraging safety: never eat a wild plant unless an expert has confirmed it in person, and never eat "
                 "a wild mushroom unless an expert has confirmed it: deadly plants and mushrooms look like edible "
                 "ones (water hemlock and poison hemlock look like wild carrot; the death cap and destroying angels "
                 "look like edible mushrooms), and a book, picture or app is never enough. Never taste a plant to "
                 "find out what it is. Gather only with the landowner's permission and within the rules of the park "
                 "or forest; leave protected and rare plants alone; do not gather beside roads, on sprayed lawns, "
                 "verges or farm edges, or from polluted water. Eat a small amount of a new wild food the first time. "
                 "If someone may have eaten a poisonous plant or mushroom, call Poison Control at 1-800-222-1222 "
                 "(US), or 911 if they are very ill.")
OLD_MUSHROOM = ("Published in {year}: an old mushroom book. Names and edibility have been revised since, some "
                "mushrooms it calls edible are now known to be poisonous or deadly, and its tests for telling edible "
                "from poisonous mushrooms are not reliable: never use it to decide what to eat. Its descriptions of "
                "cap, gills, stem, spore print, smell, texture and habitat are why it is here.")
NON_US = ("A non-US source: its laws, species and advice are those of {country}; US readers follow their own state's "
          "and the park's or forest's rules.")

# ====================================================================== National Park Service

NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_PAGES = [NPS + p for p in ("/shen/learn/management/collecting-plants.htm",
                               "/indu/learn/management/naturalitems.htm",
                               "/klgo/learn/management/hunting-gathering.htm",
                               "/cato/learn/news/catoctin-mountain-park-ramps-up-protection-of-native-plants.htm",
                               "/grte/learn/news/mushroom-collection-not-allowed-in-grand-teton-national-park.htm")]
GUIDES = [
    dict(X.page_list_book(
        GROUP, "nps_gathering_rules", "Gathering plants, berries and mushrooms in national parks: park rules (National "
        "Park Service)", "Foraging rules on public land", "National Park Service (US Department of the Interior)",
        NPS_PAGES, r"^https://www\.nps\.gov/[a-z]{4}/learn/(management|news)/[a-z0-9-]+\.htm$",
        "The National Park Service's own pages on gathering wild food in the parks, as examples of how each park "
        "sets its rules: Shenandoah's rules for collecting plants and mushrooms, Indiana Dunes's rules for natural "
        "items, Klondike Gold Rush's hunting and gathering policy (non-commercial gathering of berries and "
        "mushrooms), Catoctin Mountain Park on why digging ramps (wild leeks) is banned, and Grand Teton's notice on "
        "mushroom collection. Every park's rules are in its superintendent's compendium (under 36 CFR 2.1): check "
        "the park's own page before gathering anything.",
        f"From the National Park Service: \"material created by the National Park Service ... is generally "
        f"considered in the public domain\"; source: National Park Service (nps.gov). Park rules change from year to "
        f"year: check the park's current compendium. {FORAGE_SAFETY}",
        content=(r'<div id="main" role="main" class="MainContent">', r'<div id="related_content_position">|<footer\b'),
        units=[(r"/news/", "Park notices"), (r".", "Park rules")]),
        licence_page=NPS_TERMS, licence_text=NPS_TEXT),
]

# ====================================================================== UK Food Standards Agency (GOV.UK, OGL)

OGL_URL = "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
GOVUK_TERMS = "https://www.gov.uk/help/terms-conditions"
GOVUK_TEXT = r"Open Government Licence"
FSA_FORAGING = "https://www.gov.uk/government/publications/guidance-for-safe-foraging/guidance-for-safe-foraging"
GUIDES.append(dict(X.page_list_book(
    GROUP, "fsa_safe_foraging_uk", "Guidance for safe foraging (UK Food Standards Agency)", "Safe foraging",
    "Food Standards Agency (United Kingdom), on GOV.UK", [FSA_FORAGING],
    r"^https://www\.gov\.uk/government/publications/guidance-for-safe-foraging/guidance-for-safe-foraging$",
    "The UK Food Standards Agency's guidance for foraging safely: what foraging is, safe foraging tips (only pick what "
    "you can identify with certainty, wild mushrooms and their poisonous lookalikes, washing and cooking what you "
    "gather, avoiding polluted places) and gathering sustainably and legally in the UK.",
    "Contains public sector information licensed under the Open Government Licence v3.0 (Food Standards Agency, "
    "GOV.UK). " + NON_US.format(country="the United Kingdom") + " " + FORAGE_SAFETY),
    country="United Kingdom", licence="OGL-UK-3.0", licence_url=OGL_URL, licence_page=GOVUK_TERMS,
    licence_text=GOVUK_TEXT))

# ====================================================================== US government PDFs (Internet Archive)

PDFS = [
    K.us_pdf(GROUP, name="usda_food_plants_north_american_indians_1936", title="Food Plants of the North American "
             "Indians (USDA Miscellaneous Publication 237, Elias Yanovsky, 1936)", subject="Wild food plants",
             publisher="US Department of Agriculture", archive="foodplantsofnort237yano", published="1936",
             version="1936 edition (Internet Archive item foodplantsofnort237yano)",
             description="The USDA's list of more than a thousand plants that the Native peoples of North America "
                         "used for food, arranged by plant family: each plant's scientific and common names, the part "
                         "eaten and how it was prepared, and the people who used it.",
             notice="A work of the US Department of Agriculture (public domain), read from the Internet Archive's "
                    "copy (the National Agricultural Library's scan). Published in 1936: a list of what people ate, "
                    "not a guide to what is safe; some plants listed need special preparation or are poisonous "
                    "raw, and plant names have changed. " + FORAGE_SAFETY),
    K.us_pdf(GROUP, name="army_fm_21_76_survival_1957", title="Survival (FM 21-76, US Army, 1957)",
             subject="Survival and wild food", publisher="Headquarters, Department of the Army",
             archive="FM21-76Survival1957", distribution_a=True, published="1957-10",
             version="FM 21-76, October 1957 (Internet Archive item FM21-76Survival1957)",
             description="The US Army's 1957 survival manual, the older edition of FM 21-76 with its chapters on "
                         "finding food in the wild: edible wild plants (greens, roots, fruits, nuts and seaweeds), "
                         "poisonous plants, and preparing wild food, with water, shelter, fire and travel. The 1992 "
                         "edition (pdf:army_fm_21_76_survival_1992) and today's ATP 3-50.21 are already in the "
                         "library.",
             notice="A work of the US Army (public domain); the builder says what its own front pages print about "
                    "distribution. Published in 1957: its plant lists and tests are old, and its \"edibility "
                    "test\" is not a safe way to choose wild food. " + FORAGE_SAFETY),
]


def old(name, title, subject, publisher, archive, year, description, note=OLD_MUSHROOM, country="United States"):
    """One old public-domain book of the Internet Archive, with the foraging safety note in its notice."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note,
                    notice=FORAGE_SAFETY, country=country)


PDFS += [
    old("mcilvaine_one_thousand_american_fungi_1902", "One Thousand American Fungi (Charles McIlvaine and Robert K. "
        "Macadam, 1902 printing)", "Mushrooms and fungi", "Charles McIlvaine (The Bowen-Merrill Company)",
        "toadstoolsmushro00mcil", 1902,
        "Toadstools, mushrooms and fungi, edible and poisonous: the American species described one by one, how to "
        "select and cook the ones its author ate and how to tell the poisonous ones (first published in 1900).",
        note=OLD_MUSHROOM + " McIlvaine was known for eating species almost no one eats today; many he praised are "
                            "now known to make people ill."),
    old("peck_mushrooms_and_their_use_1897", "Mushrooms and their Use (Charles H. Peck, 1897)", "Mushrooms and fungi",
        "Charles H. Peck, New York State Botanist", "mushroomstheirus00peck", 1897,
        "The New York State Botanist's short guide to the common edible mushrooms: how to recognise each, where and "
        "when it grows, and how it was cooked."),
    old("gibson_our_edible_toadstools_1895", "Our Edible Toadstools and Mushrooms and How to Distinguish Them (W. "
        "Hamilton Gibson, 1895)", "Mushrooms and fungi", "W. Hamilton Gibson (Harper and Brothers)",
        "cu31924002064842", 1895,
        "Thirty native mushrooms described by their marked features, with a chapter on the deadly Amanitas and how "
        "to know them."),
    old("hard_mushroom_edible_and_otherwise_1908", "The Mushroom, Edible and Otherwise (Miron E. Hard, 1908)",
        "Mushrooms and fungi", "Miron Elisha Hard (Ohio Library Company)", "mushroomedibleot00harduoft", 1908,
        "A guide to the study of mushrooms of Ohio and the eastern United States, species by species, with their "
        "habitat and time of growth."),
    old("gussow_odell_mushrooms_toadstools_canada_1927", "Mushrooms and Toadstools: the More Common Edible and "
        "Poisonous Fungi of Canada (H. T. Güssow and W. S. Odell, 1927)", "Mushrooms and fungi",
        "Division of Botany, Dominion Experimental Farms (Canada Department of Agriculture)",
        "mushroomstoadsto00gsso", 1927,
        "Canada's Department of Agriculture's account of the commoner edible and poisonous mushrooms of Canada. "
        + NON_US.format(country="Canada"), country="Canada"),
    old("reed_economic_seaweeds_hawaii_1907", "The Economic Seaweeds of Hawaii and their Food Value (Minnie Reed, "
        "1907)", "Seaweeds", "Hawaii Agricultural Experiment Station (Government Printing Office)",
        "cu31924000636989", 1907,
        "The seaweeds (limu) eaten in Hawaii: each kind, where it grows, how it was gathered and prepared, and its "
        "food value.",
        note="Published in {year}: an old report. Seaweed can carry pollution, and some kinds hold much iodine; "
             "gather only from clean water where it is allowed, and follow local rules on harvesting limu."),
]

# ====================================================================== the index

SECTIONS = [
    ("Before you start: the rules that keep foragers alive", "Every wild food has a lookalike. Learn from an expert "
     "in person, start with a few plants, and read the poisonous plant books as closely as the edible ones. "
     + FORAGE_SAFETY, [
         ("key", "plantid:pammel_manual_poisonous_plants", "A Manual of Poisonous Plants (Pammel, 1911)"),
         ("key", "plantid:usfs_celebrating_wildflowers", "The Forest Service's wildflower pages, with ethnobotany "
                                                          "and food plants"),
         ("word", "plant-id", "The plant identification books (request word)"),
         ("link", "Poison Control (US): 1-800-222-1222", "https://www.poison.org/",
          "the National Capital Poison Center's site; call the number at once if someone ate a wild plant or "
          "mushroom")]),
    ("Wild greens, berries, nuts, roots, flowers and seaweeds by region and season", "Spring brings greens and "
     "shoots, summer berries and flowers, autumn nuts, fruit and roots; what grows where depends on the region. "
     "These books describe the plants, where they grow and when.", [
         ("key", "plantid:saunders_useful_wild_plants", "Useful Wild Plants of the United States and Canada "
                                                         "(Saunders, 1920)"),
         ("key", "forage:usda_food_plants_north_american_indians_1936", "Food Plants of the North American Indians "
                                                                         "(USDA, 1936)"),
         ("key", "forage:reed_economic_seaweeds_hawaii_1907", "The Economic Seaweeds of Hawaii (1907)"),
         ("key", "plantid:mathews_field_book_wild_flowers", "Field Book of American Wild Flowers (1902)"),
         ("key", "plantid:sargent_manual_trees_north_america", "Manual of the Trees of North America (1905): nut trees"),
         ("pack", "inat_wild_edibles", "Wild edible plants and their lookalikes from iNaturalist (through GBIF)"),
         ("pack", "commons_wild_food_plants", "Wild greens, berries, nuts, roots, flowers and seaweeds"),
         ("pack", "commons_wild_plants_bark", "Wild carrot, ramsons, elder, nettle, dandelion and blackberry"),
         ("link", "USDA PLANTS Database: each plant's range by state", "https://plants.usda.gov/",
          "public domain facts, but the site is a program-only page; open it in a browser")]),
    ("Mushrooms", "Never eat a wild mushroom unless an expert has confirmed it. Join a mushroom club to learn with "
     "experts. The old books describe mushrooms closely by cap, gills, stem, spore print, smell and habitat, but "
     "their advice on what is edible is out of date.", [
         ("key", "forage:peck_mushrooms_and_their_use_1897", "Mushrooms and their Use (Peck, 1897)"),
         ("key", "forage:gibson_our_edible_toadstools_1895", "Our Edible Toadstools and Mushrooms (Gibson, 1895)"),
         ("key", "forage:hard_mushroom_edible_and_otherwise_1908", "The Mushroom, Edible and Otherwise (Hard, 1908)"),
         ("key", "forage:mcilvaine_one_thousand_american_fungi_1902", "One Thousand American Fungi (McIlvaine, "
                                                                       "1902): read its warnings"),
         ("key", "forage:gussow_odell_mushrooms_toadstools_canada_1927", "Mushrooms and Toadstools of Canada (1927)"),
         ("key", "plantid:atkinson_mushrooms", "Mushrooms: Edible, Poisonous, etc. (Atkinson, 1900)"),
         ("key", "plantid:marshall_mushroom_book", "The Mushroom Book (Marshall)"),
         ("word", "pub:usda_farmers_bulletins", "USDA Farmers' Bulletin 796, Some Common Edible and Poisonous "
                                                "Mushrooms (1917), in the 1910s volume"),
         ("pack", "commons_mushrooms_id", "Deadly and edible mushrooms, each with the expert rule"),
         ("link", "North American Mycological Association: clubs and mushroom poisoning", "https://namyco.org/",
          "copyright; find a local club and its identification experts")]),
    ("Deadly lookalikes", "Each common wild food has a dangerous twin: wild carrot and parsnip with water hemlock and "
     "poison hemlock; ramps and ramsons with lily of the valley and autumn crocus; fiddleheads with bracken; wild "
     "grapes with moonseed; chanterelles with the jack-o'-lantern; morels with false morels; puffballs with young "
     "deadly Amanitas; parasols with the green-spored parasol; honey mushrooms with deadly Galerina.", [
         ("pack", "commons_poisonous_plants", "Poisonous plants and lookalikes, with the poison and skin notes"),
         ("pack", "commons_wild_food_plants", "More lookalikes: autumn crocus, lords-and-ladies, moonseed, "
                                               "bracken, fool's parsley, hemlock water-dropwort"),
         ("key", "pdf:army_atp_3_50_21_survival", "The Army's survival manual: edible and poisonous plants "
                                                  "(ATP 3-50.21)"),
         ("key", "pdf:army_fm_21_76_survival_1992", "Survival (FM 21-76, 1992): plant appendices"),
         ("key", "forage:army_fm_21_76_survival_1957", "Survival (FM 21-76, 1957): the older edition"),
         ("key", "milw:usaf_afh_10_644_sere_2017", "The Air Force's survival handbook (AFH 10-644): plant food")]),
    ("Harvesting ethically and legally", "Ask permission on private land. On public land the rules differ from park "
     "to park and forest to forest: national parks allow gathering only where the park's compendium says so; "
     "national forests may need a free or paid permit for mushrooms, berries or other forest products. Leave "
     "protected and rare plants alone, take only a small share, and never gather from sprayed or polluted ground.", [
         ("key", "forage:nps_gathering_rules", "Gathering in national parks: park rules (NPS)"),
         ("key", "plantid:nisic_invasive_plants", "Invasive plants (many are edible and good to gather)"),
         ("link", "36 CFR 2.1: preservation of natural resources in national parks",
          "https://www.ecfr.gov/current/title-36/chapter-I/part-2/section-2.1",
          "the federal rule each park's compendium follows; open it in a browser"),
         ("link", "US Forest Service: passes and permits (forest products)", "https://www.fs.usda.gov/visit/passes-permits",
          "ask the local ranger district about permits for mushrooms, berries and other forest products"),
         ("link", "US Fish and Wildlife Service: endangered and threatened plants",
          "https://www.fws.gov/program/endangered-species/", "protected species; open it in a browser"),
         ("link", "EPA: pesticides and your health", "https://www.epa.gov/pesticides",
          "why sprayed lawns, roadsides and farm edges are not places to gather food")]),
    ("Preparing and cooking wild food", "Wash wild food well; cook what the sources say must be cooked (fiddleheads, "
     "elderberries, milkweed and wild mushrooms are among those that must never be eaten raw); keep a sample of any "
     "mushroom you cook. Preserve wild food only with tested recipes.", [
         ("word", "cookbooks", "The cookbooks, with the preserving links and kitchen safety"),
         ("word", "outdoor-cooking", "Camp and outdoor cooking and food safety"),
         ("word", "preserving", "Home food preserving: canning, drying, jams and pickles, with the safety rules"),
         ("key", "outcook:usfs_camping_food_bears", "Food in camp and bear safety (US Forest Service)")]),
    ("Foraging by touch, smell and texture (low vision)", "The old field guides describe plants and mushrooms in "
     "words: leaf shape and edge, hairs, bark, the feel of a cap or stem, and smell. They can help a forager who "
     "cannot see, but a touch or smell key is never enough on its own: go with a sighted expert who confirms every "
     "find. Never touch poison ivy, giant hogweed or wild parsnip (their sap burns skin), wear gloves for nettles, and "
     "never taste to identify.", [
         ("key", "plantid:dana_how_to_know_wild_flowers", "How to Know the Wild Flowers (Dana): flowers in words"),
         ("key", "plantid:keeler_our_native_trees", "Our Native Trees (Keeler): bark, leaves and fruit in words"),
         ("key", "forage:gibson_our_edible_toadstools_1895", "Gibson's mushrooms by their marked features"),
         ("pack", "commons_wild_plants_bark", "Tree bark textures, also told by touch"),
         ("manuals", "plant_id", "Plant identification guides, hand lenses and apps (makers' pages as links)"),
         ("word", "vision-living", "Blind and low-vision living books")]),
    ("Foraging outside the United States", "Laws and species differ by country.", [
        ("key", "forage:fsa_safe_foraging_uk", "Guidance for safe foraging (UK Food Standards Agency)"),
        ("key", "forage:gussow_odell_mushrooms_toadstools_canada_1927", "Mushrooms and Toadstools of Canada (1927)"),
        ("link", "New Zealand Ministry for Primary Industries: hunting and gathering wild food",
         "https://www.mpi.govt.nz/outdoor-activities/hunting-and-gathering-biosecurity-and-food-safety/",
         "its reuse terms could not be read from its site; open it in a browser"),
        ("link", "Health Canada: food safety", "https://www.canada.ca/en/health-canada/services/general-food-safety-tips.html",
         "non-commercial terms and not reachable by the builder; open it in a browser"),
        ("link", "NSW Food Authority (Australia): wild mushrooms", "https://www.foodauthority.nsw.gov.au/",
         "its reuse terms were not confirmed; open it in a browser")]),
    ("Modern foraging books (links only)", "In copyright: borrow them from a library or buy them.", [
        ("link", "Lee Allen Peterson, A Field Guide to Edible Wild Plants (Peterson)",
         "https://openlibrary.org/search?q=field+guide+to+edible+wild+plants", "copyright; Open Library's catalogue"),
        ("link", "Samuel Thayer, The Forager's Harvest and Nature's Garden",
         "https://openlibrary.org/search?q=samuel+thayer", "copyright; Open Library's catalogue"),
        ("link", "Euell Gibbons, Stalking the Wild Asparagus", "https://openlibrary.org/search?q=euell+gibbons",
         "copyright; Open Library's catalogue"),
        ("link", "Lee Allen Peterson's and David Arora's mushroom guides (Mushrooms Demystified)",
         "https://openlibrary.org/search?q=mushrooms+demystified", "copyright; Open Library's catalogue")]),
]
INDEX = X.index_maker("forage", GROUP, "Foraging and edible wild plants: a guide to the library",
                      "Edible wild plants and foraging",
                      "A guide to foraging in the library: wild greens, berries, nuts, roots, flowers and seaweeds, "
                      "mushrooms, deadly lookalikes, harvesting ethically and legally, preparing wild food, foraging "
                      "by touch and smell, foraging abroad, and the modern books as links.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("forage", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"foraging": lambda: ["forage:index"] + [f"forage:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "forage_nps": "www.nps.gov/aboutus/disclaimer.htm (checked at every build): NPS material \"is generally considered "
                  "in the public domain\", credited in the notice; NPS's robots.txt allows the park pages (checked "
                  "2026-11-22).",
    "forage_govuk": "www.gov.uk/help/terms-conditions (checked at every build): GOV.UK content is under the Open "
                    "Government Licence v3.0, credited in the notice; robots.txt allows the page and has no rule for "
                    "our reader (checked 2026-11-22).",
    "forage_us_pdfs": "Food Plants of the North American Indians (USDA, 1936) and FM 21-76 (US Army, 1957): works of the "
                      "US government read from the Internet Archive; the Army manual follows the release rule.",
    "forage_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, so "
                        "a later reprint is refused); archive.org's robots.txt allows the files (2026-11-22).",
    "forage_index": "The index (forage:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Edible Wild Plants (Oliver Perry Medsger, 1939)", "Published in 1939 and its copyright was renewed (Stanford "
     "Copyright Renewal Database, renewal R398297, checked 2026-11-22): still in copyright. Link-only. Index: "
     "https://openlibrary.org/search?q=medsger+edible+wild+plants"),
    ("Edible Wild Plants of Eastern North America (Fernald and Kinsey, 1943)", "Its copyright was renewed (Stanford "
     "Copyright Renewal Database, renewal RE291877, checked 2026-11-22). Link-only. Index: "
     "https://openlibrary.org/search?q=edible+wild+plants+of+eastern+north+america"),
    ("Euell Gibbons, Samuel Thayer, Lee Allen Peterson, David Arora and other modern foraging books", "Copyright of "
     "their authors; link-only from the index (forage:index). Index: https://openlibrary.org/search?q=foraging"),
    ("USDA PLANTS Database", "Public domain facts, but plants.usda.gov is a program-only page with no plain pages to "
     "read; link-only from the index. Index: https://plants.usda.gov/"),
    ("iNaturalist species pages", "iNaturalist's website says \"ai-train=no\" and is never read; its open pictures "
     "come only through GBIF and the iNaturalist open-data bucket (the inat_wild_edibles picture pack). Index: "
     "https://www.gbif.org/dataset/50c9509d-22c7-4a22-a47d-8c48425ef4a7"),
    ("University extension foraging guides (Penn State, Minnesota, Wisconsin, Maine and others)", "Each university's "
     "copyright, or CC BY-NC terms for some; none was confirmed open one by one, so they are link-only for the "
     "owner to fetch with Program Downloader. Index: https://extension.psu.edu/ and https://extension.umn.edu/"),
    ("New Zealand Ministry for Primary Industries wild food pages", "Its copyright page could not be read by the "
     "builder (the text is loaded by the page's own program), so its reuse terms were not confirmed. Link-only. "
     "Index: https://www.mpi.govt.nz/outdoor-activities/hunting-and-gathering-biosecurity-and-food-safety/"),
    ("Health Canada and provincial wild mushroom and foraging pages", "canada.ca's web pages may be reproduced for "
     "non-commercial use only unless open.canada.ca lists them under the Open Government Licence - Canada, and "
     "open.canada.ca lists no wild mushroom or foraging page (searched 2026-11-22); canada.ca could not be reached "
     "from the build machine either. Link-only. Index: "
     "https://www.canada.ca/en/health-canada/services/general-food-safety-tips.html"),
    ("Project Gutenberg copies of McIlvaine, Hard and Gibson", "The same works are built from the Internet Archive's "
     "scans here; Project Gutenberg is in the Kiwix library. Index: https://www.gutenberg.org/ebooks/51393"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
