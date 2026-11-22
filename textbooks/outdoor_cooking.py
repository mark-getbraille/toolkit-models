"""Emergency cooking, camp cooking, and grills and smokers for the reference library (the owner's request of
2026-11-22). Keys: outdoor-cooking (every book), outcook:<name>.

What this module builds, in plain words, each IN FULL (every page of the guide, read from the publisher's own site):
  - CDC's carbon monoxide pages (what CO is, symptoms, generators, furnaces and boats), kept whole as CDC's terms ask;
  - CDC's emergency water pages (making water safe by boiling or disinfecting, storing an emergency water supply,
    drinking water advisories, finding clean water, wells and cisterns) with its pages on treating water when hiking
    and camping and choosing home water filters;
  - CDC's food safety pages for power outages and disasters (eating safe food after a power outage, keeping food safe
    after an emergency, discarding food, sanitising cans, thermometers and safe internal temperatures, refrigerating
    within 2 hours, separating raw meat), with its CO, generator, candle and power-outage safety pages;
  - Ready.gov's food, water and power outage pages (emergency food supply, storing water and preparing containers,
    what to do when the power goes out, the emergency supply kit, home fires and home safety);
  - the US Fire Administration's cooking, outdoor fire (grilling, campfires) and carbon monoxide safety pages;
  - the CPSC's grill, carbon monoxide, charcoal, camping equipment and generator safety pages;
  - the US Forest Service's camping, food, bear and responsible recreation pages, and the National Park Service's
    cooking in camp, backcountry camping and bear-safe food storage pages;
  - the EPA's emergency disinfection of drinking water (personal use only: EPA's non-commercial terms);
  - two US Army manuals from the Internet Archive (Distribution Statement A checked by the builder): Field Hygiene and
    Sanitation (TC 4-02.3, 2015: water purification and food safety in the field) and Basic Doctrine for Army Field
    Feeding (FM 10-23, 1996).
  Every book carries SAFETY in its notice: carbon monoxide (never use grills, camp stoves, charcoal or generators
  indoors; get out and call 911 if a CO alarm sounds or anyone feels ill), fire, propane leaks and USDA safe minimum
  internal temperatures.

Already in the library and not repeated: the Army's survival manual (ATP 3-50.21) and field sanitation (FM 4-25.12),
the Navy's Culinary Specialist course, the Army Cook and Army Recipes (fieldmanuals and cookbooks keys), the cookbooks'
smoking and preserving books and their safety notices, FEMA's "Are You Ready?" and the weather safety pages
(preparedness), and Wikibooks' Cookbook (in the Kiwix library). Pre-1900 cookery is not wanted for this collection.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): USDA FSIS and FoodSafety.gov (both refuse
programs), FEMA and the Red Cross's "Food and Water in an Emergency" (a joint brochure marked ©), NFPA, Leave No Trace
and Smokey Bear (copyright), extension guides (copyright or non-commercial), and the makers' manuals (the manual
collection outdoor_cooking lists them as links).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's, NPS's, CPSC's and EPA's own statements are checked at every build and their conditions met in each
book's notice.

Run from the repository's folder:
  python3 textbooks/outdoor_cooking.py outcook:cdc_carbon_monoxide --out build/textbooks --limit 5
  python3 textbooks/outdoor_cooking.py --list outdoor-cooking
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

HEALTH = "health"                      # "Reference, health and safety"
COOK = "cookbooks"                     # "Reference, cookbooks and recipes"
FIELD = "fieldmanual"                  # "Reference, field manuals"

# The safety notice every book carries (the picture packs say the same things in packs/outdoor_cooking_packs.py).
SAFETY = ("Safety: never use grills, camp stoves, charcoal or generators indoors, in a garage, tent or camper: they "
          "make carbon monoxide, which kills without warning. If a CO alarm sounds or anyone feels dizzy, sick or "
          "sleepy, get out to fresh air and call 911. Check propane connections with soapy water, never a flame. "
          "Cook to USDA safe minimum internal temperatures, checked with a food thermometer: 145 F for beef, pork, "
          "lamb and veal steaks, chops and roasts (with a 3-minute rest) and fish, 160 F for ground meat, 165 F for "
          "poultry. When in doubt, throw it out.")

# CDC's terms (as in parenting.py): checked at every build, kept whole, credit and no-endorsement notice.
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"
CDC = "https://www.cdc.gov"


def cdc_site_book(group, name, title, subject, sites, description, units, urls=(), extra="", limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html", which lists every
    page of the site), kept whole under CDC's terms; urls: more CDC pages (matching extra) read first."""
    alt = "|".join(sites)
    own = rf"https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html|php/|hcp/)[a-z0-9-]+(/[a-z0-9-]+)*\.html"
    pages = rf"^({own}{'|' + extra if extra else ''})$"
    entry = K.guide(group, name, title, subject, CDC_PUBLISHER, [f"{CDC}/{s}/site.html" for s in sites], pages,
                    description, f"{CDC_NOTICE} {SAFETY}", depth=1, units=units, limit=limit)
    entry["urls"] = list(urls)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


def page_list_book(group, name, title, subject, publisher, urls, pages, description, notice, units=(), **more):
    """A web guide of a fixed list of pages (no crawl beyond them): the first address is its source."""
    return K.us_web(group, name=name, title=title, subject=subject, publisher=publisher, source=urls[0],
                    description=description, notice=notice, crawl=[(urls[0], 0)], urls=list(urls), pages=pages,
                    unit_rules=list(units), limit=len(urls) + 5, **more)


# ====================================================================== CDC

CDC_FOOD_PAGES = [CDC + "/food-safety/communication-resources/" + p + ".html" for p in (
    "eat-safe-food-after-a-power-outage", "always-use-a-food-thermometer",
    "cook-meat-and-eggs-to-safe-internal-temperatures", "refrigerate-within-2-hours",
    "separate-raw-meat-from-fruits-vegetables", "always-wash-your-hands")] + [
    CDC + "/food-safety/foods/keep-food-safe-after-emergency.html"] + [
    CDC + "/natural-disasters/psa-toolkit/" + p + ".html" for p in (
        "discarding-food-after-a-power-outage", "keeping-or-discarding-packaged-food", "how-to-sanitize-food-cans",
        "safe-food", "boil-water-advisory", "follow-recs-about-boiling-water", "avoiding-carbon-monoxide-poisoning",
        "prevent-carbon-monoxide-poisoning", "use-a-generator-safely", "proper-use-of-candles-during-a-power-outage",
        "dont-heat-your-home-with-a-gas-oven", "build-an-emergency-kit")] + [
    CDC + "/natural-disasters/communication-resources/" + p + ".html" for p in (
        "eat-safe-food-factsheet", "keep-food-safe-after-a-disaster-or-emergency-infographic",
        "make-water-safe-factsheet", "drink-safe-water-flyer")] + [
    CDC + "/natural-disasters/response/what-to-do-protect-yourself-during-a-power-outage.html"]

GUIDES = [
    cdc_site_book(HEALTH, "cdc_carbon_monoxide", "Carbon monoxide poisoning: prevention, generators and symptoms "
                  "(CDC)", "Carbon monoxide safety", ["carbon-monoxide"],
                  "CDC's carbon monoxide pages, every page: what carbon monoxide is and who is at risk, the symptoms "
                  "of CO poisoning, how to prevent it at home, in a car and on a boat, and the fact sheets on CO "
                  "poisoning, generators and furnaces. Never use a generator, grill, camp stove or charcoal inside a "
                  "home, garage or camper.",
                  units=[(r"/factsheets/", "Fact sheets"), (r".", "Carbon monoxide")]),
    cdc_site_book(HEALTH, "cdc_emergency_water", "Safe water in an emergency: boiling, disinfecting and storing water "
                  "(CDC)", "Emergency drinking water", ["water-emergency"],
                  "CDC's emergency water pages, every page: making water safe by boiling or disinfecting it, how to "
                  "create and store an emergency water supply, drinking water advisories (boil water, do not drink, "
                  "do not use), how to find clean water in an emergency, disinfecting wells and cisterns after a "
                  "flood, hygiene and handwashing when water is short; with CDC's pages on treating water when "
                  "hiking, camping and travelling and on choosing a home water filter.",
                  units=[(r"/drinking-water/", "Water on the trail and at home"),
                         (r"/communication-resources/", "Fact sheets"), (r".", "Water in an emergency")],
                  urls=[CDC + "/drinking-water/prevention/water-treatment-hiking-camping-traveling.html",
                        CDC + "/drinking-water/prevention/about-choosing-home-water-filters.html"],
                  extra=r"https://www\.cdc\.gov/drinking-water/prevention/(water-treatment-hiking-camping-traveling|"
                        r"about-choosing-home-water-filters)\.html"),
    dict(page_list_book(
        HEALTH, "cdc_food_power_outage", "Food and water safety in a power outage or disaster (CDC)",
        "Food safety in power outages", CDC_PUBLISHER, CDC_FOOD_PAGES,
        r"^https://www\.cdc\.gov/(food-safety|natural-disasters)/[a-z0-9/-]+\.html$",
        "CDC's pages on food and water when the power is out or after a disaster: eating safe food after a power "
        "outage (what to keep and what to throw out from the fridge and freezer), keeping food safe after an "
        "emergency, keeping or discarding packaged food, sanitising food cans, boil water advisories, using a food "
        "thermometer and cooking meat and eggs to safe internal temperatures, refrigerating within 2 hours, keeping "
        "raw meat apart; and CDC's safety pages on carbon monoxide, generators, candles, gas ovens and what to do in "
        "a power outage.", f"{CDC_NOTICE} {SAFETY}",
        units=[(r"psa-toolkit/(avoiding-carbon|prevent-carbon|use-a-generator|proper-use|dont-heat)|power-outage\.html",
                "Carbon monoxide and power outage safety"),
               (r"water", "Water"), (r".", "Food safety")]),
        licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True),
]

# ====================================================================== Ready.gov (FEMA)

READY = "https://www.ready.gov"
READY_PAGES = [f"{READY}/{p}" for p in ("food", "water", "preparing-your-own-containers-water",
                                         "storing-water-plastic-soda-bottles", "power-outages", "kit",
                                         "home-fires", "home-safety")]
GUIDES.append(page_list_book(
    HEALTH, "ready_food_water_power", "Emergency food, water and power outages (Ready.gov, FEMA)",
    "Emergency food and water", "Ready.gov (Federal Emergency Management Agency)", READY_PAGES,
    r"^https://www\.ready\.gov/(food|water|preparing-your-own-containers-water|storing-water-plastic-soda-bottles|"
    r"power-outages|kit|home-fires|home-safety)$",
    "Ready.gov's pages on food and water in an emergency: building an emergency food supply (foods that need no "
    "refrigeration, cooking or water; rotating stored food; food safety and sanitation; cooking when the power is "
    "out), storing water (how much, containers, preparing your own containers, storing water in soda bottles, "
    "treating water by boiling, chlorination and distillation), what to do before, during and after a power outage "
    "(fridge and freezer, generators outdoors only, carbon monoxide), the emergency supply kit, home fires and home "
    "safety.", f"From Ready.gov, the Federal Emergency Management Agency's preparedness site: a US government work "
               f"(public domain). In danger, call 911. {SAFETY}",
    content=(r'<div class="region-content desktop:grid-col-fill">', r'<footer\b'),
    drop=K.DROP + [r'<div class="translations-available">.*?</ul>'],
    units=[(r"/(food|kit)$", "Emergency food and supplies"), (r"water", "Water"), (r"/power-outages$", "Power outages"),
           (r".", "Fire and home safety")]))

# ====================================================================== US Fire Administration

USFA = "https://www.usfa.fema.gov"
USFA_PAGES = [USFA + p for p in ("/prevention/home-fires/prevent-fires/cooking/", "/prevention/outdoor-fires/",
                                 "/prevention/life-safety-hazards/carbon-monoxide/",
                                 "/prevention/home-fires/prevent-fires/severe-weather/")]
GUIDES.append(page_list_book(
    HEALTH, "usfa_cooking_grilling_fire", "Cooking, grilling, campfire and carbon monoxide safety (US Fire "
    "Administration)", "Cooking and grilling fire safety", "US Fire Administration (FEMA)", USFA_PAGES,
    r"^https://www\.usfa\.fema\.gov/prevention/(home-fires/prevent-fires/(cooking|severe-weather)|outdoor-fires|"
    r"life-safety-hazards/carbon-monoxide)/$",
    "The US Fire Administration's safety pages on cooking fires (stay in the kitchen, grease fires, what to do if "
    "a fire starts), outdoor fires (grilling, campfires, fireworks and wildfire safety), carbon monoxide (alarms, "
    "generators and grills outdoors only, symptoms) and fire safety in severe weather and power outages.",
    f"From the US Fire Administration (FEMA): a US government work (public domain). In a fire, get out and call "
    f"911. {SAFETY}", content=(r'<div class="col-12 col-lg-9( mb-5)?">', r'<footer id="footer">'),
    units=[(r"cooking", "Cooking fires"), (r"outdoor", "Outdoor fires and grilling"),
           (r"carbon", "Carbon monoxide"), (r".", "Severe weather")]))

# ====================================================================== CPSC

# CPSC's copyright notice (as in parenting.py, checked at every build): its web page text is public information.
CPSC = "https://www.cpsc.gov"
CPSC_TERMS = CPSC + "/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy"
CPSC_TEXT = r"Web page text, brochures, and posters presented on CPSC websites are public information"
CO_CENTER = CPSC + "/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center"
CPSC_PAGES = [CO_CENTER, CO_CENTER + "/Charcoal", CO_CENTER + "/Portable-Heaters--Camping-Equipment",
              CO_CENTER + "/CO-Alarms",
              CPSC + "/Safety-Education/Safety-Guides/Home-Fire-Outdoors-and-Garden/Summer-Grill-Safety",
              CPSC + "/Safety-Education/Safety-Guides/Fire/Serve-up-Fire-Safety-in-the-Kitchen",
              CPSC + "/Safety-Education/Safety-Guides/Carbon-Monoxide-Fire-Electronics-and-Electrical-General-"
                     "Information/Survival-After-the-Storm",
              CPSC + "/Safety-Education/Safety-Guides/Carbon-Monoxide-Home/Generators-and-Engine-Driven-Tools",
              CPSC + "/Safety-Education/Safety-Guides/Carbon-Monoxide-Home/Hurricane-Safety",
              CPSC + "/safety-education/safety-guides/carbon-monoxide/carbon-monoxide-fact-sheet"]
GUIDES.append(dict(page_list_book(
    HEALTH, "cpsc_grill_co_safety", "Grill, charcoal, camping equipment and carbon monoxide safety (CPSC)",
    "Grill and carbon monoxide safety", "US Consumer Product Safety Commission (CPSC)", CPSC_PAGES,
    r"^https://www\.cpsc\.gov/(Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center"
    r"(/[A-Za-z-]+)?|Safety-Education/Safety-Guides/[A-Za-z-]+/[A-Za-z-]+|safety-education/safety-guides/"
    r"carbon-monoxide/[a-z-]+)$",
    "The CPSC's safety pages for cooking outdoors and in emergencies: the carbon monoxide information centre (CO "
    "alarms, charcoal, camping equipment such as stoves, heaters and lanterns in tents and campers), the CO fact "
    "sheet, summer grill safety (gas grill leaks, propane cylinders, charcoal), kitchen fire safety, generators and "
    "engine-driven tools, hurricane safety and survival after the storm.",
    f"From the US Consumer Product Safety Commission (cpsc.gov): public information, freely distributed with credit "
    f"to CPSC; this copy does not suggest CPSC's endorsement. Pictures are left out. To report an unsafe product: "
    f"SaferProducts.gov or 1-800-638-2772. {SAFETY}",
    units=[(r"Grill|Kitchen", "Grills and cooking"), (r"Generator|Storm|Hurricane", "Generators and storms"),
           (r".", "Carbon monoxide")]),
    licence_page=CPSC_TERMS, licence_text=CPSC_TEXT))

# ====================================================================== US Forest Service and National Park Service

FS = "https://www.fs.usda.gov/visit/know-before-you-go/"
FS_PAGES = [FS + p for p in ("camping", "food", "bears", "responsible-recreation", "water-safety")]
GUIDES.append(page_list_book(
    COOK, "usfs_camping_food_bears", "Camping, food and bear safety on the national forests (US Forest Service)",
    "Camp food and bear safety", "US Forest Service (US Department of Agriculture)", FS_PAGES,
    r"^https://www\.fs\.usda\.gov/visit/know-before-you-go/(camping|food|bears|responsible-recreation|"
    r"water-safety)$",
    "The US Forest Service's pages for visitors: camping safety (first aid, campfires and putting them out, weather, "
    "water), food on the trail and in camp (planning meals, keeping food cold and safe, washing up, storing food "
    "away from wildlife), being bear aware (what to do if you meet a bear, bear-resistant food storage), "
    "responsible recreation (leaving no trace of your visit) and water safety.",
    f"From the US Forest Service: a US government work (public domain). Check the local forest's fire restrictions "
    f"and food storage orders before you go. {SAFETY}",
    units=[(r"bears", "Bears"), (r"food", "Food"), (r".", "Camping")]))

NPS = "https://www.nps.gov"
NPS_TERMS = NPS + "/aboutus/disclaimer.htm"
NPS_TEXT = r"material created by the National Park Service and presented on this website, unless otherwise " \
           r"indicated, is generally considered in the public domain"
NPS_PAGES = [NPS + p for p in ("/subjects/camping/cooking-in-camp.htm", "/subjects/camping/backcountry-camping.htm",
                               "/subjects/camping/finding-and-setting-up-a-campsite.htm",
                               "/subjects/bears/safety.htm", "/articles/bearsafetyfood.htm")]
GUIDES.append(dict(page_list_book(
    COOK, "nps_camp_cooking_bears", "Cooking in camp and bear-safe food storage (National Park Service)",
    "Camp cooking and bear safety", "National Park Service (US Department of the Interior)", NPS_PAGES,
    r"^https://www\.nps\.gov/(subjects/(camping|bears)|articles)/[a-z0-9-]+\.htm$",
    "The National Park Service's camping pages: cooking in camp (stoves, campfires, food storage, cleaning up), "
    "backcountry camping, finding and setting up a campsite, staying safe around bears, and storing food so bears "
    "and other animals cannot reach it (bear-resistant containers, food lockers, hanging food).",
    f"From the National Park Service: \"material created by the National Park Service ... is generally considered "
    f"in the public domain\"; source: National Park Service (nps.gov). Each park has its own food storage and fire "
    f"rules: check them before you go. {SAFETY}",
    content=(r'<div id="main" role="main" class="MainContent">', r'<div id="related_content_position">|<footer\b'),
    units=[(r"bear", "Bears and food storage"), (r".", "Camping and cooking")]),
    licence_page=NPS_TERMS, licence_text=NPS_TEXT))

# ====================================================================== EPA (personal use)

EPA_TERMS = "EPA website copyright statement"
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"
GUIDES.append(dict(page_list_book(
    HEALTH, "epa_emergency_water", "Emergency disinfection of drinking water (EPA)", "Emergency drinking water",
    "US Environmental Protection Agency (EPA)",
    ["https://www.epa.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water"],
    r"^https://www\.epa\.gov/ground-water-and-drinking-water/emergency-disinfection-drinking-water$",
    "The EPA's guide to making water safe to drink in an emergency: boiling, disinfecting with unscented household "
    "bleach (how many drops per gallon), disinfecting with iodine or chlorine tablets, filtering cloudy water and "
    "storing treated water.",
    f"From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
    f"distributed and used for non-commercial, scientific and educational purposes\". {SAFETY}"),
    licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
    personal_use=True))
ALLOWED = {EPA_TERMS: "non-commercial"}

# ====================================================================== US Army manuals (Internet Archive)

PDFS = [
    K.us_pdf(FIELD, name="army_tc_4_02_3_field_hygiene", title="Field Hygiene and Sanitation (TC 4-02.3, 2015)",
             subject="Field hygiene, water and food safety", publisher="Headquarters, Department of the Army",
             archive="field-hygiene-and-sanitation-tc-4-02.3-may-2015", distribution_a=True, published="2015-05",
             version="TC 4-02.3, May 2015 (Internet Archive item field-hygiene-and-sanitation-tc-4-02.3-may-2015)",
             description="The US Army's field hygiene manual (it replaces FM 4-25.12): personal hygiene, safe "
                         "drinking water in the field (purifying water in canteens and bags with chlorine or "
                         "iodine), food safety and field food service sanitation, waste disposal, insects and pests, "
                         "and heat and cold injuries.",
             notice=f"A work of the US Army (public domain), approved for public release. {SAFETY}"),
    K.us_pdf(FIELD, name="army_fm_10_23_field_feeding", title="Basic Doctrine for Army Field Feeding and Class I "
             "Operations Management (FM 10-23, 1996)", subject="Field feeding",
             publisher="Headquarters, Department of the Army", archive="FM_10_23_B_D_A_F_F_C_I_O_M_1996",
             distribution_a=True, published="1996",
             version="FM 10-23, 1996 (Internet Archive item FM_10_23_B_D_A_F_F_C_I_O_M_1996)",
             description="The US Army's manual on feeding people in the field: field kitchens and their equipment, "
                         "rations (MREs, heat-and-serve and cook-prepared meals), menus, food safety and sanitation, "
                         "water, and planning food for many people away from a fixed kitchen.",
             notice=f"A work of the US Army (public domain), approved for public release. 1996 edition: some "
                    f"equipment and rations have changed. {SAFETY}"),
]

COLLECTION = K.Collection("outcook", HEALTH, guides=GUIDES, pdfs=PDFS,
                          words={"outdoor-cooking": lambda: [f"outcook:{g['name']}" for g in GUIDES + PDFS]})

GROUPS = {}
LICENCE_LINES = {
    "outcook_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                   "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on CDC's "
                   "site), met in each CDC book's notice; the pages are kept whole. robots.txt allows the pages; no AI "
                   "rules (checked 2026-11-22).",
    "outcook_ready_usfa": "www.ready.gov and www.usfa.fema.gov: works of FEMA (17 U.S.C. 105, checked on govinfo.gov's "
                          "policies page at every build); robots.txt allows the pages, no AI rules (checked "
                          "2026-11-22; ready.gov answered programs again on that day).",
    "outcook_cpsc": "www.cpsc.gov/About-CPSC/Policies-Statements-and-Directives/Privacy-Policy (checked at every "
                    "build): \"Web page text, brochures, and posters presented on CPSC websites are public "
                    "information\", credit to CPSC and no endorsement (in the notice); pictures left out.",
    "outcook_usfs_nps": "www.fs.usda.gov: a US government work (17 U.S.C. 105); www.nps.gov/aboutus/disclaimer.htm "
                        "(checked at every build): NPS material \"is generally considered in the public domain\", "
                        "credited in the notice; NPS's robots.txt asks for 5 seconds between pages, which the "
                        "builder keeps. The NPS Leave No Trace page is not read (its text is (c) 1999 the Leave No "
                        "Trace Center).",
    "outcook_epa": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These documents "
                   "may be freely distributed and used for non-commercial, scientific and educational purposes\": "
                   "personal use only.",
    "outcook_army": "TC 4-02.3 (2015) and FM 10-23 (1996): works of the US Army; the builder keeps each only when its "
                    "own front pages say \"Approved for public release; distribution is unlimited\"; read from the "
                    "Internet Archive because armypubs.army.mil shuts out automated readers.",
}
NOT_INCLUDED = [
    ("USDA Food Safety and Inspection Service (FSIS): safe minimum internal temperatures, food safety in a power "
     "outage, grilling and smoking, camping food safety", "Public domain, but www.fsis.usda.gov refuses programs "
     "(\"403\", robots.txt included, checked again 2026-11-22). Its temperatures are in every book's safety notice "
     "and CDC's same advice is built (outcook:cdc_food_power_outage). Link-only. Index: "
     "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/"
     "safe-temperature-chart and https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/"
     "emergencies/keep-your-food-safe-during-emergencies"),
    ("FoodSafety.gov (charts, the FoodKeeper app's storage times)", "Public domain, but www.foodsafety.gov refuses "
     "programs (\"403\", robots.txt included, checked 2026-11-22). Link-only. Index: "
     "https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures"),
    ("Food and Water in an Emergency (FEMA L-210 and American Red Cross ARC 5055, 1994)", "A joint FEMA and Red Cross "
     "brochure whose back page reads \"FEMA (c) L210\"; the Red Cross's share is not a government work, so it is "
     "not built (Ready.gov's newer food and water pages are). Index: "
     "https://archive.org/details/food-and-water-in-an-emergency-1994"),
    ("NFPA grilling, camping and carbon monoxide safety tips", "Copyright of the National Fire Protection "
     "Association; link-only. The US Fire Administration's and CPSC's pages say the same and are built. Index: "
     "https://www.nfpa.org/education-and-research/home-fire-safety/grilling"),
    ("Leave No Trace Seven Principles (Leave No Trace Center for Outdoor Ethics, also on nps.gov)", "\"Leave No "
     "Trace Seven Principles (c) 1999 by the Leave No Trace Center for Outdoor Ethics\", even where the Park Service "
     "reprints them, so they are not copied; the Forest Service's own responsible recreation page is built "
     "(outcook:usfs_camping_food_bears). Index: https://lnt.org/why/7-principles/"),
    ("Smokey Bear campfire safety (smokeybear.com)", "\"(c)2026 Ad Council\", with the National Association of State "
     "Foresters and the Forest Service; the character is protected by law (16 U.S.C. 580p-1, 18 U.S.C. 711). "
     "Link-only. Index: https://smokeybear.com/en/prevention-how-tos/campfire-safety"),
    ("USDA Extension guides on emergency, camp and outdoor cooking (Dutch oven, cast iron, food safety outdoors)",
     "Each university's copyright, or CC BY-NC-SA for some (non-commercial share-alike); none was confirmed open "
     "one by one, so they are link-only for the owner to fetch with Program Downloader. Index: "
     "https://extension.usu.edu/preparedness/ and https://extension.umn.edu/food-safety"),
    ("Makers' manuals and guides (Coleman, Weber, Traeger, Lodge, Camp Chef, Char-Broil, Blackstone, Big Green Egg, "
     "Masterbuilt, Pit Boss, Jetboil, MSR, Primus, Solo Stove, BioLite, Sun Oven, GoSun)", "The makers' copyright; "
     "listed as links in the manual collection outdoor_cooking for the owner to fetch himself. Index: "
     "https://www.weber.com/US/en/customer-service/ and https://www.coleman.com/"),
    ("Air Force SERE handbook (AFH 10-644) and the old Army survival manual (FM 21-76)", "The Army's current survival "
     "manual ATP 3-50.21 is already in the library (fieldmanuals); AFH 10-644 mixes survival with evasion and "
     "resistance (tactics, left out by the field manual rule). Index: https://archive.org/search?query=AFH+10-644"),
    ("Wikibooks Cookbook (CC BY-SA)", "Already in the Kiwix library (wikibooks_en_all); not built again. Index: "
     "https://en.wikibooks.org/wiki/Cookbook:Table_of_Contents"),
    ("Pre-1900 camp and outdoor cookery books", "Not wanted for this collection (the owner prefers modern equipment "
     "and current advice). Index: https://archive.org/search?query=camp+cookery"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
