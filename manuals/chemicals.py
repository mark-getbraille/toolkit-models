"""The household and garage CHEMICAL collections of the manuals library: safety data sheets, official labels and
safety guides for cleaners, pool and spa chemicals, lawn and garden products, paints, oils, wood finishes,
automotive fluids, glues, solvents, pest control, batteries, fuels, fire extinguishers, personal and baby care,
water treatment, aquarium, darkroom and art supplies, building products, welding gases, boat products and farm
products (categories.py adds them to CATEGORIES; build_manuals.py builds them).

Why (the owner's request, November 2026): a blind person cannot read the warnings, first aid and directions printed
on a bottle. The maker's SAFETY DATA SHEET (SDS) and the official label say what is in the product, what to do if it
is swallowed, splashed or breathed in, how to store it and what never to mix it with. The toolkit identifies the
product (by photo or barcode) and offers these documents, fetched from their official addresses.

Sources, and how each is used (facts and links only; nothing is copied into the index):
  makers      the major US and Canadian brands and store brands of each category (MAKERS below). Every one is
              LINKED, not read, following the firearms collection's cleaning-chemical makers (categories.MAKERS):
              the builder never reads a maker's site here; the address of each maker's SDS or product information
              page (or its home page, where no such page answered) was checked by hand on 2026-11-21 and is listed
              for the person to open. Its "reason" says what was found.
  epa         the US EPA's official labels of registered pesticide products (weed and insect killers, rodent baits,
              disinfectants and sanitisers, pool sanitisers and algaecides, wood preservatives, antifouling paints,
              repellents ...): chemical_labels.EpaData, from the EPA's bulk files and label list (public domain).
              A spec chooses the products of a category (chemical_labels.epa_selected).
  pmra        Health Canada's Pesticide Product Information Database (Open Government Licence - Canada): the
              current products registered in Canada, with the registry page of each, which lists its labels.
  niosh       the NIOSH Pocket Guide to Chemical Hazards (public domain), with links to NOAA's CAMEO Chemicals and
              PubChem for each chemical (never read by the builder).
  guidance    official safety pages linked from each collection (CPSC, EPA, CDC/NIOSH, FEMA's Fire
              Administration, PHMSA, OSHA, Health Canada's registry, CCOHS). Pages on osha.gov, phmsa.dot.gov and
              poisonhelp.hrsa.gov refuse programs, so they were not checked by a program; the others answered.

Never in these collections (CHEMICAL_EXCLUDE, checked on every document name): instructions for making explosives,
incendiaries, chemical weapons or drugs, or for extracting their precursors; and sales papers
(categories.NOT_A_MANUAL, which build_manuals.wanted_document applies to every maker).
"""

CHECKED = "2026-11-21"

# The kinds of product a document is about, from the words of its title (build_manuals.product_type with a maker's
# "types"; the firearm words are never used here).
TYPES = [("bleach", "cleaner"), ("disinfect", "cleaner"), ("detergent", "cleaner"), ("cleaner", "cleaner"),
         ("chlorine", "pool"), ("shock", "pool"), ("algaecide", "pool"), ("ph increaser", "pool"),
         ("ph decreaser", "pool"), ("test strip", "pool"), ("fertilizer", "garden"), ("weed", "garden"),
         ("herbicide", "garden"), ("insecticide", "garden"), ("fungicide", "garden"), ("grass seed", "garden"),
         ("ice melt", "salt"), ("primer", "paint"), ("paint", "paint"), ("stain", "finish"),
         ("polyurethane", "finish"), ("varnish", "finish"), ("lacquer", "finish"), ("shellac", "finish"),
         ("oil", "lubricant"), ("grease", "lubricant"), ("lubricant", "lubricant"), ("antifreeze", "auto"),
         ("coolant", "auto"), ("brake fluid", "auto"), ("washer fluid", "auto"), ("glue", "adhesive"),
         ("adhesive", "adhesive"), ("caulk", "adhesive"), ("sealant", "adhesive"), ("epoxy", "adhesive"),
         ("thinner", "solvent"), ("solvent", "solvent"), ("acetone", "solvent"), ("mineral spirits", "solvent"),
         ("bait", "pest"), ("trap", "pest"), ("battery", "battery"), ("propane", "fuel"), ("charcoal", "fuel"),
         ("kerosene", "fuel"), ("extinguisher", "extinguisher")]

# Documents never put in the index (see the module docstring).
CHEMICAL_EXCLUDE = (r"explosive|detonat|incendiar|thermite|napalm|nerve agent|chemical weapon|blister agent|"
                    r"synthes\w+\s+of\s+(?:meth|mdma|fentanyl|lsd)|clandestine|precursor extraction")

LINKED = (f"linked only: the builder reads no maker's site in the chemical collections (as for the firearms "
          f"collection's cleaning chemicals); this address was checked by hand on {CHECKED}")


def g(title, url, by):
    """One guidance page."""
    return dict(title=title, url=url, by=by)


POISON = g("Poison Help: call 1-800-222-1222 (US) for any poisoning", "https://poisonhelp.hrsa.gov/",
           "the US Health Resources and Services Administration (not checked by a program: the site refuses them)")
HHW = g("Household hazardous waste: how to store and get rid of leftover chemicals",
        "https://www.epa.gov/hw/household-hazardous-waste-hhw", "the US EPA")
CPSC_POISON = g("Poison prevention at home", "https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/"
                "Poison-Prevention-Information-Center", "the US Consumer Product Safety Commission")
HAZCOM = g("Hazard Communication: labels, pictograms and safety data sheets", "https://www.osha.gov/hazcom",
           "the US Occupational Safety and Health Administration (not checked by a program: the site refuses them)")
SDS_BRIEF = g("How to read a safety data sheet (OSHA brief)",
              "https://www.osha.gov/sites/default/files/publications/OSHA3514.pdf",
              "OSHA (not checked by a program: the site refuses them)")
PICTOGRAMS = g("The hazard pictograms on labels (OSHA QuickCard)",
               "https://www.osha.gov/sites/default/files/publications/OSHA3491QuickCardPictogram.pdf",
               "OSHA (not checked by a program: the site refuses them)")
WHMIS = g("WHMIS pictograms and what they mean (Canada)",
          "https://www.ccohs.ca/oshanswers/chemicals/whmis_ghs/pictograms.html",
          "the Canadian Centre for Occupational Health and Safety")
PESTICIDE_LABELS = g("Reading pesticide labels", "https://www.epa.gov/pesticide-labels", "the US EPA")
SAFE_PEST = g("Safe pest control at home", "https://www.epa.gov/safepestcontrol", "the US EPA")
PMRA = g("Health Canada's pesticide registry and label search", "https://pest-control.canada.ca/pesticide-registry/"
         "en/index.html", "Health Canada, Pest Management Regulatory Agency")
DISINFECTANTS = g("EPA-registered disinfectants (lists N, Q and others)",
                  "https://www.epa.gov/pesticide-registration/selected-epa-registered-disinfectants", "the US EPA")
VOC = g("Fumes from paints, solvents and other products (volatile organic compounds)",
        "https://www.epa.gov/indoor-air-quality-iaq/volatile-organic-compounds-impact-indoor-air-quality", "the US EPA")
LEAD = g("Lead in old paint: reducing the risk at home", "https://www.epa.gov/lead/reduce-risk-lead-exposure-home",
         "the US EPA")
MOLD = g("Mould at home", "https://www.epa.gov/mold", "the US EPA")
BATTERIES = g("Used household batteries: recycling and safety", "https://www.epa.gov/recycle/used-household-batteries",
              "the US EPA")
CO = g("Carbon monoxide safety (fuel-burning appliances, generators, grills)",
       "https://www.cpsc.gov/Safety-Education/Safety-Education-Centers/Carbon-Monoxide-Information-Center",
       "the US Consumer Product Safety Commission")
EXTINGUISHERS = g("Choosing and using fire extinguishers",
                  "https://www.usfa.fema.gov/prevention/home-fires/prepare-for-fire/fire-extinguishers/",
                  "the US Fire Administration (FEMA)")
WELLS = g("Private drinking water wells", "https://www.epa.gov/privatewells", "the US EPA")
ERG = g("Emergency Response Guidebook (hazmat placards and UN numbers)",
        "https://www.phmsa.dot.gov/training/hazmat/erg/emergency-response-guidebook-erg",
        "the US Pipeline and Hazardous Materials Safety Administration (not checked by a program: the site refuses "
        "them)")
COSMETIC_LABELS = g("Cosmetics labelling", "https://www.fda.gov/cosmetics/cosmetics-labeling", "the US FDA")
ANIMAL = g("Animal and veterinary products", "https://www.fda.gov/animal-veterinary", "the US FDA")
NIOSH = g("NIOSH Pocket Guide to Chemical Hazards", "https://www.cdc.gov/niosh/npg/", "NIOSH, CDC")
CAMEO = g("CAMEO Chemicals (chemical datasheets and reactivity)", "https://cameochemicals.noaa.gov/", "NOAA")
PUBCHEM = g("PubChem (chemical safety summaries)", "https://pubchem.ncbi.nlm.nih.gov/",
            "the US National Library of Medicine")
EVERY = [POISON, HHW, HAZCOM, SDS_BRIEF, PICTOGRAMS, WHMIS]

# Pesticide product types of the EPA files (chemical_labels.epa_selected "types").
DISINFECTANT_TYPES = ["DISINFECTANT", "SANITIZER", "VIRUCIDE", "TUBERCULOCIDE", "BACTERIOCIDE",
                      "BACTERIOCIDE/BACTERIOSTAT", "BACTERIOSTAT", "FUNGICIDE/FUNGISTAT", "SPORICIDE"]
GARDEN_TYPES = ["HERBICIDE", "HERBICIDE TERRESTRIAL", "INSECTICIDE", "FUNGICIDE", "MITICIDE", "MOLLUSCICIDE",
                "PLANT GROWTH REGULATOR", "REPELLENT", "ACARICIDE", "INSECT GROWTH REGULATOR", "FERTILIZER"]
PEST_TYPES = ["RODENTICIDE", "INSECTICIDE", "TERMITICIDE", "REPELLENT", "MITICIDE", "ACARICIDE",
              "INSECT GROWTH REGULATOR", "REPELLENT OR FEEDING DEPRESSANT", "POISON, MULTIPLE DOSE",
              "POISON, SINGLE DOSE"]
POOL_TYPES = DISINFECTANT_TYPES + ["ALGAECIDE", "ALGICIDE", "MICROBICIDE", "MICROBICIDE/MICROBISTAT", "BIOCIDE",
                                   "SLIMACIDE", "SLIMACIDES", "WATER PURIFIER BACTERIACIDAL"]
HOME = r"HOUSEHOLD|DOMESTIC DWELLING"


def cat(name, description, guidance, epa=None, pmra=None, niosh=False):
    """One chemical category (the makers are added from MAKERS)."""
    out = dict(name=name, description=description, kind="manuals",
               licence="CC0 (facts and links); each document belongs to its maker or publisher"
                       + ("; US EPA data: public domain" if epa else "")
                       + ("; Health Canada data: Open Government Licence - Canada" if pmra else "")
                       + ("; NIOSH data: public domain" if niosh else ""),
               exclude=CHEMICAL_EXCLUDE, guidance=list(guidance) + EVERY)
    if epa:
        out["epa"] = epa
    if pmra:
        out["pmra"] = pmra
    if niosh:
        out["niosh"] = True
    return out


CHEMICAL_CATEGORIES = {
    "household_cleaners": cat(
        "Household cleaners and laundry (safety data sheets)",
        "Bleach, all-purpose, glass, toilet, oven and drain cleaners, laundry detergents, pods and additives, fabric "
        "softeners, dish soap, disinfectant wipes and air fresheners: the makers' safety data sheets and ingredient "
        "pages, with the EPA labels of registered household disinfectants and sanitisers.",
        [CPSC_POISON, DISINFECTANTS, MOLD], epa={"types": DISINFECTANT_TYPES, "sites": HOME},
        pmra={"types": r"SANITIZER|DISINFECT", "domestic": True}),
    "pool_spa_chemicals": cat(
        "Pool and spa chemicals (labels and safety data sheets)",
        "Chlorine tablets and shock, pH up and down, algaecides, test strips and kits: the EPA's and Health "
        "Canada's official labels of every registered pool and spa sanitiser and algaecide, and the makers' "
        "safety data sheets.",
        [], epa={"types": POOL_TYPES, "sites": r"SWIMMING POOL|WHIRLPOOL|HOT TUB|\bSPAS?\b"},
        pmra={"sites": r"SWIMMING POOLS|\bSPAS?\b|HOT TUBS?"}),
    "lawn_garden_chemicals": cat(
        "Lawn and garden products (labels and safety data sheets)",
        "Fertilisers, weed killers, insect killers, fungicides, grass seed, mulch, potting soil and ice melt: the "
        "official labels of the pesticides registered for lawns, gardens and homes in the US and Canada, and the "
        "makers' safety data sheets.",
        [PESTICIDE_LABELS, SAFE_PEST, PMRA], epa={"types": GARDEN_TYPES, "sites": r"LAWN|" + HOME},
        pmra={"sites": r"TURF|RESIDENTIAL OUTDOORS|ORNAMENTALS OUTDOOR", "domestic": True}),
    "pest_control": cat(
        "Pest control at home (labels and safety data sheets)",
        "Mouse and rat baits and traps, ant and roach baits, insect sprays, flea and termite products and "
        "repellents: the official labels of those registered for use in homes, with safe-handling guides.",
        [SAFE_PEST, PESTICIDE_LABELS, PMRA], epa={"types": PEST_TYPES, "sites": HOME},
        pmra={"sites": r"STRUCTURAL|RESIDENTIAL", "types": r"INSECTICIDE|RODENTICIDE|ACARICIDE|REPELLENT",
              "domestic": True}),
    "paints_coatings": cat(
        "Paints and coatings (safety data sheets)",
        "Latex and oil paints, primers, spray paints and every sheen from flat to gloss, and artists' paints: the "
        "paint makers' safety data sheet libraries.",
        [VOC, LEAD]),
    "lubricants_oils": cat(
        "Oils, greases and lubricants (safety data sheets)",
        "Motor oil of every grade, penetrating oils such as WD-40, greases and grease guns, chain lube, white "
        "lithium and silicone sprays.",
        []),
    "wood_finishes": cat(
        "Wood finishes (safety data sheets and labels)",
        "Stains, polyurethane, varnish, lacquer, shellac, Danish and tung oil, waxes and sealers, and the official "
        "labels of registered wood preservatives.",
        [VOC], epa={"sites": r"^WOOD PROTECTION TRT TO (EXIST BUILDINGS|FINISHED WOOD|FIN\. WOOD)"},
        pmra={"types": r"WOOD PRESERVATIVE", "domestic": True}),
    "automotive_fluids": cat(
        "Automotive fluids (safety data sheets)",
        "Antifreeze and coolant, brake fluid, windshield washer fluid, fuel additives and car-care products.",
        [HHW]),
    "adhesives_sealants": cat(
        "Glues, caulks and sealants (safety data sheets)",
        "Super glue, wood glue, epoxy, construction adhesive, silicone and latex caulk, and plumbing cement.",
        [VOC]),
    "solvents_thinners": cat(
        "Solvents, thinners and strippers (safety data sheets)",
        "Paint thinner and mineral spirits, turpentine, acetone, lacquer thinner, denatured alcohol, paint "
        "strippers and adhesive removers.",
        [VOC]),
    "batteries": cat(
        "Batteries (safety data sheets)",
        "Household, button and coin, rechargeable and car batteries: the makers' safety data sheets, and how to "
        "recycle them.", [BATTERIES]),
    "fuels_propane": cat(
        "Propane, fuels, charcoal and lamp oil (safety data sheets)",
        "Propane cylinders, camping fuel, fuel cans, charcoal and lighter fluid, kerosene and lamp oil.",
        [CO]),
    "fire_extinguishers": cat(
        "Fire extinguishers (manuals and safety data sheets)",
        "Home fire extinguishers by class (A, B, C and K): how to choose, use and check them.",
        [EXTINGUISHERS]),
    "personal_care": cat(
        "Personal care products (ingredients and labels)",
        "Shampoo, lotion, sunscreen, deodorant and insect repellents for the skin: the makers' ingredient pages and "
        "the official labels of registered skin repellents.",
        [COSMETIC_LABELS], epa={"types": ["REPELLENT"], "names": r"insect|mosquito|tick|deet|picaridin|skin|off!"},
        pmra={"types": r"INSECT REPELLENT", "sites": r"HUMAN SKIN", "domestic": True}),
    "baby_care": cat(
        "Baby care products (ingredients)",
        "Nappies (diapers), wipes, baby wash, lotion and nappy cream: the makers' ingredient pages.",
        [CPSC_POISON]),
    "water_treatment": cat(
        "Water treatment (labels and safety data sheets)",
        "Water softener salt, water filters and the chlorine shock treatment of private wells: the official labels "
        "of registered drinking-water treatments and well-care guides.",
        [WELLS], epa={"sites": r"HUMAN DRINKING WATER|POTABLE"}),
    "aquarium_chemicals": cat(
        "Aquarium and pond chemicals (labels and safety data sheets)",
        "Water conditioners, test kits, algae and disease treatments for aquariums and ponds.",
        [], epa={"sites": r"AQUARI|ORNAMENTAL PONDS"}),
    "photo_chemicals": cat(
        "Photographic and darkroom chemicals (safety data sheets)",
        "Film and paper developers, stop bath, fixer and toners.", [VOC]),
    "art_craft_supplies": cat(
        "Art and craft supplies (safety data sheets)",
        "Acrylic and oil paints, mediums, resins and epoxy, glues, solder and flux.", [VOC]),
    "concrete_masonry": cat(
        "Concrete, mortar, grout and drywall compound (safety data sheets)",
        "Bagged concrete and mortar, grout, patching compounds, tile adhesive and drywall joint compound.",
        []),
    "roofing_insulation": cat(
        "Roofing and insulation (safety data sheets)",
        "Shingles, roofing cement and coatings, glass and mineral wool insulation and spray foam.", []),
    "welding_gases": cat(
        "Welding and compressed gases (safety data sheets)",
        "Oxygen, acetylene, argon and CO2 mixes, propane and MAPP cylinders, welding wire and rods.", [CO]),
    "marine_products": cat(
        "Boat and marine products (labels and safety data sheets)",
        "Antifouling bottom paint, marine varnish and grease, fuel stabilisers and boat cleaners, with the official "
        "labels of registered antifouling paints.",
        [], epa={"types": ["ANTIFOULANT", "ANTIFOULING"]}, pmra={"types": r"ANTI-FOULING"}),
    "farm_chemicals": cat(
        "Farm products (labels and safety data sheets)",
        "Livestock dewormers and fly control, teat dips, barn disinfectants and diesel fuel additives, with the "
        "official labels of pesticides registered for livestock and barns.",
        [ANIMAL], epa={"sites": r"CATTLE|DAIRY|LIVESTOCK|FARM ANIMALS|POULTRY|SWINE|HORSES|BARNS|MILKING"},
        pmra={"sites": r"LIVESTOCK"}),
    "pesticide_labels": cat(
        "Every registered pesticide label (US EPA and Health Canada)",
        "The official label of every pesticide product registered in the United States (US EPA) and Canada "
        "(Health Canada): weed, insect and rodent killers, disinfectants and sanitisers, pool chemicals, wood "
        "preservatives, antifouling paints and repellents, found by name, maker or registration number (EPA Reg. "
        "No. or PCP number, printed on every label).",
        [PESTICIDE_LABELS, PMRA, DISINFECTANTS], epa={"all": True}, pmra={"all": True}),
    "chemical_safety": cat(
        "Chemical safety guides (NIOSH, CAMEO Chemicals, PubChem)",
        "What a chemical on a label is and how dangerous it is: the NIOSH Pocket Guide page of each of about 680 "
        "chemicals (bleach's sodium hypochlorite, ammonia, acetone, mineral spirits, ethylene glycol ...), with "
        "links to the same chemical in NOAA's CAMEO Chemicals and in PubChem.",
        [NIOSH, CAMEO, PUBCHEM, ERG], niosh=True),
}

# The makers: (category, key, maker, type, the address listed, what was found when it was checked). Every one is a
# "link" maker (see the module docstring). Store brands are listed in the categories where they sell their own.
MAKER_ROWS = [
    # household_cleaners
    ("household_cleaners", "clorox",
     "The Clorox Company (Clorox, Pine-Sol, Liquid-Plumr, Glad, Kingsford, Burt's Bees)", "cleaner",
     "https://www.thecloroxcompany.com/",
     "its safety data sheet page did not answer (HTTP 404), so its home page is listed; look for Safety Data "
     "Sheets (SDS) there"),
    ("household_cleaners", "pg",
     "Procter & Gamble (Tide, Gain, Dawn, Cascade, Mr. Clean, Swiffer, Febreze, Downy)", "cleaner",
     "https://smartlabel.pg.com/",
     "its safety data sheet or product information page answered"),
    ("household_cleaners", "sc-johnson",
     "SC Johnson (Windex, Pledge, Scrubbing Bubbles, Glade, Raid, OFF!, Drano, Shout)", "cleaner",
     "https://www.whatsinsidescjohnson.com/",
     "the site refused the check (HTTP 429); the address is listed for the person to open in a browser"),
    ("household_cleaners", "reckitt", "Reckitt (Lysol, Finish, Air Wick, Woolite, d-CON)", "cleaner",
     "https://www.rbnainfo.com/",
     "its safety data sheet or product information page answered"),
    ("household_cleaners", "church-dwight", "Church & Dwight (Arm & Hammer, OxiClean, Kaboom)", "cleaner",
     "https://churchdwight.com/ingredient-disclosure/",
     "its safety data sheet or product information page answered"),
    ("household_cleaners", "colgate", "Colgate-Palmolive (Palmolive, Ajax, Fabuloso, Murphy Oil Soap)", "cleaner",
     "https://www.colgatepalmolive.com/en-us",
     "its safety data sheet page did not answer (HTTP 404), so its home page is listed; look for Safety Data "
     "Sheets (SDS) there"),
    ("household_cleaners", "henkel", "Henkel (Persil, Purex, all, Snuggle)", "cleaner",
     "https://www.henkel-northamerica.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "seventh-generation", "Seventh Generation", "cleaner",
     "https://www.seventhgeneration.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "method", "Method", "cleaner",
     "https://methodhome.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "zep", "Zep", "cleaner",
     "https://zep.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "bona", "Bona", "cleaner",
     "https://www.bona.com/en-us/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "weiman", "Weiman (Goo Gone)", "cleaner",
     "https://weiman.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "bar-keepers-friend", "Bar Keepers Friend (SerVaas Laboratories)", "cleaner",
     "https://barkeepersfriend.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "clr", "CLR (Jelmar)", "cleaner",
     "https://www.clrbrands.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "javex", "Javex (Clorox Canada)", "cleaner",
     "https://www.clorox.ca/en/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "lavo", "Lavo (Canada: La Parisienne, Hertel)", "cleaner",
     "https://www.lavo.ca/en/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "kirkland", "Kirkland Signature (Costco store brand)", "cleaner",
     "https://www.costco.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "great-value", "Great Value (Walmart store brand)", "cleaner",
     "https://www.walmart.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "up-and-up", "up&up (Target store brand)", "cleaner",
     "https://www.target.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("household_cleaners", "presidents-choice", "President's Choice (Loblaw store brand, Canada)", "cleaner",
     "https://www.pcoptimum.ca/presidents-choice",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # pool_spa_chemicals
    ("pool_spa_chemicals", "hth", "HTH Pool Care", "pool",
     "https://hthpools.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "clorox-pool", "Clorox Pool&Spa", "pool",
     "https://www.cloroxpool.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "bioguard", "BioGuard", "pool",
     "https://bioguard.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "leslies", "Leslie's", "pool",
     "https://lesliespool.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "in-the-swim", "In The Swim", "pool",
     "https://www.intheswim.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "aquachek", "AquaChek test strips", "pool",
     "https://www.aquachek.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "taylor", "Taylor Technologies (test kits)", "pool",
     "https://taylortechnologies.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "natural-chemistry", "Natural Chemistry", "pool",
     "https://naturalchemistry.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "spa-guard", "SpaGuard", "pool",
     "https://spaguard.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pool_spa_chemicals", "sani-marc", "Sani Marc / Spa Choice (Canada)", "pool",
     "https://www.sanimarc.com/",
     "its English page did not answer (HTTP 404); its home page answered"),
    # lawn_garden_chemicals
    ("lawn_garden_chemicals", "scotts",
     "Scotts Miracle-Gro (Scotts, Miracle-Gro, Ortho, Roundup for homeowners)", "garden",
     "https://scottsmiraclegro.com/en-us/home",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "spectrum", "Spectrum Brands (Spectracide, Hot Shot, Cutter, Black Flag)", "garden",
     "https://www.spectrumbrands.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "bioadvanced", "BioAdvanced (SBM Life Science)", "garden",
     "https://bioadvanced.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "bonide", "Bonide", "garden",
     "https://bonide.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "central-garden", "Central Garden & Pet (Amdro, Sevin, Pennington, AMDRO)", "garden",
     "https://www.central.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "espoma", "Espoma", "garden",
     "https://www.espoma.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "safer", "Safer Brand (Woodstream)", "garden",
     "https://www.saferbrand.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "southern-ag", "Southern Ag", "garden",
     "https://southernag.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "jonathan-green", "Jonathan Green", "garden",
     "https://www.jonathangreen.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "lesco", "LESCO (SiteOne)", "garden",
     "https://www.siteone.com/",
     "the site did not answer the check (ReadTimeout); listed for the person to try"),
    ("lawn_garden_chemicals", "morton", "Morton Salt (ice melt, water softener salt)", "salt",
     "https://www.mortonsalt.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "wilson", "Wilson (Home Hardware's garden brand, Canada)", "garden",
     "https://www.homehardware.ca/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("lawn_garden_chemicals", "scotts-canada", "Scotts Canada", "garden",
     "https://scottsmiraclegro.com/en-ca/scotts.html",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lawn_garden_chemicals", "c-i-l", "C-I-L (Nu-Gro, Canada)", "garden",
     "https://www.cil.ca/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # paints_coatings
    ("paints_coatings", "sherwin-williams",
     "Sherwin-Williams (Sherwin-Williams, Valspar, Krylon, Dutch Boy, Minwax, Thompson's WaterSeal, Cabot, "
     "General Paint)", "paint",
     "https://www.paintdocs.com/docs/?acaOrigin=aHR0cDovL3d3dy5wYWludGRvY3MuY29t",
     "its safety data sheet or product information page answered"),
    ("paints_coatings", "benjamin-moore", "Benjamin Moore", "paint",
     "https://www.benjaminmoore.com/en-us",
     "its safety data sheet page did not answer (HTTP 404), so its home page is listed; look for Safety Data "
     "Sheets (SDS) there"),
    ("paints_coatings", "behr", "Behr (and KILZ)", "paint",
     "https://www.behr.com/consumer/sds",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("paints_coatings", "ppg", "PPG (PPG Paints, Glidden, Olympic, Dulux Canada, Sico, Liquid Nails)", "paint",
     "https://www.ppg.com/en-US",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("paints_coatings", "rust-oleum", "Rust-Oleum (Rust-Oleum, Zinsser, Varathane, Watco)", "paint",
     "https://www.rustoleum.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("paints_coatings", "dunn-edwards", "Dunn-Edwards", "paint",
     "https://www.dunnedwards.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("paints_coatings", "kelly-moore", "Kelly-Moore", "paint",
     "https://kellymoore.com/",
     "the site did not answer the check (ConnectionError); listed for the person to try"),
    ("paints_coatings", "cloverdale", "Cloverdale Paint (Canada)", "paint",
     "https://www.cloverdalepaint.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("paints_coatings", "para", "Para Paints (Canada)", "paint",
     "https://www.para.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("paints_coatings", "golden", "Golden Artist Colors", "art",
     "https://goldenartistcolors.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # lubricants_oils
    ("lubricants_oils", "wd-40", "WD-40 Company (WD-40, 3-IN-ONE, Lava, X-14, 2000 Flushes)", "lubricant",
     "https://www.wd40.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "valvoline", "Valvoline", "lubricant",
     "https://www.valvoline.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "exxonmobil", "ExxonMobil (Mobil 1, Mobil Delvac)", "lubricant",
     "https://www.mobil.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("lubricants_oils", "castrol", "Castrol", "lubricant",
     "https://www.castrol.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "shell", "Shell (Pennzoil, Quaker State, Rotella)", "lubricant",
     "https://www.shell.us/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "crc", "CRC Industries", "lubricant",
     "https://www.crcindustries.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "liquid-wrench", "Liquid Wrench and Gunk (Radiator Specialty)", "lubricant",
     "https://www.liquidwrench.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "blaster", "B'laster", "lubricant",
     "https://blastercorp.com/",
     "the site did not answer the check (ConnectionError); listed for the person to try"),
    ("lubricants_oils", "lucas-oil", "Lucas Oil", "lubricant",
     "https://www.lucasoil.com/sds/",
     "its safety data sheet or product information page answered"),
    ("lubricants_oils", "royal-purple", "Royal Purple", "lubricant",
     "https://www.royalpurple.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "amsoil", "AMSOIL", "lubricant",
     "https://www.amsoil.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("lubricants_oils", "petro-canada", "Petro-Canada Lubricants", "lubricant",
     "https://petrocanadalubricants.com/",
     "the site refused the check (HTTP 429); the address is listed for the person to open in a browser"),
    ("lubricants_oils", "finish-line", "Finish Line (bicycle lubricants)", "lubricant",
     "https://finishlineusa.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("lubricants_oils", "lubriplate", "Lubriplate", "lubricant",
     "https://www.lubriplate.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("lubricants_oils", "lincoln", "Lincoln Industrial (grease guns)", "lubricant",
     "https://www.skf.com/us",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # wood_finishes
    ("wood_finishes", "minwax", "Minwax (Sherwin-Williams)", "finish",
     "https://www.minwax.com/en",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "general-finishes", "General Finishes", "finish",
     "https://generalfinishes.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("wood_finishes", "varathane", "Varathane (Rust-Oleum)", "finish",
     "https://www.rustoleum.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "thompsons", "Thompson's WaterSeal", "finish",
     "https://www.thompsonswaterseal.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "cabot", "Cabot", "finish",
     "https://www.cabotstain.com/en",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "olympic", "Olympic (PPG)", "finish",
     "https://olympic.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "deft", "Deft (PPG)", "finish",
     "https://www.ppg.com/en-US/aerospace/products/coatings",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "howard", "Howard Products", "finish",
     "https://howardproducts.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "waterlox", "Waterlox", "finish",
     "https://waterlox.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "old-masters", "Old Masters", "finish",
     "https://maisondartgallery.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "sansin", "Sansin (Canada)", "finish",
     "https://www.sansin.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("wood_finishes", "saman", "Saman (Canada)", "finish",
     "https://saman.ca/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # automotive_fluids
    ("automotive_fluids", "prestone", "Prestone", "auto",
     "https://www.prestone.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "peak", "PEAK (Old World Industries)", "auto",
     "https://www.owi.com/retail",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "zerex", "Zerex (Valvoline)", "auto",
     "https://www.valvoline.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "recochem", "Recochem (Canada)", "auto",
     "https://www.recochem.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "rain-x", "Rain-X (ITW)", "auto",
     "https://www.rainx.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "stp", "STP (Energizer)", "auto",
     "https://stp.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "sea-foam", "Sea Foam", "auto",
     "https://seafoamworks.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "bars", "Bar's Products", "auto",
     "https://www.barsproducts.com/",
     "the site did not answer the check (SSLError); listed for the person to try"),
    ("automotive_fluids", "splash", "Splash windshield washer fluid", "auto",
     "https://www.splashproducts.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "gold-eagle", "Gold Eagle (STA-BIL)", "auto",
     "https://www.goldeagle.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("automotive_fluids", "meguiars", "Meguiar's", "auto",
     "https://www.meguiars.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("automotive_fluids", "turtle-wax", "Turtle Wax", "auto",
     "https://www.turtlewax.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # adhesives_sealants
    ("adhesives_sealants", "3m", "3M (Scotch, Command, Bondo)", "adhesive",
     "https://www.3m.com/3M/en_US/company-us/SDS-search/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("adhesives_sealants", "gorilla", "Gorilla Glue", "adhesive",
     "https://gorillatough.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "elmers", "Elmer's and Krazy Glue (Newell Brands)", "adhesive",
     "https://elmers.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("adhesives_sealants", "loctite", "Loctite (Henkel)", "adhesive",
     "https://www.loctiteproducts.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "dap", "DAP (and Alex)", "adhesive",
     "https://www.dap.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "ge-sealants", "GE Sealants", "adhesive",
     "https://gesealants.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "red-devil", "Red Devil", "adhesive",
     "https://www.reddevil.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "jb-weld", "J-B Weld", "adhesive",
     "https://www.jbweld.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "titebond", "Titebond (Franklin International)", "adhesive",
     "https://www.titebond.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "liquid-nails", "Liquid Nails (PPG)", "adhesive",
     "https://www.pittsburghpaints.com/liquid-nails",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "sika", "Sika", "adhesive",
     "https://usa.sika.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "weldbond", "Weldbond (Frank T. Ross, Canada)", "adhesive",
     "https://www.weldbond.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "lepage", "LePage (Henkel Canada)", "adhesive",
     "https://www.lepage.ca/en.html",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("adhesives_sealants", "oatey", "Oatey (plumbing cement, flux)", "adhesive",
     "https://www.oatey.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # solvents_thinners
    ("solvents_thinners", "wm-barr", "W.M. Barr (Klean-Strip, Goof Off, Jasco)", "solvent",
     "https://barrbrands.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("solvents_thinners", "sunnyside", "Sunnyside", "solvent",
     "https://www.sunnysidecorp.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("solvents_thinners", "crown", "Crown (Packaging Service Company)", "solvent",
     "https://www.pscfuels.com/",
     "the site did not answer the check (ProxyError); listed for the person to try"),
    ("solvents_thinners", "citristrip", "Citristrip", "solvent",
     "https://citristrip.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # pest_control
    ("pest_control", "woodstream", "Woodstream (Victor traps, Terro)", "pest",
     "https://www.woodstream.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "terro", "TERRO", "pest",
     "https://www.terro.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "tomcat", "Tomcat (Bell Laboratories)", "pest",
     "https://scottsmiraclegro.com/en-us/tomcat.html",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "bell-labs", "Bell Laboratories", "pest",
     "https://www.belllabs.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "combat", "Combat (Henkel)", "pest",
     "https://www.combatbugs.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "raid", "Raid (SC Johnson)", "pest",
     "https://www.raid.com/",
     "the site refused the check (HTTP 429); the address is listed for the person to open in a browser"),
    ("pest_control", "catchmaster", "Catchmaster", "pest",
     "https://www.catchmaster.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("pest_control", "doktor-doom", "Doktor Doom (Canada)", "pest",
     "https://doktordoom.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # batteries
    ("batteries", "energizer", "Energizer (Energizer, Eveready, Rayovac)", "battery",
     "https://data.energizer.com/",
     "its safety data sheet or product information page answered"),
    ("batteries", "duracell", "Duracell", "battery",
     "https://duracell.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("batteries", "panasonic", "Panasonic batteries", "battery",
     "https://na.panasonic.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("batteries", "interstate", "Interstate Batteries", "battery",
     "https://www.interstatebatteries.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("batteries", "clarios", "Clarios (Optima, DieHard batteries)", "battery",
     "https://www.clarios.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # fuels_propane
    ("fuels_propane", "blue-rhino", "Blue Rhino (Ferrellgas)", "fuel",
     "https://bluerhino.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "amerigas", "AmeriGas", "fuel",
     "https://www.amerigas.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "bernzomatic", "Bernzomatic (Worthington)", "fuel",
     "https://www.bernzomatic.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "coleman", "Coleman (camping fuel and propane)", "fuel",
     "https://www.coleman.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("fuels_propane", "kingsford", "Kingsford charcoal", "fuel",
     "https://www.kingsford.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "royal-oak", "Royal Oak charcoal", "fuel",
     "https://www.royaloak.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "scepter", "Scepter (fuel cans, Canada)", "fuel",
     "https://www.scepter.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "superior-propane", "Superior Propane (Canada)", "fuel",
     "https://www.superiorpropane.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fuels_propane", "lamplight", "Lamplight (lamp oil)", "fuel",
     "https://www.lamplight.com/",
     "the site did not answer the check (SSLError); listed for the person to try"),
    # fire_extinguishers
    ("fire_extinguishers", "kidde", "Kidde", "extinguisher",
     "https://www.kidde.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fire_extinguishers", "first-alert", "First Alert", "extinguisher",
     "https://www.firstalert.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fire_extinguishers", "amerex", "Amerex", "extinguisher",
     "https://amerex-fire.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("fire_extinguishers", "buckeye", "Buckeye Fire Equipment", "extinguisher",
     "https://buckeyef.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # personal_care
    ("personal_care", "unilever", "Unilever (Dove, Axe, Degree, Suave, Vaseline)", "personal",
     "https://www.unileverusa.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("personal_care", "kenvue", "Kenvue (Neutrogena, Aveeno, Johnson's, Listerine, Band-Aid)", "personal",
     "https://www.kenvue.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("personal_care", "loreal", "L'Oréal USA (L'Oréal Paris, Garnier, Maybelline, CeraVe)", "personal",
     "https://www.loreal.com/en/usa/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("personal_care", "edgewell", "Edgewell (Banana Boat, Hawaiian Tropic, Schick)", "personal",
     "https://edgewell.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("personal_care", "beiersdorf", "Beiersdorf (Nivea, Eucerin, Coppertone)", "personal",
     "https://www.beiersdorf.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # baby_care
    ("baby_care", "kimberly-clark", "Kimberly-Clark (Huggies, Kleenex)", "baby",
     "https://www.kimberly-clark.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("baby_care", "pampers", "Pampers (Procter & Gamble)", "baby",
     "https://www.pampers.com/en-us",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("baby_care", "desitin", "Desitin and Johnson's Baby (Kenvue)", "baby",
     "https://www.kenvue.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # water_treatment
    ("water_treatment", "diamond-crystal", "Diamond Crystal (Cargill salt)", "water",
     "https://www.diamondcrystalsalt.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("water_treatment", "culligan", "Culligan", "water",
     "https://www.culligan.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("water_treatment", "brita", "Brita", "water",
     "https://www.brita.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("water_treatment", "pur", "PUR (Helen of Troy)", "water",
     "https://www.pur.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("water_treatment", "windsor-salt", "Windsor Salt (Canada)", "water",
     "https://windsorsalt.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # aquarium_chemicals
    ("aquarium_chemicals", "api", "API Fishcare (Mars)", "aquarium",
     "https://apifishcare.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("aquarium_chemicals", "tetra", "Tetra (Spectrum Brands)", "aquarium",
     "https://www.tetra-fish.com/",
     "the site did not answer the check (SSLError); listed for the person to try"),
    ("aquarium_chemicals", "seachem", "Seachem", "aquarium",
     "https://www.seachem.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("aquarium_chemicals", "fluval", "Fluval (Hagen, Canada)", "aquarium",
     "https://fluvalaquatics.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    # photo_chemicals
    ("photo_chemicals", "ilford", "Ilford (Harman Technology)", "photo",
     "https://www.ilfordphoto.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("photo_chemicals", "photographers-formulary", "Photographers' Formulary", "photo",
     "https://stores.photoformulary.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("photo_chemicals", "freestyle", "Freestyle Photographic Supplies (Arista)", "photo",
     "https://www.freestylephoto.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    # art_craft_supplies
    ("art_craft_supplies", "liquitex", "Liquitex and Winsor & Newton (ColArt)", "art",
     "https://www.liquitex.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("art_craft_supplies", "gamblin", "Gamblin Artists Colors", "art",
     "https://gamblincolors.com/gamblin/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("art_craft_supplies", "plaid", "Plaid (Mod Podge, FolkArt)", "art",
     "https://plaidonline.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("art_craft_supplies", "artresin", "ArtResin (Canada)", "art",
     "https://www.artresin.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("art_craft_supplies", "kester", "Kester (solder and flux)", "art",
     "https://www.kester.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("art_craft_supplies", "crayola", "Crayola", "art",
     "https://www.crayola.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # concrete_masonry
    ("concrete_masonry", "quikrete", "QUIKRETE", "masonry",
     "https://www.quikrete.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "sakrete", "Sakrete", "masonry",
     "https://www.sakrete.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "custom-building", "Custom Building Products (grout)", "masonry",
     "https://www.custombuildingproducts.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "mapei", "MAPEI", "masonry",
     "https://www.mapei.com/us/en-us/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("concrete_masonry", "laticrete", "LATICRETE", "masonry",
     "https://www.laticrete.com/map",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "king", "King Packaged Materials (Canada)", "masonry",
     "https://www.kingmix.com/",
     "the site did not answer the check (ConnectionError); listed for the person to try"),
    ("concrete_masonry", "usg", "USG (Sheetrock joint compound)", "masonry",
     "https://www.usg.com/en-US",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "cgc", "CGC (Canada)", "masonry",
     "https://www.usg.com/en-US",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("concrete_masonry", "national-gypsum", "National Gypsum (ProForm)", "masonry",
     "https://www.nationalgypsum.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # roofing_insulation
    ("roofing_insulation", "gaf", "GAF", "roofing",
     "https://www.gaf.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("roofing_insulation", "owens-corning", "Owens Corning", "roofing",
     "https://www.owenscorning.com/en-us",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "certainteed", "CertainTeed", "roofing",
     "https://www.certainteed.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "iko", "IKO (Canada)", "roofing",
     "https://www.iko.com/na/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "henry", "Henry (Carlisle)", "roofing",
     "https://www.henry.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "johns-manville", "Johns Manville", "roofing",
     "https://www.jm.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "rockwool", "ROCKWOOL", "roofing",
     "https://www.rockwool.com/north-america/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("roofing_insulation", "great-stuff", "Great Stuff (DuPont)", "roofing",
     "https://www.greatstuff.dupont.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # welding_gases
    ("welding_gases", "airgas", "Airgas", "gas",
     "https://www.airgas.com/sds-search",
     "its safety data sheet or product information page answered"),
    ("welding_gases", "linde", "Linde (Praxair)", "gas",
     "https://www.lindedirect.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("welding_gases", "air-liquide", "Air Liquide", "gas",
     "https://usa.airliquide.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("welding_gases", "lincoln-electric", "Lincoln Electric", "gas",
     "https://www.lincolnelectric.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("welding_gases", "messer", "Messer (Canada and US)", "gas",
     "https://www.messer-us.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    # marine_products
    ("marine_products", "interlux", "Interlux / International (AkzoNobel)", "marine",
     "https://www.international-yachtpaint.com/gl/en/country-selector",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("marine_products", "pettit", "Pettit Marine Paint", "marine",
     "https://www.pettitpaint.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("marine_products", "star-brite", "Star brite", "marine",
     "https://www.starbrite.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("marine_products", "totalboat", "TotalBoat", "marine",
     "https://www.totalboat.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("marine_products", "quicksilver", "Quicksilver (Mercury Marine)", "marine",
     "https://www.mercurymarine.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    # farm_chemicals
    ("farm_chemicals", "zoetis", "Zoetis (animal health)", "farm",
     "https://www.zoetisus.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("farm_chemicals", "merck-animal", "Merck Animal Health", "farm",
     "https://www.merck-animal-health-usa.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("farm_chemicals", "elanco", "Elanco", "farm",
     "https://www.elanco.com/us",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("farm_chemicals", "boehringer", "Boehringer Ingelheim Animal Health", "farm",
     "https://www.bi-animalhealth.com/",
     "the site refused the check (HTTP 403); the address is listed for the person to open in a browser"),
    ("farm_chemicals", "durvet", "Durvet", "farm",
     "https://www.durvet.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("farm_chemicals", "delaval", "DeLaval (teat dips)", "farm",
     "https://www.delaval.com/en-us/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
    ("farm_chemicals", "power-service", "Power Service (diesel fuel additives)", "farm",
     "https://powerservice.com/",
     "its site answered; look for Safety Data Sheets (SDS) or product information there"),
]

MAKERS = [dict(key=key, maker=maker, type=kind, access="link", library=url, category=category, prefix="ch",
               types=TYPES, documents="safety data sheets and product information",
               reason=f"{LINKED} ({found})")
          for category, key, maker, kind, url, found in MAKER_ROWS]

for _key, _cat in CHEMICAL_CATEGORIES.items():
    _cat["makers"] = [m for m in MAKERS if m["category"] == _key]
