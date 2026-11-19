"""The collection "Vaporizers, pipes and smoking accessories (manuals)" (category key smoking_vaping): its makers,
their access decisions, and the category itself (categories.py adds it to CATEGORIES).

Why this collection exists (the owner's and his team's policy of November 2026): a blind adult who owns a
vaporizer, an e-rig, a water pipe, a hookah, a grinder, a rolling machine or an e-cigarette deserves the same
instructions for using, cleaning and charging it safely that its maker gives every sighted owner. Cannabis is legal
for adults in many US states and in Canada, and tobacco and nicotine devices are legal for adults; the toolkit
identifies the device, says a short plain note (the law varies; keep it away from children and pets; nicotine is
addictive and e-liquids are poisonous if swallowed), and offers the maker's own manual.

What it covers: dry-herb and concentrate vaporizers and e-rigs (Storz & Bickel's Volcano, Mighty and Venty; PAX;
DaVinci; Arizer; Firefly; Puffco; G Pen; DynaVap), glass water pipes and pipes (GRAV), hookahs (Khalil Mamoon),
rolling papers and rolling machines (RAW), grinders (Santa Cruz Shredder), and nicotine e-cigarettes and vapes
(Vaporesso, SMOK, JUUL, NJOY, Vuse).

Never in this collection (SMOKING_EXCLUDE, checked on every product and document name): anything for making,
extracting or growing drugs (extraction kits and tubes, "closed loop" extractors, rosin presses' extraction guides,
grow kits and grow tents), pill presses, sales papers (categories.NOT_A_MANUAL), and the humidifiers and steam
"vaporizers" that share the word.

The makers. Each maker's robots.txt and terms of use were read on 2026-11-19 (the same rules as the firearms makers,
categories.MAKERS):
  read     robots.txt allows programs and the terms do not forbid them: the builder reads only the pages listed and
           keeps the links to the maker's own manual files (its hosts).
  link     the terms forbid robots, spiders, crawling or scraping, or the site does not answer programs, or its terms
           could not be read by a program, or no manual page was found: nothing is read; the library's address
           (entered by hand) is listed for the person to open.
  Two makers' terms forbid deep links (DaVinci; RAW allows a link to its home page only): only their home page is
  listed.
"""

# The kinds of product a document is about, from the words of its title: build_manuals.product_type with a maker's
# "types" (the firearm words are never used here).
TYPES = [("e-rig", "e-rig"), ("erig", "e-rig"), ("peak", "e-rig"), ("proxy", "e-rig"), ("dab", "e-rig"),
         ("pivot", "vaporizer"), ("vaporizer", "vaporizer"), ("vaporiser", "vaporizer"), ("vaporization", "vaporizer"),
         ("volcano", "vaporizer"), ("mighty", "vaporizer"), ("venty", "vaporizer"), ("crafty", "vaporizer"),
         ("plenty", "vaporizer"), ("pen", "vaporizer"), ("battery", "vaporizer"), ("hookah", "hookah"),
         ("shisha", "hookah"), ("bong", "water pipe"), ("water pipe", "water pipe"), ("bubbler", "water pipe"),
         ("pipe", "pipe"), ("rolling machine", "rolling"), ("roller", "rolling"), ("rolling paper", "rolling"),
         ("grinder", "grinder"), ("shredder", "grinder"), ("pod", "e-cigarette"), ("e-cigarette", "e-cigarette"),
         ("vape", "e-cigarette"), ("mod", "e-cigarette"), ("kit", "e-cigarette"), ("tank", "e-cigarette"),
         ("coil", "e-cigarette")]

# Products and documents never put in the index (see the module docstring).
SMOKING_EXCLUDE = (r"extract(?:ion|or)\b|closed[- ]loop|\bbho\b|butane\s+(?:hash|honey|oil|extract)|blast(?:er|ing)?\s+"
                   r"tube|pill\s+press|tablet\s+press|grow\s+(?:kit|tent|guide|box)|humidifier|steam\s+vaporizer|"
                   r"vicks|kaz\b|inhaler\s+for\s+steam|warm[- ]mist|cool[- ]mist")

ROBOTS = "robots.txt read 2026-11-19"
SHOPIFY_TERMS = ("the terms of service (read 2026-11-19) forbid using the site \"to spam, phish, pharm, pretext, "
                 "spider, crawl, or scrape\"")

# The makers: the same fields as categories.MAKERS, plus category, prefix (of the index ids), types and documents.
_COMMON = dict(category="smoking_vaping", prefix="sv", types=TYPES, documents="instructions for use")
SMOKING_MAKERS = [dict(_COMMON, **m) for m in [
    # Vaporizers and e-rigs (dry herb and concentrates).
    dict(key="puffco", maker="Puffco", type="e-rig", access="read", library="https://www.puffco.com/pages/support",
         pages=["https://www.puffco.com/pages/pro-2-support-page", "https://www.puffco.com/pages/proxy-pipe-support-page",
                "https://www.puffco.com/pages/puffco-plus-support-page",
                "https://www.puffco.com/pages/the-peak-pro-support-page", "https://www.puffco.com/pages/new-peak-support",
                "https://www.puffco.com/pages/pivot-support", "https://www.puffco.com/pages/peak-pro-link-support"],
         hosts=["cdn.shopify.com"], site="puffco.com", file_titles=True,
         reason=f"{ROBOTS}: allows all; the terms and conditions (read 2026-11-19) say nothing against programs; each "
                "product's support page links its instruction manual (PDF files on the shop's own file host)"),
    dict(key="storz-bickel", maker="Storz & Bickel", type="vaporizer", access="link",
         library="https://www.storz-bickel.com/", site="storz-bickel.com",
         reason=f"{ROBOTS}: allows general programs, but the site did not answer the builder's requests on "
                "2026-11-19 (timed out), so its terms and download pages could not be read: linked only (Volcano, "
                "Mighty, Venty, Crafty; its instructions for use are on its site and help centre)"),
    dict(key="pax", maker="PAX", type="vaporizer", access="link", library="https://www.pax.com/", site="pax.com",
         reason=f"{ROBOTS}: allows all but carts and accounts; the terms (read 2026-11-19) say nothing against "
                "programs, but no page of manual files was found to read (its guides are journal articles): the "
                "home page is linked"),
    dict(key="davinci", maker="DaVinci", type="vaporizer", access="link", library="https://davincivaporizer.com/",
         site="davincivaporizer.com",
         reason=f"{ROBOTS}: allows all; the terms (read 2026-11-19) forbid \"in-line\" links and deep links, so only "
                "the home page is listed (its Owner's Manuals page is linked from there)"),
    dict(key="arizer", maker="Arizer", type="vaporizer", access="link", library="https://arizer.com/support/",
         site="arizer.com", reason=f"{ROBOTS}: allows all but admin and search; " + SHOPIFY_TERMS),
    dict(key="firefly", maker="Firefly", type="vaporizer", access="link", library="https://thefirefly.com/pages/support",
         site="thefirefly.com", reason=f"{ROBOTS}: allows all; " + SHOPIFY_TERMS),
    dict(key="g-pen", maker="G Pen (Grenco Science)", type="vaporizer", access="link", library="https://gpen.com/pages/faq",
         site="gpen.com",
         reason=f"{ROBOTS}: allows all; the terms (read 2026-11-19) say nothing against programs, but no page of "
                "manual files was found: its help page is linked"),
    dict(key="dynavap", maker="DynaVap", type="vaporizer", access="link", library="https://www.dynavap.com/pages/faq",
         site="dynavap.com", reason=f"{ROBOTS}: allows all; " + SHOPIFY_TERMS),
    # Water pipes and pipes.
    dict(key="grav", maker="GRAV", type="water pipe", access="link", library="https://grav.com/pages/support",
         site="grav.com",
         reason=f"{ROBOTS}: allows all; the terms (read 2026-11-19) say nothing against programs, but it publishes "
                "no manual files: its support page is linked"),
    # Hookahs (tobacco).
    dict(key="khalil-mamoon", maker="Khalil Mamoon", type="hookah", access="link", library="https://khalilmamoon.com/",
         site="khalilmamoon.com",
         reason=f"{ROBOTS}: allows all; " + SHOPIFY_TERMS + "; it publishes no manuals: the home page is linked"),
    # Rolling papers and rolling machines.
    dict(key="raw", maker="RAW", type="rolling", access="link", library="https://rawthentic.com/", site="rawthentic.com",
         reason=f"{ROBOTS}: allows all; the terms (read 2026-11-19) forbid \"any robot, spider or other automatic "
                "device\" and any link but to the home page: only the home page is listed"),
    # Grinders.
    dict(key="santa-cruz-shredder", maker="Santa Cruz Shredder", type="grinder", access="link",
         library="https://www.santacruzshredder.com/", site="santacruzshredder.com",
         reason=f"{ROBOTS}: none (HTTP 404); its terms were not read, so nothing is read: the home page is linked"),
    # Nicotine e-cigarettes and vapes.
    dict(key="vaporesso", maker="Vaporesso", type="e-cigarette", access="link",
         library="https://www.vaporesso.com/download-manuals-for-vapes", site="vaporesso.com",
         reason=f"{ROBOTS}: allows all but carts and accounts; its terms of use are shown only by the browser's "
                "scripts and could not be read by a program on 2026-11-19, so nothing is read: its manuals page is "
                "linked"),
    dict(key="smok", maker="SMOK", type="e-cigarette", access="link", library="https://www.smok.com/support/manual",
         site="smok.com", reason=f"{ROBOTS}: allows all; its terms were not read, so nothing is read: its manuals "
                                 "page is linked"),
    dict(key="juul", maker="JUUL", type="e-cigarette", access="link", library="https://www.juul.com/", site="juul.com",
         reason=f"{ROBOTS}: the site refuses programs (HTTP 403): linked only"),
    dict(key="njoy", maker="NJOY", type="e-cigarette", access="link", library="https://njoy.com/", site="njoy.com",
         reason=f"{ROBOTS}: the site refuses programs (HTTP 403): linked only"),
    dict(key="vuse", maker="Vuse", type="e-cigarette", access="link", library="https://www.vuse.com/", site="vuse.com",
         reason=f"{ROBOTS}: allows most pages; its terms were not read, so nothing is read: the home page is linked"),
]]

# General guidance linked from the collection: official public-health pages (US government works).
SMOKING_GUIDANCE = [
    dict(title="Quitting vaping and smoking: Smokefree.gov", url="https://smokefree.gov/",
         by="the US National Cancer Institute"),
    dict(title="Find help for substance use: SAMHSA's National Helpline, 1-800-662-4357",
         url="https://www.samhsa.gov/find-help/helplines/national-helpline",
         by="the US Substance Abuse and Mental Health Services Administration"),
]

CATEGORY = dict(
    name="Vaporizers, pipes and smoking accessories (manuals)",
    description="Makers' own instructions for dry-herb and concentrate vaporizers and e-rigs, water pipes, hookahs, "
                "rolling machines, grinders and nicotine e-cigarettes and vapes: how to use, clean and charge them "
                "safely, as the maker tells every owner. The toolkit says a short plain note with each (the law "
                "varies by place; keep them away from children and pets; nicotine is addictive). Links only, "
                "fetched from the maker.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    makers=SMOKING_MAKERS, exclude=SMOKING_EXCLUDE, guidance=SMOKING_GUIDANCE)
