"""The collection "Canners, dehydrators, vacuum sealers and freeze dryers (home food preserving manuals)" (category key
canning_preserving): the owner's request of 2026-11-22 for home food preserving. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia             the Internet Archive's manual collections, searched by the words in IA_WORDS (pressure canners,
                 steam and water-bath canners, canning jars, freeze dryers, fermentation crocks). "dehydrator",
                 "vacuum sealer" and "sous vide" are already searched by kitchen_equipment and "pressure cooker" by
                 small_kitchen, so they are not repeated here;
  makers         the canner, jar, dehydrator, vacuum sealer and freeze dryer makers: LINK-ONLY by the owner's rule,
                 for the person (or the personal assistant) to open in a browser or fetch with Program Downloader;
                 nothing is read from their sites;
  public_guides  the USDA Complete Guide to Home Canning (2015 revision, a US government work), the Internet
                 Archive's copy, indexed when the item has a PDF (it is also in the Kiwix library and is the tested
                 method every canner manual should be read with);
  guidance       the reference library's preserving books (textbooks/preserving.py) and the National Center for Home
                 Food Preservation as links.
No canner maker's manual published before 1931 was found as a downloadable copy on the Internet Archive (searched
2026-11-22), so no old maker's manual is listed.

The safety notice is said first (NOTICE): tested recipes, low-acid foods in a pressure canner, gauge testing,
altitude, botulism and pressure canner safety.
"""

NOTICE = ("Read the safety section first. Follow tested, current recipes and processing times (the USDA Complete "
          "Guide to Home Canning or the National Center for Home Food Preservation), not old manuals. Low-acid foods "
          "(vegetables, meat, poultry, fish, beans) must be processed in a pressure canner, never a boiling-water "
          "bath, a steam canner, an oven, a multicooker or an electric pressure cooker that is not tested for "
          "canning, or they can cause botulism. Adjust time or pressure for your altitude above 1,000 feet. Have a "
          "dial gauge tested every year and replace worn gaskets; never open a pressure canner until the pressure "
          "is fully down. Throw away bulging or leaking jars without tasting them; botulism signs (blurred or double "
          "vision, drooping eyelids, trouble swallowing or breathing): call 911.")

IA_WORDS = ["pressure canner", "canner", "steam canner", "water bath canner", "canning", "home canning",
            "canning jar", "freeze dryer", "fermentation crock"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="canning_preserving", prefix="cp", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="presto", maker="Presto (National Presto Industries)", type="pressure canner and dehydrator",
         library="https://www.presto.com/", site="presto.com"),
    dict(key="all-american", maker="All American (Wisconsin Aluminum Foundry)", type="pressure canner",
         library="https://www.allamericancanner.com/", site="allamericancanner.com"),
    dict(key="ball", maker="Ball and Kerr (Newell Brands)", type="canning jars, lids, water-bath canner and electric "
         "canner", library="https://www.ballmasonjars.com/", site="ballmasonjars.com"),
    dict(key="harvest-right", maker="Harvest Right", type="home freeze dryer", library="https://harvestright.com/",
         site="harvestright.com"),
    dict(key="excalibur", maker="Excalibur", type="food dehydrator", library="https://www.excaliburdehydrator.com/",
         site="excaliburdehydrator.com"),
    dict(key="nesco", maker="Nesco", type="food dehydrator and pressure canner", library="https://www.nesco.com/",
         site="nesco.com"),
    dict(key="foodsaver", maker="FoodSaver (Newell Brands)", type="vacuum sealer", library="https://www.foodsaver.com/",
         site="foodsaver.com"),
    dict(key="weston", maker="Weston Brands", type="vacuum sealer, dehydrator and meat processing tools",
         library="https://westonbrands.com/", site="westonbrands.com"),
    dict(key="lem", maker="LEM Products", type="dehydrator, vacuum sealer and jerky tools",
         library="https://www.lemproducts.com/", site="lemproducts.com"),
    dict(key="avid-armor", maker="Avid Armor", type="chamber and external vacuum sealer",
         library="https://www.avidarmor.com/", site="avidarmor.com"),
    dict(key="victorio", maker="Victorio Kitchen Products", type="steam canner, water-bath canner and food strainer",
         library="https://www.victorio.info/", site="victorio.info"),
    dict(key="cosori", maker="COSORI", type="food dehydrator", library="https://www.cosori.com/", site="cosori.com"),
]]

GUIDES = [
    dict(ia="usda-complete-guide-to-home-canning-2015-revision", title="Complete Guide to Home Canning (USDA, 2015 "
         "revision)", by="the US Department of Agriculture (National Institute of Food and Agriculture)", year=2015),
]

GUIDANCE = [
    dict(title="Home food preserving: a guide to the library (built in the reference library: preserve:index)",
         url="https://github.com/mark-getbraille/toolkit-models", by="the toolkit (CC0)"),
    dict(title="Botulism: home-canned foods, symptoms and prevention (CDC; built in full: preserve:cdc_botulism)",
         url="https://www.cdc.gov/botulism/", by="the US Centers for Disease Control and Prevention"),
    dict(title="Food preservation at home (UK Food Standards Agency; built in full: preserve:fsa_food_preservation_uk)",
         url="https://www.gov.uk/guidance/consumer-advice-for-food-preservation-at-home",
         by="the Food Standards Agency (United Kingdom)"),
    dict(title="National Center for Home Food Preservation: tested recipes and canner use (copyright; listed in the "
               "cookbooks: cook:nchfp_preserving_links)", url="https://nchfp.uga.edu/",
         by="the University of Georgia"),
    dict(title="Your county extension office: dial gauge testing and preserving classes (link)",
         url="https://www.nifa.usda.gov/about-nifa/how-we-work/extension/cooperative-extension-system",
         by="the US Department of Agriculture's Cooperative Extension System"),
]

CATEGORY = dict(
    name="Canners, dehydrators, vacuum sealers and freeze dryers (home food preserving manuals)",
    description="Pressure canners, water-bath and steam canners, canning jars and lids, electric canners, food "
                "dehydrators, vacuum sealers, home freeze dryers and fermentation crocks: the Internet Archive's "
                "manuals, the makers' manual pages (Presto, All American, Ball and Kerr, Harvest Right, Excalibur, "
                "Nesco, FoodSaver, Weston, LEM and others; links), the USDA Complete Guide to Home Canning, and the "
                "reference library's preserving and botulism books.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, public_guides=GUIDES, guidance=GUIDANCE, notice=NOTICE)
