"""The collection "Water purifiers, navigation instruments and forge equipment (manuals)" (category key
homestead_skills): the owner's request of 2026-11-23 to fill the thin homestead and self-reliance areas, the manual
side of the reference books under the request word homestead-fill (textbooks/homestead_fill.py). categories.py adds
it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (water purifiers, gravity and
            UV water purifiers, chlorine dioxide tablets, sextants, marine chronometers, blacksmith and gas forges,
            anvils and sausage stuffers). The words "water filter", "meat grinder" and "seed starting" are already
            searched by other collections, so they are not repeated here;
  makers    the water purifier, sextant and navigation instrument, and forge makers: by the owner's rule their own
            manuals are LINK-ONLY (nothing is read from their sites);
  guidance  the reference library's books that hold the government guides in full: the homestead skills index
            (hfill:index), the armed forces' field water manual (TB MED 577) and CDC's emergency water pages.

The safety notice is said first (NOTICE): boiling water when unsure, a filter's own claims about viruses, the Sun
through a sextant, and hot metal and galvanised fumes at the forge.
"""

NOTICE = ("Read the safety section first. If you are not sure water is safe, bring it to a rolling boil for 1 minute "
          "(3 minutes above 6,500 feet); a filter removes viruses only if its maker says it does, and no filter or "
          "tablet removes fuel or chemicals. Never look at the Sun through a sextant without its Sun shades. At the "
          "forge, treat all metal as hot, wear safety glasses, and never heat galvanised metal (its fumes cause metal "
          "fume fever).")

IA_WORDS = ["water purifier", "gravity water filter", "uv water purifier", "chlorine dioxide tablets", "sextant",
            "marine chronometer", "blacksmith forge", "gas forge", "anvil", "sausage stuffer"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="homestead_skills", prefix="hk", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="hk-sawyer", maker="Sawyer Products", type="water filters and purifiers", library="https://www.sawyer.com/",
         site="sawyer.com"),
    dict(key="hk-katadyn", maker="Katadyn", type="water filters, purifiers and tablets", library="https://www.katadyn.com/",
         site="katadyn.com"),
    dict(key="hk-lifestraw", maker="LifeStraw", type="personal and family water filters", library="https://lifestraw.com/",
         site="lifestraw.com"),
    dict(key="hk-aquamira", maker="Aquamira", type="water treatment drops and tablets", library="https://www.aquamira.com/",
         site="aquamira.com"),
    dict(key="hk-davis", maker="Davis Instruments", type="plastic sextants and marine instruments",
         library="https://www.davisnet.com/", site="davisnet.com"),
    dict(key="hk-celestaire", maker="Celestaire", type="sextants and celestial navigation instruments",
         library="https://www.celestaire.com/", site="celestaire.com"),
    dict(key="hk-centaur-forge", maker="Centaur Forge", type="forges, anvils and blacksmith and farrier tools",
         library="https://www.centaurforge.com/", site="centaurforge.com"),
]]

GUIDANCE = [
    dict(title="Homestead skills: a guide to the library (seed saving, butchering, trapping and tanning, blacksmithing, "
               "stars and navigation, water, nets and baskets; in the reference library: hfill:index)",
         url="https://github.com/mark-getbraille/toolkit-models", by="the Digital Accessibility Toolkit"),
    dict(title="Sanitary Control and Surveillance of Field Water Supplies (TB MED 577; in the reference library: "
               "skill:army_tb_med_577_field_water_supplies_2010)",
         url="https://archive.org/details/ost-military-medical-tbmed577",
         by="the US Army, Navy and Air Force"),
    dict(title="Making water safe in an emergency (CDC; in the reference library: outcook:cdc_emergency_water)",
         url="https://www.cdc.gov/water-emergency/", by="the Centers for Disease Control and Prevention"),
]

CATEGORY = dict(
    name="Water purifiers, navigation instruments and forge equipment (manuals)",
    description="Water purifiers and treatment tablets, sextants and marine chronometers, blacksmith and gas forges, "
                "anvils and sausage stuffers: the Internet Archive's manuals, the makers' manual pages (links) and "
                "the library's water and homestead skills books. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
