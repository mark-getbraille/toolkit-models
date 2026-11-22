"""The collection "Hair styling tools, shavers, trimmers and personal care appliances (manuals)" (category key
personal_care_appliances): the owner's request of 2026-11-22 for personal care and beauty products. categories.py adds
it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (hair straighteners and
            flat irons, curling irons and wands, hot rollers, hair clippers, beard, nose and body trimmers,
            epilators, electric razors, facial cleansing brushes, nail drills, foot spas and lighted makeup
            mirrors). Hair dryers, shavers and electric toothbrushes are already searched by the "around the house"
            collection and water flossers by dental_care_devices, so they are not searched again here;
  makers    the makers of these appliances: LINK-ONLY by the owner's rule (Oral-B and Waterpik are already listed
            by the dental care devices collection);
  guidance  the FDA's cosmetics pages the reference library builds in full (textbooks/personal_care.py) and the
            CPSC's and Poison Help's pages as links.

The safety notice is said first (NOTICE): water and electricity, hot tools, sharp blades, sprays near flame, and
Poison Help.
"""

NOTICE = ("Read the safety section first. Never use a hair dryer, straightener, curling iron or trimmer near a filled "
          "sink, bath or shower, and unplug it after use; if a plugged-in appliance falls into water, do not reach "
          "in: unplug it first. Let hot tools cool on a heat-proof surface away from children. Keep blades and "
          "trimmer heads clean and covered. Hair spray and perfume can catch fire near a hot tool or flame. If a "
          "child swallows a cosmetic or a battery, call Poison Help at 1-800-222-1222.")

IA_WORDS = ["hair straightener", "flat iron", "curling iron", "curling wand", "hot rollers", "hair clipper",
            "beard trimmer", "nose trimmer", "body groomer", "epilator", "electric razor", "facial cleansing brush", "nail drill", "foot spa", "lighted mirror", "makeup mirror"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="personal_care_appliances", prefix="pc", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="conair", maker="Conair", type="hair dryers, straighteners, curling irons and trimmers",
         library="https://www.conair.com/", site="conair.com"),
    dict(key="remington", maker="Remington", type="shavers, trimmers and hair styling tools",
         library="https://www.remingtonproducts.com/", site="remingtonproducts.com"),
    dict(key="philips-norelco", maker="Philips Norelco and Philips personal care", type="shavers, trimmers and "
         "epilators", library="https://www.usa.philips.com/c-m-pe/support", site="philips.com"),
    dict(key="braun", maker="Braun", type="shavers, epilators and trimmers", library="https://www.braun.com/",
         site="braun.com"),
    dict(key="panasonic-grooming", maker="Panasonic (personal care)", type="shavers, trimmers and hair dryers",
         library="https://shop.panasonic.com/support", site="panasonic.com"),
    dict(key="wahl", maker="Wahl Clipper", type="hair clippers and trimmers", library="https://wahlusa.com/",
         site="wahlusa.com"),
    dict(key="babylisspro", maker="BaBylissPRO", type="professional hair dryers, irons and clippers",
         library="https://www.babylisspro.com/", site="babylisspro.com"),
    dict(key="dyson-hair", maker="Dyson (hair care)", type="hair dryers and stylers",
         library="https://www.dyson.com/support", site="dyson.com"),
    dict(key="revlon-tools", maker="Revlon hair tools (Helen of Troy)", type="hot air brushes, irons and dryers",
         library="https://www.revlonhairtools.com/", site="revlonhairtools.com"),
    dict(key="hot-tools", maker="Hot Tools (Helen of Troy)", type="curling irons, flat irons and dryers",
         library="https://www.hottools.com/", site="hottools.com"),
]]

GUIDANCE = [
    dict(title="Using cosmetics safely, labels and allergens (FDA; built in full in the reference library: "
               "pcare:fda_cosmetics_safety)",
         url="https://www.fda.gov/cosmetics/resources-consumers-cosmetics/using-cosmetics-safely",
         by="the US Food and Drug Administration"),
    dict(title="Hair dyes, hair products and nail products (FDA; in the reference library: pcare:fda_cosmetic_products)",
         url="https://www.fda.gov/cosmetics/cosmetic-products/hair-dyes", by="the US Food and Drug Administration"),
    dict(title="Electrical safety and hair dryers (CPSC; cpsc.gov refuses programs, so open it in a browser)",
         url="https://www.cpsc.gov/Safety-Education/Safety-Guides", by="the US Consumer Product Safety Commission"),
    dict(title="Poison Help (call 1-800-222-1222; open it in a browser)", url="https://poisonhelp.hrsa.gov/",
         by="the Health Resources and Services Administration"),
]

CATEGORY = dict(
    name="Hair styling tools, shavers, trimmers and personal care appliances (manuals)",
    description="Hair straighteners and flat irons, curling irons and wands, hot rollers, hair clippers, beard and "
                "body trimmers, epilators, electric razors, facial cleansing brushes, nail drills, foot spas "
                "and lighted makeup mirrors: the Internet Archive's manuals, the makers' manual pages "
                "(links) and the FDA's cosmetics safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
