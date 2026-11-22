"""Hunting and fishing food for the reference library, in its own group "Reference, game and fish processing" (the
owner's request of 2026-11-22): field dressing, transporting and processing game, game meat food safety, chronic
wasting disease, cleaning and cooking fish, and fish consumption advice. Keys: game-fish (every book),
gamefish:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - CDC's pages on diseases hunters can get from wild game, every page, kept whole as CDC's terms ask: chronic
    wasting disease (what it is, where it is found, and CDC's advice to hunters: do not shoot or eat an animal that
    looks sick, wear gloves when field dressing, have deer, elk and moose tested where the disease is found, and do
    not eat meat from an animal that tests positive), brucellosis (from feral swine, elk and bison), trichinellosis
    (from undercooked bear, wild boar and other wild game meat) and tularemia (from rabbits and other animals);
  - USDA APHIS's chronic wasting disease pages: the disease, where it is found, the herd certification programme
    and the questions and answers;
  - the USGS National Wildlife Health Center's chronic wasting disease page (the science, its spread, and the
    distribution maps described in words);
  - the FDA's advice about eating fish (which fish to choose, how often, and for those who are or may become
    pregnant, nursing mothers and children) with its questions and answers;
  - the EPA's pages on choosing fish and shellfish wisely: eating fish the healthy way, the EPA-FDA advice, whether
    fish you caught might be contaminated, and the state and tribal fish advisory contacts (personal use only: EPA's
    non-commercial terms);
  - gamefish:index, a guide to game and fish in the library: field dressing and transporting game, processing and
    preserving meat (the cookbooks' smoking and curing books, linked), hunting and fishing rules, fish advisories,
    and the firearms safety notes.

Already in the library and linked, not repeated: the hunting and fishing pages of the Fish and Wildlife Service and
the Forest Service, NOAA's fish species directory (outdoors:), the old smokehouse and meat curing books and the home
canning links (cook:), and the camp food safety books (outcook:).

Every book's notice ends with the game safety note: wear gloves and keep meat cold; never eat meat from an animal
that looked sick or that tests positive for chronic wasting disease; cook game with a food thermometer; check your
state's fish advisories before eating fish you caught; and for hunters the firearm line used everywhere in the
toolkit (treat every gun as loaded, and keep your fingers away from the trigger), with hunter education and blaze
orange.

Not built (NOT_INCLUDED, link-only): USDA FSIS's game and fish food safety pages (fsis.usda.gov refuses programs),
state wildlife agencies' field dressing and CWD testing guides (each state's own site and terms), university
extension game processing guides (copyright or non-commercial), and hunter education courses (copyright).

Licences: CDC's terms, FDA's website policy and the EPA's copyright statement are checked at every build; APHIS and
USGS pages are works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page).

Run from the repository's folder:
  python3 textbooks/game_fish.py gamefish:fda_advice_eating_fish --out build/textbooks
  python3 textbooks/game_fish.py --list game-fish
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared CDC book helper
import practical_index as X  # noqa: E402 - the index maker, page lists and the EPA's terms
from outdoors import GUN_LINE  # noqa: E402 - the firearm line used everywhere in the toolkit

GROUP = "gamefish"
GROUPS = {GROUP: "Reference, game and fish processing"}
NOTE = ("Safety: wear gloves when field dressing, and keep meat and fish cold. Never eat meat from an animal that "
        "looked sick, or that tests positive for chronic wasting disease. Cook game meat thoroughly, checked with a "
        "food thermometer. Check your state's fish advisories before eating fish you caught. Hunters: take a hunter "
        "education course, wear blaze orange, identify your target and what is beyond it, and follow your state's "
        "rules. " + GUN_LINE)

FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FDA_FISH = [FDA + "/food/consumers/" + p for p in (
    "advice-about-eating-fish", "questions-answers-fdaepa-advice-about-eating-fish-those-who-might-become-or-are-"
    "pregnant-or", "resources-use-fdaepas-fish-advice")]
EPA_FISH = "https://www.epa.gov/choose-fish-and-shellfish-wisely"
EPA_FISH_PAGES = [EPA_FISH] + [f"{EPA_FISH}/{p}" for p in (
    "eat-fish-and-shellfish-healthy-way", "epa-fda-advice-about-eating-fish-and-shellfish",
    "should-i-be-concerned-about-eating-fish-and-shellfish", "how-do-i-know-if-fish-i-caught-contaminated",
    "nlfa-contacts")]
APHIS_CWD = "https://www.aphis.usda.gov/livestock-poultry-disease/cervid/chronic-wasting"
USGS_CWD = "https://www.usgs.gov/centers/nwhc/science/chronic-wasting-disease"

GUIDES = [
    M.cdc_book(GROUP, "cdc_wild_game_diseases", "Diseases from wild game: chronic wasting disease, brucellosis, "
               "trichinellosis and tularemia (CDC)", "Game meat safety and hunters' health",
               ["chronic-wasting", "brucellosis", "trichinellosis", "tularemia"],
               "CDC's pages, every page: chronic wasting disease in deer, elk and moose (where it is found, the "
               "risk to people, and CDC's advice to hunters on testing and not eating meat from infected animals), "
               "brucellosis (hunters of feral swine, elk and bison: gloves and eye protection when dressing, and "
               "cooking the meat), trichinellosis (undercooked bear, wild boar, walrus and other wild game: why "
               "freezing does not always kill it, and cooking to a safe temperature) and tularemia (rabbits, hares "
               "and rodents: gloves, and not handling sick or dead animals).",
               units=[(r"/chronic-wasting/", "Chronic wasting disease"), (r"/brucellosis/", "Brucellosis"),
                      (r"/trichinellosis/", "Trichinellosis"), (r".", "Tularemia")], note=NOTE),
    K.guide(GROUP, "aphis_chronic_wasting_disease", "Chronic wasting disease in deer and elk (USDA APHIS)",
            "Chronic wasting disease", "Animal and Plant Health Inspection Service (APHIS), US Department of "
            "Agriculture", APHIS_CWD,
            r"^https://www\.aphis\.usda\.gov/livestock-poultry-disease/cervid/chronic-wasting(/[a-z0-9-]+)*$",
            "USDA APHIS's chronic wasting disease pages, every page: what the disease is and how it spreads among "
            "deer, elk and moose, where it has been found, the herd certification programme for farmed deer and "
            "elk, and the questions and answers.",
            f"A work of the US Department of Agriculture (public domain). {NOTE}", depth=1, limit=30,
            units=[(r".", "Chronic wasting disease")]),
    X.page_list_book(
        GROUP, "usgs_chronic_wasting_disease", "Chronic wasting disease: the science (USGS National Wildlife Health "
        "Center)", "Chronic wasting disease", "US Geological Survey, National Wildlife Health Center", [USGS_CWD],
        r"^https://www\.usgs\.gov/centers/nwhc/science/chronic-wasting-disease$",
        "The USGS National Wildlife Health Center's page on chronic wasting disease: what prions are, how the "
        "disease spreads in wild deer, elk and moose, its distribution across North America (the map described in "
        "words), and the Center's research.",
        f"From the US Geological Survey: a work of the US government (public domain). {NOTE}",
        units=[(r".", "Chronic wasting disease")]),
    dict(X.page_list_book(
        GROUP, "fda_advice_eating_fish", "Advice about eating fish: which fish and how often (FDA)",
        "Eating fish safely", "US Food and Drug Administration (FDA)", FDA_FISH,
        r"^https://www\.fda\.gov/food/consumers/[a-z0-9-]+$",
        "The FDA's advice about eating fish: the \"best choices\", \"good choices\" and \"choices to avoid\" by "
        "mercury, how many servings a week, the advice for those who are or might become pregnant, those "
        "breastfeeding and young children, fish caught by family and friends, and the questions and answers.",
        f"From the US Food and Drug Administration: FDA's web pages \"are in the public domain and may be "
        f"republished\"; credit to the FDA, with no endorsement implied. {NOTE}",
        units=[(r"questions", "Questions and answers"), (r".", "Advice about eating fish")]),
        licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    dict(X.page_list_book(
        GROUP, "epa_fish_advisories", "Choosing fish and shellfish wisely, and fish advisories (EPA)",
        "Fish advisories", "US Environmental Protection Agency (EPA)", EPA_FISH_PAGES,
        r"^https://www\.epa\.gov/choose-fish-and-shellfish-wisely(/[a-z0-9-]+)?$",
        "The EPA's fish and shellfish pages: eating fish the healthy way, the EPA-FDA advice about eating fish and "
        "shellfish, whether you should be concerned about eating fish (mercury, PCBs and other contaminants), how "
        "to know if fish you caught is contaminated (state, territorial and tribal fish advisories), and the "
        "contacts for each state's advisory programme.",
        "From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
        f"distributed and used for non-commercial, scientific and educational purposes\". {NOTE}",
        units=[(r"nlfa-contacts", "State advisory contacts"), (r".", "Fish and shellfish advice")]),
        licence=X.EPA_TERMS, licence_url=X.EPA_DISCLAIMER, licence_page=X.EPA_DISCLAIMER, licence_text=X.EPA_TEXT,
        personal_use=True),
]

# ====================================================================== the index

SECTIONS = [
    ("Field dressing and transporting game", "Gloves, cooling the carcass fast, and your state's rules on moving "
     "deer, elk and moose from areas with chronic wasting disease.", [
         ("key", "gamefish:cdc_wild_game_diseases", "CDC's advice for hunters: gloves, sick animals, testing"),
         ("key", "gamefish:aphis_chronic_wasting_disease", "Chronic wasting disease (USDA APHIS)"),
         ("key", "gamefish:usgs_chronic_wasting_disease", "Chronic wasting disease: where it is found (USGS)"),
         ("link", "USDA FSIS: game food safety", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-"
          "preparation/meat/game-food-safety", "fsis.usda.gov refuses programs; open it in a browser"),
         ("link", "Your state wildlife agency: field dressing, carcass transport rules and CWD testing",
          "https://www.fws.gov/hunting", "each state's own site, linked from the Fish and Wildlife Service")]),
    ("Processing, preserving and cooking game", "Cutting, freezing, curing, smoking and canning meat.", [
        ("word", "cook:old_secrets_of_meat_curing_1922", "Secrets of Meat Curing (1922; old methods)"),
        ("word", "cook:old_practical_small_smokehouse_for_fish_1918", "A Practical Small Smokehouse for Fish (1918)"),
        ("word", "cook:nchfp_preserving_links", "Home canning and preserving (links to the National Center for Home "
                                               "Food Preservation)"),
        ("key", "outcook:cdc_food_power_outage", "Food safety and safe internal temperatures (CDC)"),
        ("word", "cookbooks", "The cookbooks (request word)")]),
    ("Fish: cleaning, cooking and advisories", "Check the advisory for the water you fished before eating the catch.", [
        ("key", "gamefish:fda_advice_eating_fish", "Advice about eating fish (FDA)"),
        ("key", "gamefish:epa_fish_advisories", "Fish advisories and state contacts (EPA)"),
        ("key", "outdoors:noaa_fisheries_species", "Fish and marine species directory (NOAA Fisheries)"),
        ("link", "EPA fish advisory contacts by state", "https://fishadvisoryonline.epa.gov/Contacts.aspx",
         "an EPA database page; open it in a browser")]),
    ("Hunting and fishing rules and safety", "Licences, seasons and safety.", [
        ("key", "outdoors:fws_hunting_fishing", "Hunting and fishing on national wildlife refuges (US Fish and "
                                                "Wildlife Service)"),
        ("key", "outdoors:usfs_know_before_you_go", "Hunting and outdoor safety on the national forests (US Forest "
                                                    "Service)"),
        ("word", "outdoors", "The outdoor recreation books (request word)"),
        ("manuals", "firearms", "Firearms manuals, with their safety rules"),
        ("link", "Hunter education (IHEA-USA)", "https://www.ihea-usa.org/", "copyright; every state requires its "
         "own course for new hunters")]),
]
INDEX = X.index_maker("gamefish", GROUP, "Game and fish processing: a guide to the library", "Game and fish "
                      "processing", "A guide to game and fish in the library: field dressing and transporting game, "
                      "processing and preserving, fish and fish advisories, and hunting and fishing rules and "
                      "safety.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("gamefish", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"game-fish": lambda: ["gamefish:index"] + [f"gamefish:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "gamefish_cdc_fda": "CDC's terms (as mind_cdc; the pages kept whole) and FDA's website policy (\"in the public "
                        "domain and may be republished\"), both checked at every build.",
    "gamefish_us_gov": "aphis.usda.gov and usgs.gov: works of the US government (17 U.S.C. 105, checked on "
                       "govinfo.gov's policies page at every build); robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "gamefish_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): non-commercial, "
                    "so the fish advisories book is personal use only.",
    "gamefish_index": "The index (gamefish:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("USDA FSIS game, venison and fish food safety pages", "Public domain, but www.fsis.usda.gov refuses programs "
     "(\"403\", robots.txt included, checked again 2026-11-22). CDC's same advice is built. Link-only. Index: "
     "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/meat/game-food-safety"),
    ("State wildlife agencies' field dressing, carcass transport and CWD testing guides", "Each state's own work and "
     "terms (some are not public domain); link-only. Index: https://www.fws.gov/hunting"),
    ("University extension game and fish processing guides (venison processing, jerky, smoking fish)", "Each "
     "university's copyright, or non-commercial licences; none confirmed open one by one, so link-only. Index: "
     "https://nchfp.uga.edu/"),
    ("Hunter education courses and handbooks (IHEA-USA, Kalkomey)", "Copyright; link-only, as in the outdoor "
     "recreation books. Index: https://www.hunter-ed.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
