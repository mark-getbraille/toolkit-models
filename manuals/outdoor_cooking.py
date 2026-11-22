"""The collection "Grills, smokers, camp stoves and emergency cookers (manuals)" (category key outdoor_cooking): the
owner's request of 2026-11-22 for emergency cooking, camp cooking, and grills and smokers. categories.py adds it to
CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (flat-top griddles, pellet grills,
            kamados, rotisseries, Dutch ovens, backpacking and butane stoves, propane regulators, solar ovens ...).
            The plain words "grill", "smoker", "camp stove", "lantern" and "cooler" are already searched by the
            lawn_garden and camping_outdoor collections (and "griddle" by small_kitchen), so they are not repeated here;
  makers    the grill, smoker, stove and cookware makers the owner named and the other big modern makers: by the
            owner's rule their own manuals and guides are LINK-ONLY, for the person (or the personal assistant) to
            open in a browser or fetch with Program Downloader; nothing is read from their sites (their terms keep
            all rights, and Coleman's site refuses programs);
  guidance  the US government pages the reference library builds in full (textbooks/outdoor_cooking.py: CPSC, the US
            Fire Administration, CDC, Ready.gov, the Forest Service and Park Service), with USDA FSIS's temperature
            chart as a link (fsis.usda.gov refuses programs) and NFPA's grilling page as a link (copyright).

The safety notice is said first (NOTICE): carbon monoxide, propane leak test, fire and USDA temperatures.
"""

NOTICE = ("Read the safety section first. Never use a grill, smoker, camp stove, charcoal or generator indoors, in a "
          "garage, tent or camper: carbon monoxide kills; if a CO alarm sounds or anyone feels ill, get out and call "
          "911. Check propane connections with soapy water, never a flame. Keep grills well away from the house. "
          "Cook to USDA safe internal temperatures (145 F whole cuts and fish with a 3-minute rest, 160 F ground "
          "meat, 165 F poultry).")

IA_WORDS = ["flat top griddle", "pellet grill", "kamado", "rotisserie", "barbecue", "bbq", "charcoal", "propane regulator",
            "propane tank", "dutch oven", "cast iron", "backpacking stove", "butane stove", "solar oven",
            "solar cooker", "chafing", "camp chef", "turkey fryer", "outdoor fryer", "pizza oven",
            "meat thermometer", "smokehouse"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="outdoor_cooking", prefix="oc", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="coleman", maker="Coleman", type="camp stove, grill and cooler", library="https://www.coleman.com/",
         site="coleman.com"),
    dict(key="weber", maker="Weber", type="gas, charcoal and pellet grill and griddle",
         library="https://www.weber.com/US/en/customer-service/", site="weber.com"),
    dict(key="traeger", maker="Traeger", type="pellet grill", library="https://www.traeger.com/support",
         site="traeger.com"),
    dict(key="lodge", maker="Lodge Cast Iron", type="cast-iron cookware and Dutch oven",
         library="https://www.lodgecastiron.com/", site="lodgecastiron.com"),
    dict(key="camp-chef", maker="Camp Chef", type="camp stove, pellet grill and griddle",
         library="https://www.campchef.com/", site="campchef.com"),
    dict(key="char-broil", maker="Char-Broil", type="gas and charcoal grill and smoker",
         library="https://www.charbroil.com/", site="charbroil.com"),
    dict(key="blackstone", maker="Blackstone", type="flat-top griddle", library="https://blackstoneproducts.com/",
         site="blackstoneproducts.com"),
    dict(key="big-green-egg", maker="Big Green Egg", type="kamado grill", library="https://biggreenegg.com/",
         site="biggreenegg.com"),
    dict(key="kamado-joe", maker="Kamado Joe", type="kamado grill", library="https://www.kamadojoe.com/",
         site="kamadojoe.com"),
    dict(key="masterbuilt", maker="Masterbuilt", type="electric and charcoal smoker",
         library="https://www.masterbuilt.com/", site="masterbuilt.com"),
    dict(key="pit-boss", maker="Pit Boss", type="pellet grill and smoker", library="https://pitboss-grills.com/",
         site="pitboss-grills.com"),
    dict(key="jetboil", maker="Jetboil", type="backpacking stove", library="https://www.jetboil.com/",
         site="jetboil.com"),
    dict(key="msr", maker="MSR (Mountain Safety Research)", type="backpacking stove and water filter",
         library="https://www.msrgear.com/", site="msrgear.com"),
    dict(key="primus", maker="Primus", type="camp stove", library="https://primus.eu/", site="primus.eu"),
    dict(key="solo-stove", maker="Solo Stove", type="wood-burning camp stove", library="https://www.solostove.com/",
         site="solostove.com"),
    dict(key="biolite", maker="BioLite", type="camp stove", library="https://www.bioliteenergy.com/",
         site="bioliteenergy.com"),
    dict(key="sun-oven", maker="SUN OVEN (Sun Ovens International)", type="solar oven",
         library="https://www.sunoven.com/", site="sunoven.com"),
    dict(key="gosun", maker="GoSun", type="solar cooker", library="https://gosun.co/", site="gosun.co"),
]]

GUIDANCE = [
    dict(title="Grill, charcoal, camping equipment and carbon monoxide safety (CPSC; built in full in the reference "
               "library: outcook:cpsc_grill_co_safety)",
         url="https://www.cpsc.gov/Safety-Education/Safety-Guides/Home-Fire-Outdoors-and-Garden/Summer-Grill-Safety",
         by="the US Consumer Product Safety Commission"),
    dict(title="Outdoor fire safety: grilling and campfires (US Fire Administration; in the reference library: "
               "outcook:usfa_cooking_grilling_fire)", url="https://www.usfa.fema.gov/prevention/outdoor-fires/",
         by="the US Fire Administration (FEMA)"),
    dict(title="Carbon monoxide poisoning (CDC; in the reference library: outcook:cdc_carbon_monoxide)",
         url="https://www.cdc.gov/carbon-monoxide/about/index.html",
         by="the US Centers for Disease Control and Prevention"),
    dict(title="Power outages and emergency food (Ready.gov; in the reference library: "
               "outcook:ready_food_water_power)", url="https://www.ready.gov/power-outages",
         by="FEMA (Ready.gov)"),
    dict(title="Safe minimum internal temperature chart (USDA FSIS; open it in a browser: it refuses programs)",
         url="https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/"
             "safe-temperature-chart", by="the US Department of Agriculture"),
    dict(title="Grilling safety (NFPA; copyright, open it in a browser)",
         url="https://www.nfpa.org/education-and-research/home-fire-safety/grilling",
         by="the National Fire Protection Association"),
]

CATEGORY = dict(
    name="Grills, smokers, camp stoves and emergency cookers (manuals)",
    description="Gas, charcoal, pellet and kamado grills, smokers, flat-top griddles, rotisseries, outdoor fryers and "
                "pizza ovens, camp and backpacking stoves, propane tanks and regulators, Dutch ovens and cast iron, "
                "chafing dishes and solar ovens: the Internet Archive's manuals, the makers' manual pages (links) and "
                "the US government's grill, fire and carbon monoxide safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
