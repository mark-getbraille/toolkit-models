"""Home food preserving for the reference library, in the group "Reference, home food preserving" (the owner's request
of 2026-11-22). Keys: preserving (every book), preserve:<name>.

A sibling of cookbooks.py (cook:, "Reference, cookbooks and recipes"), which already has the National Center for Home
Food Preservation's tested recipes as links (cook:nchfp_preserving_links), three old preserving books (Everywoman's
Canning Book 1918, Preservation of Food 1919, the 1917 Home Drying Manual), meat curing and the fish smokehouse; and of
outdoor_cooking.py (outcook:, smokers and food safety in a power cut). The USDA Complete Guide to Home Canning is in the
Kiwix library (usda-2015_en). This module LINKS all of those and adds what they lack.

What this module builds, in plain words:
  - preserve:index, a guide to home food preserving in the library (the toolkit's own facts and links, CC0), one page
    per part: canning in a boiling-water canner and a pressure canner, pickling, jams and jellies, freezing, drying
    and dehydrating, fermenting, curing and smoking, root cellars and storage, botulism and safety, altitude
    adjustments, equipment, the old books (historical only), extension services (links) and sources outside the US;
  - IN FULL, works of governments:
      CDC's botulism pages, every page (what botulism is, its symptoms, home-canned foods as its commonest cause in
      the US, and how to prevent it), kept whole under CDC's terms;
      the UK Food Standards Agency's Consumer advice for food preservation at home and its Botulism (Clostridium
      botulinum) guidance (GOV.UK, Open Government Licence v3.0, a non-US source);
      the USDA's Reliable Methods of Home Canning (1930 radio talk) and the US Food Administration's Preserving
      Vegetables by Salting, Drying and Storing (1918), as history;
  - old books, kept as HISTORY ONLY (published before 1931; the builder checks each item's year on the Internet
    Archive at every build): George Washington Carver's The Canning and Preserving of Fruits and Vegetables in the
    Home (Tuskegee, 1912), Ola Powell's Successful Canning and Preserving (1917), Janet McKenzie Hill's Canning,
    Preserving and Jelly Making (1915), Theodora Carrell's A Manual of Canning and Preserving (1919), Emily
    Riesenberg's Preserving at Home (1921), A. Louise Andrea's Dehydrating Foods (1920), the National War Garden
    Commission's Home Canning and Drying of Vegetables and Fruits (1918), the North Carolina Department of
    Agriculture's Canning and Preserving (1907) and Eduard Wagner's Recipes for the Preserving of Fruit, Vegetables
    and Meat (1908); and the Kerr Home Canning Book (Kerr Glass Manufacturing, 1945), published after 1930 but
    whose copyright was not renewed (no renewal in the Stanford Copyright Renewal Database, searched 2026-11-22).
  Every book carries PRESERVE_SAFETY in its notice (tested current recipes, low-acid foods in a pressure canner,
  botulism signs and 911, altitude adjustments); every old book also carries OLD_PRESERVE (open-kettle and oven
  canning, paraffin seals, boiling-water canning of vegetables and meat, old preservatives: no longer safe).

Not built (NOT_INCLUDED, link-only): the modern Ball Blue Book (Newell Brands copyright); the Ball Blue Book and Kerr
editions published before 1931 (none was found as a downloadable copy: the Internet Archive's Ball Blue Books are
1963 and later, lending-library copies, and HathiTrust refuses programs); the NCHFP's text (All rights reserved);
the extension services' guides (each university's copyright or non-commercial terms); Health Canada (non-commercial
and not reachable); FAO's processing manuals (per-document terms not confirmed); the USDA Complete Guide (in Kiwix).

Run from the repository's folder:
  python3 textbooks/preserving.py preserve:fsa_food_preservation_uk --out build/textbooks --limit 3
  python3 textbooks/preserving.py --list preserving
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import foraging as F  # noqa: E402  (the shared GOV.UK licence names)
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402
from old_ia_books import old_book, OLD_CHANGES  # noqa: E402

GROUP = "preserving"
GROUPS = {GROUP: "Reference, home food preserving"}

# The safety notice every book carries (packs/foraging_preserving_packs.py PRESERVE_NOTE says the same for a picture).
PRESERVE_SAFETY = ("Home preserving safety: follow tested, current recipes and methods exactly, such as the USDA "
                   "Complete Guide to Home Canning (in the Kiwix library) and the National Center for Home Food "
                   "Preservation (nchfp.uga.edu); do not invent or change canning recipes. Low-acid foods "
                   "(vegetables, meat, poultry, fish, beans and soups) must be processed in a pressure canner, never "
                   "a boiling-water bath, or they can cause botulism, which can kill. Adjust for altitude: above "
                   "1,000 feet, add processing time for a boiling-water canner and raise the pressure for a pressure "
                   "canner, exactly as the tested recipe's altitude table says. Throw away, without tasting, any jar "
                   "or can that is bulging, leaking, spurting, mouldy, foul-smelling or has a broken seal. Botulism "
                   "signs include double or blurred vision, drooping eyelids, slurred speech, trouble swallowing or "
                   "breathing and muscle weakness: call 911 at once.")
OLD_PRESERVE = ("Published in {year}: kept as HISTORY ONLY. Its methods are no longer considered safe: open-kettle "
                "canning, oven canning, sealing jars with paraffin wax, canning vegetables, meat or fish in a "
                "boiling-water bath, its processing times, and preservatives now banned (such as borax and salicylic "
                "acid). Follow current USDA guidance instead.")
NON_US = F.NON_US

# Works published 1931 to 1963 whose copyright was not renewed (evidence given in each entry's notice).
NOT_RENEWED = "Public domain (US: published 1931 to 1963, copyright not renewed)"
NOT_RENEWED_URL = "https://www.copyright.gov/circs/circ15a.pdf"
ALLOWED = {NOT_RENEWED: "open"}

# ====================================================================== CDC

GUIDES = [
    X.cdc_site_book(GROUP, "cdc_botulism", "Botulism: home-canned foods, symptoms and prevention (CDC)", "Botulism",
                    ["botulism"],
                    "CDC's botulism pages, every page: what botulism is, its kinds (foodborne, infant, wound), its "
                    "signs and symptoms, how it is treated, home-canned foods (low-acid vegetables) as the most "
                    "common cause of foodborne botulism outbreaks in the US, preventing botulism from home-canned, "
                    "fermented and stored foods, and CDC's fact sheets.", PRESERVE_SAFETY,
                    units=[(r"prevention", "Prevention and home canning"), (r"signs|symptom", "Signs and symptoms"),
                           (r".", "Botulism")]),
]

# ====================================================================== UK Food Standards Agency (GOV.UK, OGL)

FSA_PAGES = ["https://www.gov.uk/guidance/consumer-advice-for-food-preservation-at-home",
             "https://www.gov.uk/government/publications/botulism-clostridium-botulinum/botulism-clostridium-botulinum"]
GUIDES.append(dict(X.page_list_book(
    GROUP, "fsa_food_preservation_uk", "Food preservation at home and botulism (UK Food Standards Agency)",
    "Home food preserving safety", "Food Standards Agency (United Kingdom), on GOV.UK", FSA_PAGES,
    r"^https://www\.gov\.uk/(guidance/consumer-advice-for-food-preservation-at-home|government/publications/"
    r"botulism-clostridium-botulinum/botulism-clostridium-botulinum)$",
    "The UK Food Standards Agency's consumer advice on preserving food at home (the food safety risks, what food "
    "preservation is, how to preserve food safely: canning, bottling, pickling, fermenting, drying, curing and "
    "smoking, infused oils) and its guidance on botulism (Clostridium botulinum): where it comes from, the foods at "
    "risk and how it is controlled.",
    "Contains public sector information licensed under the Open Government Licence v3.0 (Food Standards Agency, "
    "GOV.UK). " + NON_US.format(country="the United Kingdom") + " " + PRESERVE_SAFETY,
    units=[(r"botulism", "Botulism"), (r".", "Preserving food at home")]),
    country="United Kingdom", licence="OGL-UK-3.0", licence_url=F.OGL_URL, licence_page=F.GOVUK_TERMS,
    licence_text=F.GOVUK_TEXT))

# ====================================================================== the old books (history only)


def old(name, title, subject, publisher, archive, year, description):
    """One old public-domain preserving book of the Internet Archive, kept as history, with both safety notes."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=OLD_PRESERVE,
                    notice=PRESERVE_SAFETY)


PDFS = [
    K.us_pdf(GROUP, name="usda_reliable_methods_home_canning_1930", title="Reliable Methods of Home Canning (USDA "
             "Bureau of Home Economics, 1930)", subject="Home canning (history)",
             publisher="US Department of Agriculture, Bureau of Home Economics (Radio Service)",
             archive="reliablemethodso1930unit", published="1930",
             version="1930 edition (Internet Archive item reliablemethodso1930unit)",
             description="A USDA radio talk of 1930 on home canning methods, from the Housekeepers' Chat series. "
                         + OLD_PRESERVE.format(year=1930),
             notice="A work of the US Department of Agriculture (public domain), read from the National Agricultural "
                    "Library's scan on the Internet Archive. " + PRESERVE_SAFETY),
    old("food_administration_salting_drying_storing_1918", "Preserving Vegetables by Salting, Drying, and Storing (US "
        "Food Administration, 1918)", "Salting, drying and storing (history)", "US Food Administration, Division of "
        "Home Conservation (Government Printing Office)", "cu31924003570318", 1918,
        "A wartime US government booklet on keeping vegetables by salting (brining and fermenting), drying and "
        "storing them in cellars, pits and storage rooms."),
    old("carver_canning_preserving_1912", "The Canning and Preserving of Fruits and Vegetables in the Home (George W. "
        "Carver, 1912)", "Home canning (history)", "George Washington Carver (Tuskegee Normal and Industrial "
        "Institute)", "canningpreservin00carv", 1912,
        "George Washington Carver's Tuskegee bulletin for farm families on canning and preserving fruits and "
        "vegetables at home."),
    old("powell_successful_canning_preserving_1917", "Successful Canning and Preserving (Ola Powell, 1917)",
        "Home canning (history)", "Ola Powell (J. B. Lippincott)", "successfulcannin00powe", 1917,
        "A practical handbook for schools, canning clubs and homes: canning fruits and vegetables, jellies, "
        "preserves, pickles, drying and the canning club work of its day."),
    old("hill_canning_preserving_jelly_1915", "Canning, Preserving and Jelly Making (Janet McKenzie Hill, 1915)",
        "Jams, jellies and preserves (history)", "Janet McKenzie Hill (Little, Brown)", "cu31924001742059", 1915,
        "Canning, preserves, jams, marmalades, jellies, fruit butters, pickles and relishes."),
    old("carrell_manual_canning_preserving_1919", "A Manual of Canning and Preserving (Theodora M. Carrell, 1919)",
        "Home canning (history)", "Theodora M. Carrell (E. P. Dutton)", "manualofcanningp00carr", 1919,
        "A home manual of canning, preserving, jelly making, pickling and drying."),
    old("riesenberg_preserving_at_home_1921", "Preserving at Home (Emily Riesenberg, 1921)", "Home preserving (history)",
        "Emily Riesenberg (Rand McNally)", "preservingathome00ries", 1921,
        "A book for the home economist on canning, preserving, pickling and drying."),
    old("andrea_dehydrating_foods_1920", "Dehydrating Foods: Fruits, Vegetables, Fish and Meats (A. Louise Andrea, "
        "1920)", "Drying and dehydrating (history)", "A. Louise Andrea (The Cornhill Company)",
        "dehydratingfoods00andr_0", 1920,
        "Drying fruits, vegetables, fish and meat at home, with recipes for cooking dried foods."),
    old("war_garden_home_canning_drying_1918", "Home Canning and Drying of Vegetables and Fruits (National War Garden "
        "Commission, 1918)", "Home canning and drying (history)", "National War Garden Commission",
        "homecanningdryin00nati", 1918,
        "The wartime commission's manual of canning and drying, with jellies, fruit butters, fermenting, salting "
        "and pickling."),
    old("north_carolina_canning_preserving_1907", "Canning and Preserving (North Carolina Department of Agriculture, "
        "1907)", "Home canning (history)", "North Carolina Department of Agriculture", "canningpreservin00nort", 1907,
        "A state bulletin on canning and preserving fruits and vegetables at home."),
    old("wagner_recipes_preserving_1908", "Recipes for the Preserving of Fruit, Vegetables and Meat (Eduard Wagner, "
        "1908)", "Home preserving (history)", "Eduard Wagner (Scott, Greenwood; Van Nostrand)",
        "recipesforpreser00wagnrich", 1908,
        "A translated German handbook of preserving fruit, vegetables and meat: drying, salting, smoking, sugaring, "
        "vinegar, sterilising and the chemical preservatives of its day."),
    dict(group=GROUP, name="kerr_home_canning_book_1945", title="Kerr Home Canning Book (Kerr Glass Manufacturing "
         "Corporation, 1945)", subject="Home canning (history)",
         publisher="Kerr Glass Manufacturing Corporation (prepared by Zella Hale Weyant)", archive="CAT11013959",
         country="United States", licence=NOT_RENEWED, licence_url=NOT_RENEWED_URL, level="reference",
         published="1945", version="1945 edition (Internet Archive item CAT11013959, National Agricultural Library)",
         description="Kerr's wartime home canning book: jars and lids, canning fruits, tomatoes, vegetables and "
                     "meats, jellies, preserves and pickles. " + OLD_PRESERVE.format(year=1945),
         notice="Published in 1945. Its copyright was not renewed: no renewal of the Kerr Home Canning Book is listed "
                "in the Stanford Copyright Renewal Database (searched 2026-11-22), and the National Agricultural "
                "Library, which holds the copy, \"believes that this item is not in copyright\". Read from its "
                "Internet Archive scan: the machine-read text has the scanner's mistakes. Kerr is a trademark of its "
                "owner; this old book is not endorsed by it. " + PRESERVE_SAFETY,
         changes=OLD_CHANGES),
]

# ====================================================================== the index

KIWIX_USDA = ("link", "USDA Complete Guide to Home Canning (2015)", "https://library.kiwix.org/#lang=eng&q=usda",
              "public domain: in the toolkit's Kiwix library as \"USDA Guide to Home Canning\" (usda-2015_en); the "
              "tested methods and processing times: use it for all canning")
NCHFP_LINK = ("link", "National Center for Home Food Preservation (University of Georgia)", "https://nchfp.uga.edu/",
              "All rights reserved; its tested recipes are listed by name and address in the cookbooks "
              "(cook:nchfp_preserving_links)")
SECTIONS = [
    ("Start here: botulism and the safe way to preserve", PRESERVE_SAFETY, [
        ("key", "preserve:cdc_botulism", "Botulism: home-canned foods, symptoms and prevention (CDC)"),
        ("key", "preserve:fsa_food_preservation_uk", "Food preservation at home and botulism (UK Food Standards "
                                                     "Agency)"),
        KIWIX_USDA, NCHFP_LINK]),
    ("Canning: boiling-water and pressure canners", "High-acid foods (most fruits, jams and jellies, pickles, and "
     "tomatoes with added acid) go in a boiling-water canner; low-acid foods (vegetables, meat, poultry, fish, beans) "
     "only in a pressure canner, with the tested recipe's time and pressure for your altitude. Have a dial gauge "
     "tested every year.", [
         KIWIX_USDA, NCHFP_LINK,
         ("manuals", "canning_preserving", "Pressure canners, water-bath and steam canners: the makers' manuals "
                                            "(links) and USDA's guides"),
         ("pack", "commons_home_preserving", "Canning jars, lids and canners, for the picture describer")]),
    ("Pickling, fermenting, jams and jellies", "Use tested recipes: the acid, salt and sugar in them are part of "
     "what makes them safe. Use canning or pickling salt and vinegar of 5 per cent acidity when the recipe says so.", [
         ("word", "cookbooks", "The cookbooks: the NCHFP's pickling, fermenting and jam recipes as links, and "
                               "Everywoman's Canning Book (1918) and Preservation of Food (1919) as history"),
         ("key", "preserve:hill_canning_preserving_jelly_1915", "Canning, Preserving and Jelly Making (Hill, 1915), "
                                                                "history only"),
         ("key", "preserve:food_administration_salting_drying_storing_1918", "Salting (brining and fermenting) "
                                                                             "vegetables (1918), history only"),
         ("pack", "commons_home_preserving", "Pickles, sauerkraut, kimchi, jams and jellies")]),
    ("Freezing", "Freeze at 0 F (-18 C) or colder; blanch vegetables first as tested directions say; thaw in the "
     "fridge. A full freezer keeps food frozen about 48 hours in a power cut if the door stays shut.", [
         ("key", "outcook:cdc_food_power_outage", "Food safety in a power outage (CDC)"),
         ("key", "outcook:ready_food_water_power", "Emergency food, water and power outages (Ready.gov)"),
         KIWIX_USDA]),
    ("Drying and dehydrating", "Dry fruit, vegetables and herbs as tested directions say; for jerky, heat meat to "
     "160 F (poultry 165 F) before or after drying, as the cookbooks' smoking notice says.", [
         ("key", "preserve:andrea_dehydrating_foods_1920", "Dehydrating Foods (Andrea, 1920), history only"),
         ("key", "preserve:war_garden_home_canning_drying_1918", "Home Canning and Drying (1918), history only"),
         ("manuals", "canning_preserving", "Food dehydrators and freeze dryers: makers' manuals as links"),
         ("pack", "commons_home_preserving", "Dried fruit, jerky and food dehydrators")]),
    ("Curing and smoking", "Curing needs exact amounts of curing salt and cold temperatures; smoked meat is cooked to "
     "safe temperatures. These are in the cookbooks and outdoor cooking books.", [
         ("word", "cookbooks", "The cookbooks: curing, sausage and smoking (Secrets of Meat Curing, 1922; the fish "
                               "smokehouse, 1918) with their safety notices"),
         ("word", "outdoor-cooking", "Smokers and grills, with carbon monoxide and food temperature safety"),
         ("pack", "commons_grills_smokers", "Smokers and smokehouses")]),
    ("Root cellars and storage", "Cool, dark, humid and ventilated storage keeps potatoes, roots, apples and cabbage "
     "for months; keep stored food away from fuel and chemicals and check it often.", [
         ("key", "preserve:food_administration_salting_drying_storing_1918", "Storing vegetables in cellars, pits "
                                                                             "and storage rooms (1918)"),
         ("word", "pub:usda_farmers_bulletins", "USDA Farmers' Bulletins: Home Storage of Vegetables (Bulletin "
                                                "879, 1917) and the canning and drying bulletins, by decade"),
         ("word", "homestead", "Homesteading books"),
         ("pack", "commons_home_preserving", "Root cellars and storage")]),
    ("Altitude adjustments", "Water boils at a lower temperature higher up, so processing changes above 1,000 feet: "
     "longer times in a boiling-water canner and more pressure in a pressure canner. Use the altitude table in the "
     "tested recipe or the USDA guide; your county extension office can tell you your altitude.", [
         KIWIX_USDA, NCHFP_LINK]),
    ("Old preserving books (history only)", "These old books show how people preserved food in their day. Their "
     "methods are NOT safe to follow: open-kettle and oven canning, paraffin seals, water-bath canning of "
     "vegetables and meat, and old preservatives have all been given up. The Ball Blue Book and Kerr books of "
     "today are copyright; no Ball Blue Book published before 1931 was found as a downloadable copy.", [
         ("key", "preserve:carver_canning_preserving_1912", "Carver (Tuskegee, 1912)"),
         ("key", "preserve:powell_successful_canning_preserving_1917", "Successful Canning and Preserving (Powell, "
                                                                       "1917)"),
         ("key", "preserve:carrell_manual_canning_preserving_1919", "A Manual of Canning and Preserving (1919)"),
         ("key", "preserve:riesenberg_preserving_at_home_1921", "Preserving at Home (1921)"),
         ("key", "preserve:north_carolina_canning_preserving_1907", "Canning and Preserving (North Carolina, 1907)"),
         ("key", "preserve:wagner_recipes_preserving_1908", "Recipes for the Preserving of Fruit, Vegetables and "
                                                            "Meat (1908)"),
         ("key", "preserve:usda_reliable_methods_home_canning_1930", "Reliable Methods of Home Canning (USDA, 1930)"),
         ("key", "preserve:kerr_home_canning_book_1945", "Kerr Home Canning Book (1945; copyright not renewed)"),
         ("link", "Ball Blue Book (current edition)", "https://www.ballmasonjars.com/",
          "Newell Brands copyright; buy it or borrow it from a library")]),
    ("Extension services (links only)", "Each state's extension service teaches tested home preserving and tests "
     "dial gauges. Their guides are each university's copyright (some non-commercial).", [
         ("link", "Utah State University Extension: Preserve the Harvest", "https://extension.usu.edu/preserve-the-harvest/",
          "copyright of the university; open it in a browser"),
         ("link", "Oregon State University Extension: food preservation", "https://extension.oregonstate.edu/food/preservation",
          "copyright of the university; open it in a browser"),
         ("link", "University of Wisconsin Extension: Safe and Healthy Food Preserving",
          "https://fyi.extension.wisc.edu/safepreserving/", "copyright of the university; open it in a browser"),
         ("link", "Penn State Extension: home food preservation", "https://extension.psu.edu/",
          "copyright of the university; search its site for home food preservation"),
         ("link", "University of Minnesota Extension: food preservation", "https://extension.umn.edu/",
          "copyright of the Regents; search its site for preserving"),
         ("link", "Clemson Home and Garden Information Center: food preservation", "https://hgic.clemson.edu/",
          "copyright of Clemson University; open it in a browser")]),
    ("Outside the United States", "Measures, jars and rules differ by country.", [
        ("key", "preserve:fsa_food_preservation_uk", "Food preservation at home (UK Food Standards Agency, OGL)"),
        ("link", "Health Canada: home canning safety",
         "https://www.canada.ca/en/health-canada/services/general-food-safety-tips/home-canning-safety.html",
         "non-commercial terms, not reachable by the builder; open it in a browser"),
        ("link", "Food Standards Australia New Zealand: food safety", "https://www.foodstandards.gov.au/consumer/safety",
         "its reuse terms were not confirmed; open it in a browser"),
        ("link", "FAO (UN Food and Agriculture Organization): food processing manuals", "https://openknowledge.fao.org/",
         "newer FAO documents are CC BY-NC-SA 3.0 IGO (personal use), older ones all rights reserved; not checked "
         "one by one")]),
]
INDEX = X.index_maker("preserve", GROUP, "Home food preserving: a guide to the library", "Home food preserving",
                      "A guide to home food preserving in the library: canning, pickling, jams and jellies, freezing, "
                      "drying, fermenting, curing and smoking, root cellars, botulism and safety, altitude, "
                      "equipment, the old books as history, and the extension services as links.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("preserve", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"preserving": lambda: ["preserve:index"] + [f"preserve:{g['name']}"
                                                                             for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "preserve_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                    "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on CDC's "
                    "site), met in the notice; the pages are kept whole.",
    "preserve_govuk": "www.gov.uk/help/terms-conditions (checked at every build): the Food Standards Agency's GOV.UK "
                      "pages are under the Open Government Licence v3.0, credited in the notice.",
    "preserve_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build, "
                          "so a later reprint is refused); the USDA's 1930 talk is also a US government work.",
    "preserve_kerr_1945": "Kerr Home Canning Book (1945): published after 1930, and no renewal of it is listed in the "
                          "Stanford Copyright Renewal Database (exhibits.stanford.edu/copyrightrenewals, which covers "
                          "the renewals of books of 1923 to 1963; searched for \"kerr\", \"home canning\" and "
                          "\"canning book\" on 2026-11-22), so it is in the US public domain.",
    "preserve_index": "The index (preserve:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Ball Blue Book (modern editions)", "Newell Brands copyright (the 1963 and later editions on the Internet Archive "
     "are lending-library copies; the 1940s to 1960s editions' renewals are listed in the Stanford Copyright Renewal "
     "Database). Link-only. Index: https://www.ballmasonjars.com/"),
    ("Ball Blue Book and Ball recipe books published before 1931", "Public domain in the US, but no downloadable copy "
     "was found: the Internet Archive has none before 1963 (its \"Ball Blue Book of Canning and Preserving Recipes\" "
     "is an undated modern reprint) and HathiTrust refuses programs (checked 2026-11-22). Could be added when a copy "
     "is found. Index: https://archive.org/search?query=%22ball+blue+book%22"),
    ("Kerr Home Canning Book editions before 1931", "None found as a downloadable copy (the Internet Archive's are 1944 "
     "and later); the 1945 edition is built (copyright not renewed). Index: "
     "https://archive.org/search?query=%22kerr+home+canning%22"),
    ("Kerr Home Canning Book, 1944 and 1958 copies", "The 1944 copy is a user upload whose year the builder cannot "
     "confirm and the 1958 copy is a later edition; the 1945 National Agricultural Library copy is built instead. "
     "Index: https://archive.org/details/canning_202309"),
    ("National Center for Home Food Preservation recipes and So Easy to Preserve", "\"All rights reserved\" "
     "(University of Georgia); its recipes are listed as links in cook:nchfp_preserving_links. Index: "
     "https://nchfp.uga.edu/"),
    ("USDA Complete Guide to Home Canning", "Already in the Kiwix library (usda-2015_en), so it is not built again; "
     "the manual collection canning_preserving also lists the Internet Archive's copy. Index: "
     "https://archive.org/details/usda-complete-guide-to-home-canning-2015-revision"),
    ("University extension preserving guides (Penn State, Utah State, Oregon State, Wisconsin, Minnesota, Clemson and "
     "others)", "Each university's copyright, some non-commercial (CC BY-NC or \"educational use\"); none was "
     "confirmed open one by one, so they are link-only from the index. Index: https://extension.usu.edu/"
     "preserve-the-harvest/"),
    ("Health Canada: Home canning and bottling of seafood, and its home canning safety page", "open.canada.ca lists "
     "the seafood page under the Open Government Licence - Canada (record 50364239-21ee-455d-a894-c1fcf757aa62, "
     "checked 2026-11-22), so it could be built in full, but canada.ca's web pages could not be reached from the "
     "build machine (no answer, 2026-11-22); its other home canning web pages are non-commercial only. Link-only "
     "for now. Index: https://www.canada.ca/en/health-canada/services/meat-poultry-fish-seafood-safety/"
     "home-canning-bottling-seafood.html"),
    ("Food Standards Australia New Zealand", "Its reuse terms were not confirmed in this pass. Link-only. Index: "
     "https://www.foodstandards.gov.au/"),
    ("FAO home food processing manuals", "Newer FAO documents are CC BY-NC-SA 3.0 IGO (personal use), older ones "
     "\"all rights reserved\" with educational reproduction allowed; not checked one by one. Index: "
     "https://openknowledge.fao.org/"),
    ("USDA FSIS and FoodSafety.gov canning and botulism pages", "Public domain, but both refuse programs (403). "
     "Link-only. Index: https://www.fsis.usda.gov/food-safety/foodborne-illness-and-disease/illnesses-and-pathogens/"
     "botulism"),
    ("USDA Farmers' Bulletins on canning, drying and storage (853, 1211, 841, 984, 879)", "Already in the library by "
     "decade (pub:usda_farmers_bulletins); not built again. Index: https://archive.org/details/usda-farmersbulletin"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
