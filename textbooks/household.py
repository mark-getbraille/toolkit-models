"""Cleaning and household management for the reference library, in the group "Reference, cleaning and household
management" (the owner's request of 2026-11-22). Keys: household (every book), house:<name>.

What this module builds, in plain words:
  - house:index, a guide to the library for running a home (the toolkit's own facts and links, CC0): cleaning by room
    and surface and cleaning schedules, safe cleaners and never mixing them, stains and laundry, organising and
    decluttering, kitchen hygiene, mould and pests, the household budget, moving house, home safety checklists, and
    accessible organising and labelling, with the books by key, the picture packs and the links;
  - IN FULL: the FDA's food safety pages for the home kitchen (clean, separate, cook and chill; your kitchen;
    storing food; refrigerator thermometers; produce), a US government work; the EPA's Safer Choice pages (what the
    label means and how to find safer cleaning products), personal use only under the EPA's terms; the CPSC's Home
    Safety Checklist for Older Consumers (1986, read from the Internet Archive's copy, a US government work);
  - three old public-domain books on running a household (published before 1931; each one's description says what
    is out of date): Christine Frederick's Household Engineering (1919), Lucy Balderston's Housewifery (1919) and
    Carlotta Taber's The Business of the Household (1918).
  Every book carries CLEAN_SAFETY in its notice (never mix bleach with ammonia or acids; one product at a time, with
  fresh air; read the label; Poison Control).

Already in the library and not repeated: the USDA stain removal bulletin and the EPA's pest pages (home-crafts), the
EPA's mould, radon and indoor air guides (home:epa_home_health), the CFPB's and FDIC's money guides (money), the
household chemical and pool chemical manual collections, and the laundry care label pack.

Not built (NOT_INCLUDED, link-only): FMCSA's Protect Your Move (public domain, but fmcsa.dot.gov refuses programs and
no Internet Archive copy was found), USDA FSIS (refuses programs), CPSC's current pages (refuse programs), extension
guides (copyright or non-commercial) and decluttering books (copyright).

Run from the repository's folder:
  python3 textbooks/household.py house:fda_kitchen_food_safety --out build/textbooks --limit 3
  python3 textbooks/household.py --list household
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import practical_index as X  # noqa: E402
import refs_kit as K  # noqa: E402

GROUP = "household"
GROUPS = {GROUP: "Reference, cleaning and household management"}

# The same safety words as packs/household_packs.py MIX_NOTE, written for a book.
CLEAN_SAFETY = ("Cleaning safety: never mix cleaning products. Bleach mixed with ammonia, or with acids such as some "
                "toilet bowl and rust cleaners or vinegar, makes poisonous gas. Use one product at a time with fresh "
                "air, follow the label, store cleaners in their own containers away from children and food, and call "
                "Poison Control (1-800-222-1222 in the US) if someone swallows or breathes in a cleaner.")
OLD_HOUSEHOLD_NOTE = ("Published in {year}: an old book. Its cleaning chemicals and methods are out of date and some "
                      "are dangerous (never mix bleach, ammonia or acids; old polishes and moth treatments can be "
                      "poisonous), and its ideas about who does the housework are of its time; it is kept for its "
                      "explanations of planning, schedules and household management. The machine-read text has the "
                      "scanner's mistakes.")

# ====================================================================== FDA (public domain)

FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"are not copyrighted\. They are in the public domain"
FDA_PAGES = [FDA + "/food/buy-store-serve-safe-food/" + p for p in (
    "safe-food-handling", "food-safety-your-kitchen", "food-facts-consumers", "everyday-food-safety-young-adults",
    "selecting-and-serving-produce-safely", "refrigerator-thermometers-cold-facts-about-food-safety")] + [
    FDA + "/consumers/consumer-updates/are-you-storing-food-safely"]
GUIDES = [dict(X.page_list_book(
    GROUP, "fda_kitchen_food_safety", "Food safety in the home kitchen: clean, separate, cook and chill (FDA)",
    "Kitchen hygiene", "US Food and Drug Administration (FDA)", FDA_PAGES,
    r"^https://www\.fda\.gov/(food/buy-store-serve-safe-food|consumers/consumer-updates)/[a-z0-9-]+$",
    "The FDA's pages on keeping food safe at home: the four steps (clean hands and surfaces, separate raw meat, cook "
    "to safe temperatures, chill promptly), food safety in your kitchen (cutting boards, sponges and dishcloths, "
    "counters), the food facts for consumers, everyday food safety for young adults, choosing and serving fruit and "
    "vegetables safely, refrigerator thermometers (40 F or below, the freezer 0 F) and storing food safely.",
    f"From the US Food and Drug Administration: \"the contents of the FDA website ... are not copyrighted. They are "
    f"in the public domain\"; credit to the FDA, with no endorsement implied. {CLEAN_SAFETY}",
    units=[(r"kitchen|handling|young-adults", "Clean, separate, cook and chill"), (r"produce", "Fruit and vegetables"),
           (r".", "Storing food")]),
    licence_page=FDA_POLICY, licence_text=FDA_TEXT)]

# ====================================================================== EPA Safer Choice (personal use)

SAFER = "https://www.epa.gov/saferchoice"
SAFER_PAGES = [SAFER] + [f"{SAFER}/{p}" for p in ("learn-about-safer-choice-label",
                                                  "find-safer-choices-use-your-community", "safer-choice-fact-sheets")]
GUIDES.append(dict(X.page_list_book(
    GROUP, "epa_safer_choice", "Safer Choice: choosing safer cleaning products (EPA)", "Choosing cleaning products",
    "US Environmental Protection Agency (EPA), Safer Choice program", SAFER_PAGES,
    r"^https://www\.epa\.gov/saferchoice(/(learn-about-safer-choice-label|find-safer-choices-use-your-community|"
    r"safer-choice-fact-sheets))?$",
    "The EPA's Safer Choice pages for households: what the Safer Choice label on cleaning, laundry and dish products "
    "means and how products earn it, finding safer products in your community, and the program's fact sheets.",
    f"From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
    f"distributed and used for non-commercial, scientific and educational purposes\". The EPA does not endorse any "
    f"product. {CLEAN_SAFETY}"),
    licence=X.EPA_TERMS, licence_url=X.EPA_DISCLAIMER, licence_page=X.EPA_DISCLAIMER, licence_text=X.EPA_TEXT,
    personal_use=True))
ALLOWED = {X.EPA_TERMS: "non-commercial"}

# ====================================================================== CPSC checklist and the old books

PDFS = [
    K.us_pdf(GROUP, name="cpsc_home_safety_checklist_1986", title="Safety for Older Consumers: Home Safety Checklist "
             "(CPSC, 1986)", subject="Home safety", publisher="US Consumer Product Safety Commission",
             archive="micro_IA41153302_0155", published="1986", version="1986 printing (Internet Archive item "
                                                                         "micro_IA41153302_0155)",
             description="The CPSC's room-by-room home safety checklist for older people and their families: electric "
                         "cords and outlets, rugs and floors, smoke detectors, the kitchen, bathroom, bedrooms, "
                         "stairs, "
                         "lighting and the basement and garage, each with the danger and what to do. Published in "
                         "1986: smoke and carbon monoxide alarm advice has changed (have both, test them monthly).",
             notice=f"A work of the US Consumer Product Safety Commission (public domain), read from the Internet "
                    f"Archive's microfiche scan (the machine-read text has the scanner's mistakes). {CLEAN_SAFETY}"),
    X.old_book(GROUP, "frederick_household_engineering_1919", "Household Engineering: Scientific Management in the "
               "Home (Christine Frederick, 1919)", "Household management", "Christine Frederick (American School of "
               "Home Economics)", "householdenginee00fredrich", 1919,
               "Planning housework like an efficient workshop: arranging the kitchen to save steps, schedules for "
               "daily, weekly and seasonal cleaning, choosing equipment, laundry, buying and budgeting.",
               OLD_HOUSEHOLD_NOTE.format(year=1919)),
    X.old_book(GROUP, "balderston_housewifery_1919", "Housewifery: A Manual and Text Book of Practical Housekeeping "
               "(Lucy R. Balderston, 1919)", "Housekeeping and cleaning", "Lucy R. Balderston (J. B. Lippincott)",
               "housewiferymanua1919bald", 1919,
               "A housekeeping textbook: cleaning each room and surface (wood, metal, glass, fabrics), cleaning tools "
               "and their care, removing stains, laundry, pests, and the order of daily and weekly work.",
               OLD_HOUSEHOLD_NOTE.format(year=1919)),
    X.old_book(GROUP, "taber_business_of_household_1918", "The Business of the Household (C. W. Taber, 1918)",
               "Household budgeting and management", "Carlotta Taber (J. B. Lippincott)",
               "businessofhouseh00tabe", 1918,
               "Running a household as a business: the budget, accounts and records, buying wisely, saving, insurance, "
               "and the costs of food, housing and clothing (prices of 1918).",
               OLD_HOUSEHOLD_NOTE.format(year=1918)),
]
# The old books carry the safety notice too (after the scan notice).
for _p in PDFS:
    if _p.get("old_public_domain"):
        _p["notice"] = f"{_p['notice']} {CLEAN_SAFETY}"

# ====================================================================== the index

SECTIONS = [
    ("Cleaning by room and surface, and cleaning schedules", "What to clean, how, and how often.", [
        ("key", "house:balderston_housewifery_1919", "Housewifery: cleaning each room and surface (old, 1919)"),
        ("key", "house:frederick_household_engineering_1919", "Household Engineering: daily, weekly and seasonal "
                                                              "schedules (old, 1919)"),
        ("pack", "commons_cleaning_tools", "Brooms, mops, sponges, squeegees, toilet brushes, gloves and spray "
                                           "bottles"),
        ("pack", "open_images_cleaning", "Dustpans, dusters, squeegees, sponges and cleaning supplies"),
        ("manuals", "household_cleaning", "Vacuum, carpet cleaner, steam mop and robot vacuum manuals, as links")]),
    ("Safe use of cleaners: never mix them", "Bleach and ammonia, acids, labels and safer products.", [
        ("key", "house:epa_safer_choice", "Safer Choice: choosing safer cleaning products (EPA, personal use)"),
        ("pack", "commons_household_chemicals", "Household chemicals in their containers, with their hazard notes"),
        ("manuals", "household_cleaners", "Cleaning product labels and safety data sheets, as links"),
        ("link", "Poison Control (help line and online tool)", "https://www.poison.org/",
         "call 1-800-222-1222 in the US; open the site in a browser")]),
    ("Stains and laundry", "Removing stains and reading care labels.", [
        ("key", "craft:usda_removing_stains_1965", "Removing Stains from Fabrics (USDA, 1965)"),
        ("pack", "laundry_care_labels", "Laundry care labels and their symbols")]),
    ("Kitchen hygiene", "Clean, separate, cook and chill.", [
        ("key", "house:fda_kitchen_food_safety", "Food safety in the home kitchen (FDA)"),
        ("link", "USDA FSIS: safe food handling and the safe temperature chart",
         "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation", "public domain, but "
                                                                                     "fsis.usda.gov refuses programs; "
                                                                                     "open it in a browser")]),
    ("Mould and pests", "Damp, mould, bed bugs, mice and insects.", [
        ("key", "home:epa_home_health", "The EPA's mould, moisture, radon and indoor air guides (personal use)"),
        ("key", "craft:epa_safe_pest_control", "Controlling pests safely at home (EPA, personal use)")]),
    ("Organising, decluttering and accessible labelling", "Finding things again, by touch and by ear.", [
        ("pack", "commons_cleaning_tools", "Storage boxes, closets and pantries"),
        ("word", "vision-living", "The vision collection's books on labelling, money, medicines and organising the "
                                  "home without sight")]),
    ("The household budget, moving house and home safety", "Money, moving and checklists.", [
        ("key", "house:taber_business_of_household_1918", "The Business of the Household: budgets and accounts (old, "
                                                          "1918)"),
        ("key", "money:cfpb_your_money_your_goals", "Your Money, Your Goals: budgeting tools (CFPB)"),
        ("key", "house:cpsc_home_safety_checklist_1986", "The CPSC's Home Safety Checklist (1986)"),
        ("link", "Protect Your Move (FMCSA): your rights when you hire movers", "https://www.fmcsa.dot.gov/"
                                                                                "protect-your-move",
         "public domain, but fmcsa.dot.gov refuses programs; open it in a browser"),
        ("link", "CPSC home safety guides", "https://www.cpsc.gov/Safety-Education/Safety-Guides", "public "
                                                                                                  "information, but "
                                                                                                  "cpsc.gov refuses "
                                                                                                  "programs")]),
]
INDEX = X.index_maker("house", GROUP, "Cleaning and household management: a guide to the library",
                      "Cleaning and household management",
                      "A guide to the library for running a home: cleaning by room and surface and cleaning schedules, "
                      "safe cleaners and never mixing them, stains and laundry, kitchen hygiene, mould and pests, "
                      "organising and accessible labelling, the household budget, moving house and home safety.",
                      SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("house", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"household": lambda: ["house:index"] + [f"house:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "household_fda": "www.fda.gov/about-fda/about-website/website-policies (checked at every build): \"the contents of "
                     "the FDA website ... are not copyrighted. They are in the public domain\"; credit given. "
                     "robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "household_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): the EPA's "
                     "documents "
                     "are for non-commercial, scientific and educational use, so the Safer Choice book is personal "
                     "use only.",
    "household_cpsc": "The CPSC checklist (1986) is a US government work (17 U.S.C. 105, checked on govinfo.gov's "
                      "policies page at every build), read from the Internet Archive's copy (micro_IA41153302_0155).",
    "household_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every "
                           "build); archive.org's robots.txt allows the files; no AI rules (checked 2026-11-22).",
    "household_index": "The index (house:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("Protect Your Move and \"Your Rights and Responsibilities When You Move\" (FMCSA)", "Public domain, but "
     "www.fmcsa.dot.gov refuses programs (\"403\", 2026-11-22) and no Internet Archive copy was found (searched: "
     "protect your move, rights and responsibilities when you move). Link-only. Index: "
     "https://www.fmcsa.dot.gov/protect-your-move"),
    ("USDA FSIS kitchen and food safety pages", "Public domain, but www.fsis.usda.gov refuses programs (\"403\"); the "
     "FDA's same advice is built (house:fda_kitchen_food_safety). Index: https://www.fsis.usda.gov/food-safety"),
    ("CPSC's current home safety guides and checklists", "Public information under the CPSC's notice, but "
     "www.cpsc.gov refuses this build machine (\"403\", 2026-11-22); the 1986 checklist is built from its Internet "
     "Archive copy. Index: https://www.cpsc.gov/Safety-Education/Safety-Guides"),
    ("University extension guides on cleaning, laundry, organising and household budgets", "Copyright of each "
     "university or CC BY-NC-SA without a usable bulk route (as found for home_crafts.py). Link-only. Index: "
     "https://extension.psu.edu/ and https://extension.umn.edu/"),
    ("Decluttering and organising books (Marie Kondo and others) and cleaning blogs", "Copyright; not built. Index: "
     "https://www.loc.gov/books/"),
    ("Household chemical safety (bleach, ammonia, drain cleaners) and pool chemicals", "Already in the library's "
     "chemical safety manual collections and the household chemical picture packs; not repeated. Index: "
     "https://www.epa.gov/saferchoice"),
    ("Labelling and organising for blind people (braille and large-print labels, talking labels)", "Built by "
     "the vision "
     "collection (request word vision-living); not repeated. Index: https://www.loc.gov/nls/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
