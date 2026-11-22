"""The collection "Homesteading and small livestock equipment (manuals)" (category key homestead): the owner's request
of 2026-11-22 for homesteading. categories.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (beekeeping equipment, cream
            separators, butter churns, grain mills, hand and well pumps, pressure tanks, composting toilets, poultry
            pluckers, sheep shears, goat milkers). The
            words "incubator", "brooder", "electric fence", "milking machine" and "livestock waterer" are already
            searched by pet_livestock_supplies, portable power stations by emergency_lighting, and solar, battery, inverter and wind words by
            the power collections, so they are not repeated here;
  makers    the beekeeping, pump, poultry and dairy makers: by the owner's rule their own manuals are
            LINK-ONLY (nothing is read from their sites);
  guidance  the US government pages the reference library builds in full (textbooks/homestead.py: the EPA's well and
            septic pages, the FDA's egg safety page) and the Energy Saver articles.

The safety notice is said first (NOTICE): animal handling, hand washing after poultry, bee sting allergies, septic
tanks and qualified electricians.
"""

NOTICE = 'Read the safety section first. Handle animals calmly with an escape route; wash your hands after touching poultry or eggs (Salmonella). If you are allergic to bee stings, keep your emergency medicine with you. Never enter a septic tank or well pit. Solar, battery, inverter and generator wiring is work for a qualified electrician; switch off and lock out power before servicing a pump.'

IA_WORDS = ["beekeeping", "beehive", "bee hive", "bee smoker", "honey extractor", "cream separator", "butter churn", "grain mill", "hand pump", "pitcher pump", "well pump", "submersible pump", "jet pump", "pressure tank", "composting toilet", "chicken plucker", "poultry plucker", "sheep shears", "shearing machine", "goat milker", "chicken coop"]

RULE = ("by the owner's rule the maker's own manuals and guides are link-only: nothing is read from its site; its "
        "page is listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="homestead", prefix="hs", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="mann-lake", maker="Mann Lake", type="beekeeping equipment", library="https://www.mannlakeltd.com/", site="mannlakeltd.com"),
    dict(key="dadant", maker="Dadant and Sons", type="beekeeping equipment", library="https://www.dadant.com/", site="dadant.com"),
    dict(key="betterbee", maker="Betterbee", type="beekeeping equipment", library="https://www.betterbee.com/", site="betterbee.com"),
    dict(key="premier1", maker="Premier1Supplies", type="electric netting, fencing and sheep equipment", library="https://www.premier1supplies.com/", site="premier1supplies.com"),
    dict(key="heiniger", maker="Heiniger", type="shearing and clipping machines", library="https://www.heiniger.com/", site="heiniger.com"),
    dict(key="featherman", maker="Featherman Equipment", type="poultry pluckers and scalders", library="https://www.featherman.net/", site="featherman.net"),
    dict(key="grundfos", maker="Grundfos", type="well and water pumps", library="https://www.grundfos.com/us", site="grundfos.com"),
    dict(key="goulds", maker="Goulds Water Technology (Xylem)", type="well pumps and pressure tanks", library="https://www.xylem.com/en-us/brands/goulds-water-technology/", site="xylem.com"),
    dict(key="simple-pump", maker="Simple Pump", type="hand well pumps", library="https://www.simplepump.com/", site="simplepump.com"),
    dict(key="separett", maker="Separett", type="composting and urine-diverting toilets", library="https://separett.com/", site="separett.com"),
    dict(key="country-living", maker="Country Living Grain Mills", type="hand grain mills", library="https://countrylivinggrainmills.com/", site="countrylivinggrainmills.com"),
]]

GUIDANCE = [
    dict(title="Private wells and septic systems (EPA; built in full in the reference library: homestead:epa_private_wells_septic)",
         url="https://www.epa.gov/privatewells", by="the US Environmental Protection Agency"),
    dict(title="Egg safety (FDA; in the reference library: homestead:fda_egg_safety)",
         url="https://www.fda.gov/food/buy-store-serve-safe-food/what-you-need-know-about-egg-safety", by="the US Food and Drug Administration"),
    dict(title="Energy Saver: solar and home energy (DOE; in the reference library: dir:energy_saver_articles)",
         url="https://www.energy.gov/energysaver/", by="the US Department of Energy"),
]

CATEGORY = dict(
    name='Homesteading and small livestock equipment (manuals)',
    description="Beekeeping equipment, cream separators, butter churns, grain mills, hand and well pumps, pressure tanks, composting toilets, poultry pluckers, shears and goat milkers: the Internet Archive's manuals, the makers' manual pages (links) and the US government's well, septic and egg safety guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
