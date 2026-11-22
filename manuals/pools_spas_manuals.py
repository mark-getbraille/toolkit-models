"""The collection "Pools, spas and hot tubs (manuals)" (category key pools_spas): the owner's request of 2026-11-22 for
pools, spas and hot tubs. practical_manuals.py adds it to CATEGORIES.

What it lists, in plain words (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (pool filters and heaters,
            pool cleaners, salt chlorine generators, hot tubs and spas, above-ground pools). "pool pump" is already
            searched by the lawn_garden collection, so it is not repeated here;
  makers    the pool and spa equipment makers (Pentair, Hayward, Jandy and Zodiac, Polaris, Intex, Bestway, Jacuzzi,
            Hot Spring, Sundance, Bullfrog, Coleman SaluSpa): by the owner's rule LINK-ONLY, for the person (or the
            personal assistant) to open in a browser or fetch with Program Downloader;
  guidance  CDC's healthy swimming, drowning and Legionella pages (built in full in the reference library when CDC
            answers) and the CPSC's Pool Safely (refuses programs), as links.

The pool chemical labels and safety data sheets are the collection pool_spa_chemicals. The safety notice is said
first (NOTICE): drowning prevention, drain covers and never mixing pool chemicals.
"""

NOTICE = ("Never leave children alone in or near water; fence a pool on all four sides with a self-closing, "
          "self-latching gate; keep drain covers in place; turn off the pump and the power before opening a pump, "
          "filter or heater. Never mix different pool chemicals, and add the chemical to water, never water to the "
          "chemical. Keep a hot tub at 104 F (40 C) or below.")

IA_WORDS = ["pool filter", "pool heater", "pool cleaner", "robotic pool cleaner", "salt chlorine generator",
            "salt chlorinator", "chlorinator", "hot tub", "spa heater", "jacuzzi", "above ground pool", "pool cover",
            "sand filter", "cartridge filter"]

RULE = ("by the owner's rule the maker's own manuals are link-only: nothing is read from its site; its page is "
        "listed for the person to open or fetch with Program Downloader")
_COMMON = dict(category="pools_spas", prefix="ps", documents="manuals", access="link", reason=RULE)
MAKERS = [dict(_COMMON, **m) for m in [
    dict(key="pentair", maker="Pentair", type="pool pump, filter, heater and automation",
         library="https://www.pentair.com/en-us/pool-spa-equipment.html", site="pentair.com"),
    dict(key="hayward", maker="Hayward", type="pool pump, filter, heater, cleaner and salt chlorinator",
         library="https://hayward.com/", site="hayward.com"),
    dict(key="jandy-zodiac", maker="Jandy and Zodiac (Fluidra)", type="pool equipment and cleaner",
         library="https://www.jandy.com/", site="jandy.com"),
    dict(key="polaris", maker="Polaris (Zodiac)", type="pool cleaner", library="https://www.polarispool.com/",
         site="polarispool.com"),
    dict(key="intex", maker="Intex", type="above-ground pool, filter pump and inflatable spa",
         library="https://www.intexcorp.com/", site="intexcorp.com"),
    dict(key="bestway", maker="Bestway", type="above-ground pool and Lay-Z-Spa", library="https://www.bestwaycorp.com/",
         site="bestwaycorp.com"),
    dict(key="jacuzzi", maker="Jacuzzi", type="hot tub", library="https://www.jacuzzi.com/", site="jacuzzi.com"),
    dict(key="hot-spring", maker="Hot Spring Spas", type="hot tub", library="https://www.hotspring.com/",
         site="hotspring.com"),
    dict(key="sundance", maker="Sundance Spas", type="hot tub", library="https://www.sundancespas.com/",
         site="sundancespas.com"),
    dict(key="bullfrog", maker="Bullfrog Spas", type="hot tub", library="https://www.bullfrogspas.com/",
         site="bullfrogspas.com"),
]]

GUIDANCE = [
    dict(title="Healthy swimming, drowning prevention and Legionella (CDC; in the reference library: "
               "pool:cdc_healthy_swimming)", url="https://www.cdc.gov/healthy-swimming/",
         by="the US Centers for Disease Control and Prevention"),
    dict(title="Model Aquatic Health Code (CDC)", url="https://www.cdc.gov/model-aquatic-health-code/",
         by="the US Centers for Disease Control and Prevention"),
    dict(title="Pool Safely: drowning and drain entrapment prevention (CPSC; open it in a browser: it refuses "
               "programs)", url="https://www.poolsafely.gov/", by="the US Consumer Product Safety Commission"),
    dict(title="Swimming Pools and Bathing Facilities (Army TB MED 575; in the reference library: "
               "pool:army_tb_med_575)",
         url="https://archive.org/details/ost-military-medical-tbmed575", by="the US Army"),
]

CATEGORY = dict(
    name="Pools, spas and hot tubs (manuals)",
    description="Pool filters, heaters, cleaners, salt chlorine generators and covers, above-ground pools, hot tubs "
                "and spas: the Internet Archive's manuals, the makers' manual pages (links), and the government's "
                "pool, hot tub and drowning prevention guidance. Links only.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=MAKERS, guidance=GUIDANCE, notice=NOTICE)
