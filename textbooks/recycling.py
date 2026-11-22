"""Recycling, waste and composting for the reference library, in its own group "Reference, recycling and waste" (the
owner's request of 2026-11-22). Keys: recycling (every book), recycle:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the EPA's recycling and waste pages for households, every page: recycling basics and benefits, how to recycle
    common things (paper, glass, metal, plastics), what you can do to reduce and reuse, frequent questions,
    electronics donation and recycling, used household batteries and lithium-ion batteries, composting at home,
    preventing wasted food at home, and household hazardous waste (paints, cleaners, oils, pesticides: how to store
    and get rid of them). Personal use only: the EPA's copyright statement allows non-commercial use;
  - the FDA's medicine disposal pages: what to do with unused and expired medicines, drug take-back options, the
    flush list of medicines dangerous enough to flush when no take-back is available, how to put other medicines in
    the household trash, and the questions and answers;
  - the DEA's drug disposal and take-back pages (Diversion Control Division): National Prescription Drug Take Back
    Day, year-round collection sites and disposal of controlled substances;
  - recycle:index, a guide to recycling and waste in the library, with state and city recycling as a list of links
    (each state's and city's own rules), the garden composting books and picture packs, and the electronics waste
    note.

Every book's notice ends with the waste note: never mix cleaning products or pour hazardous waste down a drain, into
the ground or into the household bin; keep it in its original container away from children and pets; lithium
batteries can start fires, so never put them in the household bin or recycling cart; follow your city's or county's
own rules, which differ from place to place.

Not built (NOT_INCLUDED, link-only): the DEA's take-back day site on dea.gov (refuses programs), state and city
recycling programmes (each place's own site), Earth911 and Call2Recycle (copyright), and EPA's regulatory hazardous
waste pages for businesses (out of scope).

Licences: the EPA's copyright statement (non-commercial: personal use) and FDA's website policy are checked at every
build; the DEA's pages are works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page).

Run from the repository's folder:
  python3 textbooks/recycling.py recycle:fda_medicine_disposal --out build/textbooks
  python3 textbooks/recycling.py --list recycling
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import practical_index as X  # noqa: E402 - the index maker, page lists and the EPA's terms

GROUP = "recycling"
GROUPS = {GROUP: "Reference, recycling and waste"}
NOTE = ("Safety: never mix cleaning products, and never pour hazardous waste (paint thinner, oil, pesticides, "
        "pool chemicals) down a drain, onto the ground or into the household bin; keep it in its original, labelled "
        "container away from children and pets. Lithium and other rechargeable batteries can start fires: never put "
        "them in the household bin or the recycling cart. Rules differ from place to place: follow your city's or "
        "county's own.")

EPA = "https://www.epa.gov"
EPA_NOTICE = ("From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
              "distributed and used for non-commercial, scientific and educational purposes\".")
FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FDA_DISPOSAL = [FDA + "/drugs/safe-disposal-medicines/disposal-unused-medicines-what-you-should-know"] + [
    FDA + "/drugs/disposal-unused-medicines-what-you-should-know/" + p for p in (
        "drug-disposal-drug-take-back-options", "drug-disposal-fdas-flush-list-certain-medicines",
        "drug-disposal-dispose-non-flush-list-medicine-trash", "drug-disposal-questions-and-answers")]
DEA = "https://www.deadiversion.usdoj.gov/drug_disposal/"
DEA_PAGES = [DEA + "takeback/", DEA + "drug-disposal.html", DEA + "takeback/takeback.html"]

GUIDES = [
    dict(K.guide(GROUP, "epa_recycling_household_waste", "Recycling, composting, electronics, batteries, food waste "
                 "and household hazardous waste (EPA)", "Recycling and household waste",
                 "US Environmental Protection Agency (EPA)",
                 [EPA + "/recycle", EPA + "/hw/household-hazardous-waste-hhw"],
                 r"^https://www\.epa\.gov/(recycle(/(?!forms/)[a-z0-9-]+)*|hw/household-hazardous-waste-hhw|"
                 r"sustainable-management-food/(composting|community-composting|food-donation-basics|"
                 r"sustainable-management-food-basics))$",
                 "The EPA's pages for households, every page: recycling basics and benefits, how to recycle common "
                 "recyclables (paper, glass, metal, plastics), reducing and reusing, frequent questions about "
                 "recycling, electronics donation and recycling, used household batteries and used lithium-ion "
                 "batteries, composting at home (what to compost and what not to), preventing wasted food at home, "
                 "food donation and composting basics, and household hazardous waste (what it is, storing it "
                 "safely, and taking it to a collection day or site).", f"{EPA_NOTICE} {NOTE}", depth=1,
                 urls=[EPA + "/sustainable-management-food/" + p for p in (
                     "sustainable-management-food-basics", "composting", "community-composting",
                     "food-donation-basics")],
                 units=[(r"batter|electronics", "Electronics and batteries"),
                        (r"compost|food", "Composting and food waste"), (r"/hw/", "Household hazardous waste"),
                        (r".", "Recycling")], limit=80),
         licence=X.EPA_TERMS, licence_url=X.EPA_DISCLAIMER, licence_page=X.EPA_DISCLAIMER, licence_text=X.EPA_TEXT,
         personal_use=True),
    dict(X.page_list_book(
        GROUP, "fda_medicine_disposal", "Disposing of unused medicines: take-back, the flush list and the trash (FDA)",
        "Medicine disposal", "US Food and Drug Administration (FDA)", FDA_DISPOSAL,
        r"^https://www\.fda\.gov/drugs/(safe-disposal-medicines|disposal-unused-medicines-what-you-should-know)/"
        r"[a-z0-9-]+$",
        "The FDA's pages on getting rid of medicines safely: what you should know about unused and expired "
        "medicines, drug take-back options (take-back days, permanent collection sites in pharmacies and police "
        "stations, mail-back envelopes), the flush list of medicines (such as some opioids) that should be flushed "
        "when no take-back is available, how to put other medicines in the household trash (mixed with coffee "
        "grounds or cat litter in a sealed bag, the label scratched out), and the questions and answers.",
        f"From the US Food and Drug Administration: FDA's web pages \"are in the public domain and may be "
        f"republished\"; credit to the FDA, with no endorsement implied. {NOTE}",
        units=[(r"flush", "The flush list"), (r".", "Disposing of medicines")]),
        licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    X.page_list_book(
        GROUP, "dea_drug_take_back", "Drug take-back days and disposal sites (DEA Diversion Control Division)",
        "Medicine take-back", "Drug Enforcement Administration (DEA), Diversion Control Division", DEA_PAGES,
        r"^https://www\.deadiversion\.usdoj\.gov/drug_disposal/(takeback/(takeback\.html)?|drug-disposal\.html)$",
        "The DEA's drug disposal pages: National Prescription Drug Take Back Day (twice a year, at collection sites "
        "across the country), year-round authorised collection sites and how to find one, and how people may get "
        "rid of controlled substance medicines.",
        f"From the Drug Enforcement Administration: a work of the US government (public domain). {NOTE}",
        content=(r'<div role="main" class="main">', r'<footer id="footer"'),
        units=[(r".", "Take-back and disposal")]),
]

# ====================================================================== the index

SECTIONS = [
    ("Recycling at home", "What goes in the recycling cart: check your own city's or county's list, because it "
     "differs from place to place.", [
         ("key", "recycle:epa_recycling_household_waste", "Recycling basics, common recyclables and frequent "
                                                          "questions (EPA)"),
         ("link", "Your state's environmental agency (EPA's list of state agencies)",
          "https://www.epa.gov/home/health-and-environmental-agencies-us-states-and-territories",
          "a list of links; each state's own rules"),
         ("link", "Your city's or county's recycling rules", "https://www.usa.gov/local-governments",
          "find your local government on USA.gov, then its recycling or solid waste page"),
         ("link", "Earth911 recycling locator", "https://search.earth911.com/",
          "a private site, copyright; open it in a browser")]),
    ("Electronics and batteries", "Old phones, computers and batteries go to e-waste and battery drop-offs, never "
     "the household bin.", [
         ("key", "recycle:epa_recycling_household_waste", "Electronics donation and recycling; household and "
                                                          "lithium-ion batteries (EPA)"),
         ("link", "Call2Recycle battery drop-off locator", "https://www.call2recycle.org/locator/",
          "a non-profit's site, copyright; open it in a browser")]),
    ("Household hazardous waste", "Paints, solvents, oils, pesticides, pool chemicals and cleaners.", [
        ("key", "recycle:epa_recycling_household_waste", "Household hazardous waste (EPA)"),
        ("manuals", "household_cleaners", "Household cleaners and laundry: the makers' safety data sheets, as links")]),
    ("Medicines", "Take-back first; the flush list only for the medicines it names; otherwise the trash, mixed and "
     "sealed.", [
         ("key", "recycle:fda_medicine_disposal", "Disposing of unused medicines (FDA)"),
         ("key", "recycle:dea_drug_take_back", "Drug take-back days and sites (DEA)"),
         ("link", "DEA National Prescription Drug Take Back Day", "https://www.dea.gov/takebackday",
          "dea.gov refuses programs; open it in a browser")]),
    ("Composting and food waste", "Composting at home and in the garden.", [
        ("key", "recycle:epa_recycling_household_waste", "Composting at home and preventing wasted food (EPA)"),
        ("key", "garden:nrcs_soil_health", "Soil health and compost (USDA NRCS)"),
        ("word", "gardening", "The gardening books (request word)"),
        ("pack", "commons_garden_care", "Compost, compost bins and worm composting, for the picture describer")]),
]
INDEX = X.index_maker("recycle", GROUP, "Recycling and waste: a guide to the library", "Recycling and waste",
                      "A guide to recycling and waste in the library: recycling at home, electronics and batteries, "
                      "household hazardous waste, medicines, and composting and food waste, with state and city "
                      "recycling as links.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("recycle", GROUP, guides=GUIDES, makers=MAKERS,
                          words={"recycling": lambda: ["recycle:index"] + [f"recycle:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "recycle_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These documents "
                   "may be freely distributed and used for non-commercial, scientific and educational purposes\": "
                   "personal use only.",
    "recycle_fda_dea": "FDA's website policy (\"in the public domain and may be republished\", checked at every "
                       "build); www.deadiversion.usdoj.gov: a work of the US government (17 U.S.C. 105); robots.txt "
                       "allows the pages; no AI rules (checked 2026-11-22).",
    "recycle_index": "The index (recycle:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("DEA National Prescription Drug Take Back Day site (dea.gov/takebackday)", "Public domain, but www.dea.gov "
     "answers programs \"403\" (checked 2026-11-22); the Diversion Control Division's take-back pages are built "
     "(recycle:dea_drug_take_back). Link-only. Index: https://www.dea.gov/takebackday"),
    ("State and city recycling programmes", "Each state's and city's own site and rules; listed as links in the index "
     "(recycle:index). Index: https://www.epa.gov/home/health-and-environmental-agencies-us-states-and-territories"),
    ("Earth911 and Call2Recycle locators", "Copyright of their owners; link-only. Index: https://search.earth911.com/"),
    ("EPA hazardous waste regulations for businesses (RCRA)", "About permits and rules for businesses, not households; "
     "the household hazardous waste page is built. Index: https://www.epa.gov/hw"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
