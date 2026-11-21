"""Pack builders for HOUSEHOLD AND GARAGE PRODUCTS AND CHEMICALS, both in their packaging and as they look applied or
in use, and the HAZARD SYMBOLS on their labels. Used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "child": true where the words of a picture name a child and "facts" (the Commons category
it came from). A picture with more than one question comes once with its JPEG and then again as (None, None, row)
rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Why: a blind person at home, in the garage or in a shop needs to know which bottle is bleach and which is
all-purpose cleaner, whether a can is spray paint or WD-40, what a symbol on a package means, whether a metal is
rusting or coated, what finish a piece of wood has, and how to handle a hazardous product safely. Answers are fixed
sentences written here from each source's own labels (a Commons category's name, a file's own title for a symbol, the
file's own English caption), never by an AI model. A brand is said only where the file is in that brand's own Commons
category; nothing printed on a label is said unless the file's own caption says it (the "Describe this picture."
row). Hazardous products get a short safety note ("Keep away from children; never mix bleach with ammonia ..."), from
SAFETY below, the same for every picture of that kind.

The packs (all open: CC0, public domain or CC BY, checked file by file at the source, November 2026):
  commons_household_chemicals  Wikimedia Commons categories of products in their containers: household cleaners
                         (bleach bottles, toilet and oven cleaners, detergents, dish soap, disinfectants, hand
                         sanitisers, air fresheners), lawn and garden products (fertilisers, weed killers including
                         Roundup, insecticides, fungicides, insect repellents, grass seed, mulch, road and rock salt),
                         paints (paint cans, spray cans, artists' paint tubes), oils and automotive fluids (motor oil,
                         WD-40, grease guns, lubricants, antifreeze, brake fluid, fuel additives), adhesives and
                         sealants, solvents (turpentine, acetone), pest control (mousetraps, bait stations, insect
                         traps), batteries (AA, AAA, button cells), propane, acetylene and oxygen cylinders,
                         jerrycans, charcoal and kerosene, fire extinguishers by type (CO2, water, foam), cement bags,
                         mineral wool insulation and photographic chemicals.
  commons_finishes_in_use  Commons categories of what these look like applied or in use: rust, corrosion and
                         verdigris, against galvanised, powder-coated, chrome-plated and brushed metal; varnish,
                         shellac, lacquer and linseed and tung oil on wood; peeling paint and house painting; mildew,
                         efflorescence and spalling on walls and concrete; mortar joints; and pesticides being
                         applied.
  commons_hazard_symbols   Commons drawings and photos of the symbols on chemical packages: the Canadian WHMIS
                         hazard symbols, the NFPA 704 "fire diamond", and GHS pictograms other than safety_signs'
                         nine drawings (photos of labels, variants), plus any US DOT hazardous materials placard
                         filed there. Each symbol's meaning comes from its own file title or category ("WHMIS Class
                         B", "GHS05", "Hazard class 3"): no title, no meaning. The nine GHS pictogram drawings are
                         NOT repeated: safety_signs has them (events_safety_packs.ghs_items).

Not repeated: abo_packaged_goods (Amazon's catalogue photos of cleaners, laundry detergent and motor oil; this
change adds the safety notes of SAFETY to its hazardous household rows), commons_packaging, open_images_packaged_goods,
safety_signs, the fire extinguisher photos of events_safety_packs and work_farm_mech_packs (only Commons categories of
an extinguisher TYPE are read here), the paint rollers of things_packs, and the personal care, toiletry and baby
product pictures of home_packs and abo_packaged_goods. Share-alike Commons files on the same subjects and Open
Products Facts' household chemicals are entries in training-kit/kit/chemical_sources.py.

Safety (packs/SOURCE-RULES.md): no sexual content (NUDE, us_packs.NOT_SHOWN); no poisonings, injuries, deaths, drug
labs, explosives or chemical weapons (HARM: these are everyday packs, and nothing here explains how to make anything
dangerous); chemical structure drawings and molecule models are not photos of products (SKIP, NOT_A_PHOTO); every row
whose words name a child is marked "child". People appear in some photos (painting, spraying), so the two photo packs
are never used for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS); the symbols pack may be. A free photo
dropped only because it has no answer is set aside for a description (build_packs.needs_description).

    python packs/chemical_packs.py commons_household_chemicals --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import math
import random
import re
import sys

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, say, considered, listing_out_of_time, needs_description, pass_random
from food_packs import with_twins, count_pictures, commons_members
from home_packs import file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count, CHILD
from mechanical_packs import in_english, JUST_A_RECORD, NOT_A_CHILD, NOT_A_PHOTO
from us_packs import NOT_SHOWN
from events_safety_packs import commons_files, finish, GHS, GHS_CATEGORY

WHAT_Q = "What is this?"
SAFE_Q = "How do I handle this safely?"
BRAND_Q = "What brand is this?"
SURFACE_Q = "What does this surface look like?"
FINISH_Q = "What finish is on this?"
SYMBOL_Q = "What does this symbol mean?"
SYMBOL_KIND_Q = "What kind of symbol is this?"
CLASS_Q = "What kind of fire is this extinguisher for?"
DESCRIBE_Q = "Describe this picture."

# ----------------------------------------------------------------- safety notes, one per kind of hazard

SAFETY = {
    "bleach": "Keep it away from children and pets. Never mix bleach with ammonia, vinegar, acids or other cleaners: "
              "together they give off toxic gas. Use it with fresh air and rinse skin or eyes with water at once.",
    "corrosive": "It is corrosive: it can burn skin and eyes. Wear gloves, keep it away from children, and never mix "
                 "it with other cleaners.",
    "cleaner": "Keep it away from children and pets, use it with fresh air, and do not mix it with other cleaners.",
    "pods": "Keep detergent pods locked away from children: they look like sweets and are poisonous if bitten or "
            "swallowed.",
    "pool": "Keep pool chemicals dry, closed and away from children. Never mix different pool chemicals, and add the "
            "chemical to water, never water to the chemical: they can catch fire or give off toxic gas.",
    "pesticide": "Read and follow its label. Keep children and pets away until it has dried, and store it locked "
                 "up in its own container.",
    "fertiliser": "Keep it away from children and pets, and wash your hands after using it.",
    "bait": "It holds poison: keep it away from children and pets, and use tamper-resistant bait stations.",
    "flammable": "It is flammable: use it with fresh air, far from flames and sparks, and keep it away from "
                 "children.",
    "aerosol": "It is under pressure and often flammable: keep it away from heat and flames, and never puncture or "
               "burn the can.",
    "oily rags": "Rags soaked in linseed oil, tung oil, oil stains or oil varnish can catch fire by themselves as "
                 "they dry: lay them flat outdoors to dry, or keep them in a closed metal can filled with water.",
    "antifreeze": "Antifreeze is poisonous and tastes sweet: keep it away from children and pets, and wipe up every "
                  "spill.",
    "auto fluid": "It is poisonous: keep it away from children and pets, and wipe up spills.",
    "oil": "Keep it away from children, wipe up spills, and take used oil to a recycling point.",
    "glue": "Some glues bond skin in seconds and give off fumes: keep them away from eyes and children, and use "
            "them with fresh air.",
    "propane": "It is flammable gas under pressure: keep the cylinder upright, outdoors and away from heat; never "
               "store or use it indoors.",
    "fuel": "Petrol (gasoline) and other fuels are highly flammable: store them outdoors or in a shed, in a proper "
            "fuel can, far from flames.",
    "battery": "Do not throw batteries in the household bin: take them to a battery recycling point.",
    "button battery": "Keep button and coin batteries away from children: a swallowed one can burn through the "
                      "throat in two hours. If one is swallowed, go to an emergency department at once.",
    "car battery": "A car battery holds acid and can give off explosive gas: keep sparks and flames away, and wear "
                   "eye protection.",
    "ice melt": "Keep it away from pets' paws and mouths, and wash it off skin.",
    "cement": "Wet cement and mortar are caustic and can burn skin: wear gloves and eye protection, and wash skin at "
              "once.",
    "gas cylinder": "It holds gas under high pressure: keep it upright and chained or strapped, away from heat; a "
                    "damaged valve can make it a dangerous projectile.",
    "insulation": "Glass and mineral wool can irritate skin, eyes and lungs: wear gloves, long sleeves and a dust "
                  "mask when handling it.",
    "photo": "Photographic chemicals can irritate skin and eyes: wear gloves, use them with fresh air, and keep them "
             "away from food and children.",
}

# ----------------------------------------------------------------- answers, from the category names

# (pattern on a category name, question, answer, safety key or ""). A file gets the rows of every rule its own
# category (the one it was found in) or any of its other categories matches; for each question the first matching
# rule wins (so the more particular rules come first). Answers about a general topic say "a picture of ...": the
# category holds the product, its container and the product in use.
RULES = [
    # household cleaners
    (r"\bbleach bottles\b", WHAT_Q, "This is a bottle of bleach.", "bleach"),
    (r"\bbleach(es)?\b(?! bypass)", WHAT_Q, "This is a picture of bleach: the cleaning and whitening liquid, "
                                           "usually sold in plastic jugs.", "bleach"),
    (r"\btoilet cleaners?\b", WHAT_Q, "This is a toilet cleaner, usually a bottle with a bent neck for squirting "
                                      "under the rim.", "corrosive"),
    (r"\boven cleaners?\b", WHAT_Q, "This is an oven cleaner.", "corrosive"),
    (r"\bdrain cleaners?\b", WHAT_Q, "This is a drain cleaner.", "corrosive"),
    (r"\b(laundry|detergent) (pods|pacs|capsules|tablets)\b", WHAT_Q,
     "These are laundry detergent pods: small soft packets of detergent that dissolve in the wash.", "pods"),
    (r"\blaundry detergents?\b|\bwashing powders?\b", WHAT_Q, "This is laundry detergent, for washing clothes.",
     "cleaner"),
    (r"\bfabric softeners?\b", WHAT_Q, "This is fabric softener, added to the wash to make clothes soft.",
     "cleaner"),
    (r"\b(dishwashing liquids?|washing-up liquids?|dish soaps?)\b", WHAT_Q,
     "This is dishwashing liquid (dish soap), for washing dishes by hand.", "cleaner"),
    (r"\bdishwasher detergents?\b", WHAT_Q, "This is dishwasher detergent.", "cleaner"),
    (r"\bglass cleaners?\b", WHAT_Q, "This is a glass and window cleaner, usually in a spray bottle.", "cleaner"),
    (r"\bdisinfectant wipes\b", WHAT_Q, "These are disinfectant wipes, in a tub or pack you pull them from.",
     "cleaner"),
    (r"\bhand sanitizers?\b|\bhand sanitisers?\b", WHAT_Q, "This is hand sanitiser, an alcohol gel or liquid for "
                                                           "cleaning hands without water.", "flammable"),
    (r"\bdisinfectants?\b", WHAT_Q, "This is a picture of a disinfectant: a cleaner that kills germs on surfaces.",
     "cleaner"),
    (r"\bair fresheners?\b", WHAT_Q, "This is an air freshener.", "aerosol"),
    (r"\bdetergents?\b", WHAT_Q, "This is a picture of a detergent (a soap-like cleaner).", "cleaner"),
    (r"\b(cleaning products|cleaning agents|household chemicals|(?<!vacuum )(?<!pipe )(?<!steam )cleaners)\b", WHAT_Q,
     "This is a picture of household cleaning products.", "cleaner"),
    # pool and spa
    (r"\bpool test kits?\b|\b(pool|swimming pool) water test\w*\b", WHAT_Q,
     "This is a pool water test kit, for checking the chlorine and pH of the water.", ""),
    (r"\b(swimming )?pool chemicals?\b|\bpool chlorine\b|\bchlorine tablets?\b|\bpool chlorinators?\b", WHAT_Q,
     "This is a picture of swimming pool chemicals, such as chlorine tablets or pool shock.", "pool"),
    # lawn and garden
    (r"\bfertili[sz]er (bags|sacks)\b", WHAT_Q, "This is a bag of fertiliser.", "fertiliser"),
    (r"\bfertili[sz]er spreaders?\b", WHAT_Q, "This is a fertiliser spreader, which scatters fertiliser evenly on a "
                                              "lawn or field.", ""),
    (r"\bfertili[sz]ers?\b", WHAT_Q, "This is a picture of fertiliser: plant food spread on soil or lawns, sold in "
                                     "bags, boxes and bottles.", "fertiliser"),
    (r"\bpesticide application\b|\bspraying (of )?pesticides?\b|\bcrop spraying\b", WHAT_Q,
     "This shows a pesticide being sprayed or spread.", "pesticide"),
    (r"\broundup\b", WHAT_Q, "This is Roundup, a weed killer (herbicide).", "pesticide"),
    (r"\bherbicides?\b|\bweed ?killers?\b", WHAT_Q, "This is a picture of a weed killer (herbicide): the product, "
                                                    "its container or its use.", "pesticide"),
    (r"\binsect repellents?\b|\bmosquito repellents?\b", WHAT_Q, "This is an insect repellent.", "pesticide"),
    (r"\binsecticides?\b|\bbug sprays?\b", WHAT_Q, "This is a picture of an insect killer (insecticide): the "
                                                   "product, its container or its use.", "pesticide"),
    (r"\bfungicides?\b", WHAT_Q, "This is a picture of a fungicide, which kills moulds and plant diseases: the "
                                 "product, its container or its use.", "pesticide"),
    (r"\bpesticides?\b", WHAT_Q, "This is a picture of a pesticide: the product, its container or its use.",
     "pesticide"),
    (r"\bgrass seeds?\b", WHAT_Q, "This is grass seed, for sowing a lawn.", ""),
    (r"\bmulch(es|ing)?\b", WHAT_Q, "This is mulch: shredded bark, wood chips or similar spread over soil around "
                                    "plants to keep in moisture and keep down weeds.", ""),
    (r"\bpotting (soil|mix|compost)\b", WHAT_Q, "This is potting soil (potting mix), for plants in pots.", ""),
    (r"\b(road salt|rock salt|ice melt\w*|de-?icing salt)\b", WHAT_Q,
     "This is road salt or ice melt, spread on paths and roads to melt ice.", "ice melt"),
    # paints
    (r"\bspray (cans|paint cans)\b|\baerosol (paint|spray) cans\b|\bspray paints?\b", WHAT_Q,
     "This is a spray can (an aerosol can), such as spray paint.", "aerosol"),
    (r"\bpaint (cans|tins|buckets|pails)\b", WHAT_Q, "This is a can of paint.", "flammable"),
    (r"\b(acrylic|oil|watercolou?r) paints?\b|\bpaint tubes\b|\btubes of paint\b", WHAT_Q,
     "These are artists' paints, often in tubes.", ""),
    (r"\bprimers? \(paint\)|\bpaint primers?\b", WHAT_Q, "This is paint primer, the first coat under paint.",
     "flammable"),
    (r"\bpaint (samples|swatches|chips|cards)\b|\bcolou?r charts\b", WHAT_Q,
     "These are paint colour samples (swatches), for choosing a colour.", ""),
    # oils and lubricants
    (r"\bwd-40\b", WHAT_Q, "This is WD-40, a spray lubricant and penetrating oil.", "aerosol"),
    (r"\bgrease guns?\b", WHAT_Q, "This is a grease gun, a hand pump that pushes grease into machine fittings.", ""),
    (r"\b(motor|engine) oils?\b", WHAT_Q, "This is motor oil (engine oil), usually sold in plastic bottles marked "
                                          "with its grade, such as 5W-30.", "oil"),
    (r"\boil cans\b", WHAT_Q, "This is an oil can, for oiling machines.", "oil"),
    (r"\bgrease \(lubricant\)|\blubricating grease\b", WHAT_Q, "This is lubricating grease.", "oil"),
    (r"\blubricants?\b", WHAT_Q, "This is a picture of a lubricant, such as oil or grease.", "oil"),
    # automotive fluids
    (r"\bantifreeze\b|\b(engine )?coolants?\b", WHAT_Q, "This is antifreeze (engine coolant).", "antifreeze"),
    (r"\bbrake fluids?\b", WHAT_Q, "This is brake fluid.", "auto fluid"),
    (r"\b(windshield|windscreen) washer fluids?\b", WHAT_Q, "This is windshield washer fluid.", "auto fluid"),
    # adhesives and sealants
    (r"\bsilicone sealants?\b", WHAT_Q, "This is silicone sealant, a rubbery paste for sealing joints around baths, "
                                        "sinks and windows.", "glue"),
    (r"\bcaulk\w*\b", WHAT_Q, "This is caulk (sealant) or a caulking gun, for filling joints and gaps.", "glue"),
    (r"\bsuper ?glue\b|\bcyanoacrylate\b", WHAT_Q, "This is super glue (cyanoacrylate).", "glue"),
    (r"\bepoxy\b", WHAT_Q, "This is epoxy, a two-part glue or resin that sets hard.", "glue"),
    (r"\bglue sticks\b", WHAT_Q, "These are glue sticks.", ""),
    (r"\b(adhesives?|glues?)\b", WHAT_Q, "This is a picture of glue or another adhesive.", "glue"),
    # solvents
    (r"\bturpentine\b", WHAT_Q, "This is turpentine, a solvent for thinning oil paint and cleaning brushes.",
     "flammable"),
    (r"\bwhite spirit\b|\bmineral spirits\b|\bpaint thinners?\b", WHAT_Q,
     "This is paint thinner (mineral spirits or white spirit).", "flammable"),
    (r"\bacetone\b", WHAT_Q, "This is acetone, a strong solvent (as in some nail polish removers).", "flammable"),
    (r"\bsolvents?\b", WHAT_Q, "This is a picture of a solvent.", "flammable"),
    # pest control
    (r"\bmouse ?traps?\b|\bmousetraps\b|\brat traps?\b", WHAT_Q, "This is a mousetrap.", ""),
    (r"\b(rodent )?bait stations?\b|\brat poison\b|\brodenticides?\b", WHAT_Q,
     "This is a rodent bait station or rat poison.", "bait"),
    (r"\bfly ?papers?\b|\bsticky traps?\b", WHAT_Q, "This is a sticky insect trap (fly paper).", ""),
    (r"\binsect traps?\b|\bant traps?\b", WHAT_Q, "This is an insect trap.", ""),
    # batteries
    (r"\b(button|coin) cells?\b|\bbutton batter(y|ies)\b", WHAT_Q, "These are button batteries (coin cells).",
     "button battery"),
    (r"\b(car|automotive|lead-acid) batter(y|ies)\b", WHAT_Q, "This is a car battery (a lead-acid battery).",
     "car battery"),
    (r"\b(AAA?|9-volt|9 volt|C|D) batteries\b", WHAT_Q, "These are household batteries.", "battery"),
    # fuel and gas
    (r"\bpropane (cylinders|tanks|bottles)\b|\blpg cylinders\b", WHAT_Q, "This is a propane cylinder (a propane "
                                                                          "tank), as used for barbecue grills.",
     "propane"),
    (r"\b(gasoline|petrol|fuel) (cans|containers)\b", WHAT_Q, "This is a fuel can (a gas can).", "fuel"),
    (r"\bjerry ?cans\b", WHAT_Q, "This is a jerrycan, a sturdy can for fuel or water.", "fuel"),
    (r"\bcharcoal briquettes?\b", WHAT_Q, "These are charcoal briquettes, for barbecue grills.", ""),
    (r"\b(kerosene|oil|paraffin) (lamps?|lanterns?)\b", WHAT_Q, "This is an oil lamp (a kerosene lamp).", "flammable"),
    (r"\bkerosene\b(?! (heaters?|stoves?))|\blamp oil\b|\bparaffin oil\b", WHAT_Q, "This is kerosene (lamp oil or "
                                                                                    "paraffin).", "flammable"),
    (r"\b(acetylene|oxygen|argon|welding gas|shielding gas) cylinders\b", WHAT_Q,
     "This is a gas cylinder, such as a welding gas cylinder.", "gas cylinder"),
    (r"\bgas (cylinders|bottles)\b", WHAT_Q, "This is a gas cylinder.", "gas cylinder"),
    # fire extinguishers by type (CLASS_Q) and what they are
    (r"\b(carbon dioxide|co2) fire extinguishers\b", CLASS_Q,
     "This is a carbon dioxide (CO2) fire extinguisher, for flammable liquid fires and electrical fires (classes B "
     "and C in the US and Canada); it has a wide horn instead of a hose nozzle.", ""),
    (r"\b(powder|dry chemical|dry powder|abc) fire extinguishers\b", CLASS_Q,
     "This is a dry chemical (powder) fire extinguisher. Most are ABC extinguishers, for ordinary materials, "
     "flammable liquids and electrical fires; the label shows which classes.", ""),
    (r"\bwater fire extinguishers\b", CLASS_Q,
     "This is a water fire extinguisher, for ordinary materials like wood, paper and cloth (class A) only; never use "
     "it on electrical, grease or burning liquid fires.", ""),
    (r"\bfoam fire extinguishers\b", CLASS_Q,
     "This is a foam fire extinguisher, for ordinary materials and flammable liquids (classes A and B).", ""),
    (r"\bwet chemical fire extinguishers\b|\bclass k fire extinguishers\b", CLASS_Q,
     "This is a wet chemical (class K) fire extinguisher, for kitchen fires in cooking oil and fat.", ""),
    (r"\bhalon fire extinguishers\b", CLASS_Q,
     "This is a halon fire extinguisher, an older kind for electrical and liquid fires, now rarely made.", ""),
    # building products
    (r"\b(cement|concrete|mortar) (bags|sacks|mixes)\b|\bbags of (cement|concrete)\b", WHAT_Q,
     "This is a bag of cement, concrete mix or mortar.", "cement"),
    (r"\b(joint|drywall) compound\b", WHAT_Q, "This is drywall joint compound (mud).", ""),
    (r"\b(fiberglass|fibreglass|glass wool|mineral wool|rock wool) insulation\b|\b(glass|mineral|rock) wool\b",
     WHAT_Q, "This is insulation: glass or mineral wool, in rolls or batts.", "insulation"),
    (r"\bspray foam\b|\bpolyurethane foam insulation\b", WHAT_Q, "This is spray foam insulation.", "aerosol"),
    (r"\basphalt shingles\b|\broofing (felt|tar|shingles)\b", WHAT_Q, "These are roofing materials, such as "
                                                                       "asphalt shingles or roofing felt.", ""),
    # other products
    (r"\bphotographic (chemicals|developers?|fixers?)\b|\bdarkroom chemicals\b", WHAT_Q,
     "These are photographic darkroom chemicals, such as developer and fixer.", "photo"),
    (r"\baquarium (chemicals|water treatments?|test kits?)\b", WHAT_Q,
     "This is an aquarium water treatment or test kit.", ""),
    (r"\bsolder\b(?!ing iron)", WHAT_Q, "This is solder, a soft metal wire melted to join electrical parts.", ""),
    (r"\b(soldering )?flux\b", WHAT_Q, "This is soldering flux.", "corrosive"),
    (r"\banti-?fouling( paints?)?\b", WHAT_Q, "This is antifouling paint, used on boat hulls to stop weed and "
                                              "barnacles growing.", "pesticide"),
    (r"\b(de-?wormers|anthelmintics?)\b", WHAT_Q, "This is an animal dewormer.", ""),
    (r"\bteat dips?\b", WHAT_Q, "This is a teat dip, used on dairy animals' udders.", ""),
    (r"\bfuel additives?\b|\bfuel stabili[sz]ers?\b", WHAT_Q, "This is a fuel additive or fuel stabiliser.",
     "flammable"),
]
RULES = [(re.compile(p, re.I), q, a, k) for p, q, a, k in RULES]

# What the finishes and surfaces look like (commons_finishes_in_use): (pattern, question, answer, safety key).
FINISH_RULES = [
    (r"\bverdigris\b", SURFACE_Q, "This shows verdigris: the green or blue-green crust that forms on copper, brass "
                                  "and bronze as they corrode.", ""),
    (r"\bpatina(s|tion)?\b", SURFACE_Q, "This shows a patina: a dull film, often green, brown or black, that forms "
                                        "on metal over years outdoors.", ""),
    (r"\brust(ed|y|ing)?\b(?!-oleum| belt| \(fung| fungi| diseases?)", SURFACE_Q,
     "This shows rust: rough, flaky, orange-brown iron oxide that forms on iron and steel left wet. It eats the "
     "metal away: scaly or bubbling rust means the metal under it is weakening.", ""),
    (r"\bcorro(sion|ded)\b", SURFACE_Q, "This shows corroded metal: its surface is eaten away, pitted, crusted or "
                                        "discoloured.", ""),
    (r"\b(hot-dip )?galvani[sz](ed|ing|ation)\b", FINISH_Q,
     "This is galvanised steel: coated with zinc, a dull grey or silvery finish, often with a crystal pattern "
     "(spangle), that protects the steel from rust.", ""),
    (r"\bpowder coat(ed|ing)\b", FINISH_Q, "This metal is powder-coated: a tough, even, baked-on plastic paint, "
                                           "usually smooth and slightly glossy.", ""),
    (r"\bchrom(e|ium)[- ]plat(ed|ing)\b|\bchrome (finish|trim|bumpers?)\b", FINISH_Q,
     "This is chrome plating: a mirror-bright, slightly bluish silver coat on metal or plastic.", ""),
    (r"\bbrushed (metal|steel|aluminium|aluminum|stainless steel)\b", FINISH_Q,
     "This is brushed metal: fine parallel lines rubbed into the surface give it a soft satin sheen.", ""),
    (r"\banodi[sz](ed|ing)\b", FINISH_Q, "This is anodised aluminium: a hard matt or satin surface layer, often "
                                         "dyed a colour.", ""),
    (r"\bshellac\b", FINISH_Q, "This shows shellac, a traditional wood finish made from lac resin dissolved in "
                               "alcohol; it dries to a warm, amber, glossy coat.", "flammable"),
    (r"\bfrench polish\w*\b", FINISH_Q, "This shows French polish: many thin coats of shellac rubbed on by hand to a "
                                        "deep, mirror-like gloss.", "flammable"),
    (r"\blacquer(ed|s)?\b", FINISH_Q, "This shows lacquer, a hard, fast-drying finish, often very glossy.",
     "flammable"),
    (r"\bvarnish(ed|es)?\b", FINISH_Q, "This shows varnish: a clear, hard protective coat, usually glossy, over wood "
                                       "(in its tin, or applied).", "oily rags"),
    (r"\bpolyurethane\b", FINISH_Q, "This shows polyurethane varnish, a tough clear plastic finish for wood floors and "
                                    "furniture, from matt to high gloss.", "flammable"),
    (r"\b(linseed|tung|danish) oil\b", FINISH_Q, "This shows a drying oil finish (such as linseed or tung oil): it "
                                                 "soaks into wood, darkens it a little and leaves a soft, low sheen.",
     "oily rags"),
    (r"\bwood stains?\b|\bstained wood\b", FINISH_Q, "This shows wood stain, which colours wood while letting its "
                                                     "grain show through.", "oily rags"),
    (r"\bwax(ed)? (wood|furniture|finish)\b|\bwood wax\b", FINISH_Q, "This shows a wax finish on wood: a soft, low "
                                                                      "sheen.", ""),
    (r"\b(peeling|flaking|chipped|chipping|cracked) paint\b", SURFACE_Q,
     "This shows peeling or flaking paint: the old paint is cracking and lifting off the surface. Old paint may "
     "contain lead: do not sand or scrape it without testing.", ""),
    (r"\bhouse painting\b|\bpainting (walls|houses)\b", WHAT_Q, "This shows a house or wall being painted.", ""),
    (r"\b(gloss|glossy|high-gloss) paint\b", FINISH_Q, "This is a gloss paint finish: shiny and reflective, easy to "
                                                       "wipe clean, showing every bump in the surface.", ""),
    (r"\b(matte|matt|flat) paint\b", FINISH_Q, "This is a flat (matt) paint finish: no shine at all, hiding bumps in "
                                               "the wall, harder to wipe clean.", ""),
    (r"\b(mou?ld|mildew)\b.*\b(walls?|ceilings?|buildings?|bathrooms?|houses?)\b|\bblack mou?ld\b|\bmildew\b",
     SURFACE_Q, "This shows mould or mildew: dark (often black, green or grey) spotty growth, usually where it is "
                "damp. Unlike a stain, it spreads in fuzzy spots and smells musty.", ""),
    (r"\befflorescence\b", SURFACE_Q, "This shows efflorescence: a white, powdery crust of salts left on brick, "
                                      "concrete or stone as water dries out of it.", ""),
    (r"\b(fresh|wet) concrete\b|\bconcrete (pouring|placing|finishing|curing)\b", SURFACE_Q,
     "This shows fresh concrete being poured, smoothed or left to cure (harden).", "cement"),
    (r"\bspalling\b|\bconcrete (cracks|damage)\b|\bcracked concrete\b", SURFACE_Q,
     "This shows damaged concrete: cracked, or with pieces flaking off its surface (spalling).", ""),
    (r"\bgrout\b", SURFACE_Q, "This shows grout, the hard paste filling the joints between tiles.", "cement"),
    (r"\bmortar \(masonry\)|\bmortar joints\b|\bpointing \(masonry\)", SURFACE_Q,
     "This shows mortar, the cement paste in the joints between bricks or stones.", "cement"),
    (r"\boil (stains|leaks|spots)\b", SURFACE_Q, "This shows oil stains: dark, glossy or rainbow-sheened patches "
                                                 "where oil has dripped or leaked.", ""),
    (r"\b(algae|algal) in (swimming )?pools\b|\bgreen (swimming )?pools\b", SURFACE_Q,
     "This shows a swimming pool with algae: the water is green and cloudy and needs treating before anyone swims.",
     "pool"),
    (r"\bpesticide application\b|\bspraying (of )?pesticides?\b|\bcrop spraying\b", WHAT_Q,
     "This shows a pesticide being sprayed or spread.", "pesticide"),
    (r"\bfertili[sz]er (application|spreading)\b|\bspreading fertili[sz]er\b", WHAT_Q,
     "This shows fertiliser being spread.", "fertiliser"),
]
FINISH_RULES = [(re.compile(p, re.I), q, a, k) for p, q, a, k in FINISH_RULES]

# Brand categories (Commons categories of a brand's own products): {pattern on a category name: the brand}. Said only
# when the file is in that category AND another rule says what the product is.
BRANDS = {r"^WD-40\b": "WD-40", r"^Roundup\b": "Roundup", r"^Clorox\b": "Clorox", r"^Lysol\b": "Lysol",
          r"^Windex\b": "Windex", r"^Drano\b": "Drano", r"^Tide \(": "Tide", r"^Mr\. Clean\b": "Mr. Clean",
          r"^Comet \(clean": "Comet", r"^Ajax \(clean": "Ajax", r"^Dawn \(": "Dawn", r"^Javex\b": "Javex",
          r"^Rust-Oleum\b": "Rust-Oleum", r"^Krylon\b": "Krylon", r"^Valvoline\b": "Valvoline",
          r"^Castrol\b": "Castrol", r"^Pennzoil\b": "Pennzoil", r"^Quaker State\b": "Quaker State",
          r"^Mobil 1\b": "Mobil 1", r"^Prestone\b": "Prestone", r"^Gorilla Glue\b": "Gorilla Glue",
          r"^Elmer's\b": "Elmer's", r"^Loctite\b": "Loctite", r"^Duracell\b": "Duracell", r"^Energizer\b": "Energizer",
          r"^Kingsford\b": "Kingsford", r"^Miracle-Gro\b": "Miracle-Gro", r"^Raid \(": "Raid",
          r"^Brasso\b": "Brasso", r"^Pledge \(": "Pledge", r"^OxiClean\b": "OxiClean"}
BRANDS = {re.compile(p): b for p, b in BRANDS.items()}

# Subcategories that are not photos of the product or surface: drawings, molecules and structures, chemistry,
# history and art, factories and companies, people, events, and places.
SKIP = re.compile(r"\b(diagrams?|drawings?|structural formulae?|skeletal formulae?|molecules?|molecular|3D models?|"
                  r"ball-and-stick|space-filling|crystal structures?|chemical structures?|spectra|chemistry|"
                  r"compounds?|isomers?|salts of|ions|minerals?|art|artworks?|paintings?|illustrations?|history|"
                  r"historical|advertisements?|advertising|logos?|videos?|maps?|museums?|people|persons|portraits|"
                  r"companies|factories|plants|headquarters|buildings by|shops?|stores?|stations?|vehicles?|ships?|"
                  r"aircraft|cars|trucks|warfare|weapons?|military|accidents?|disasters?|spills?|pollution|"
                  r"protests?|by country|by year|quality images|in literature|music|films?|fung(i|us)|plant "
                  r"diseases?|pathogens?)\b", re.I)
# For the symbols pack: drawings and placards on vehicles are wanted; only these subcategories are left out.
SYMBOL_SKIP = re.compile(r"\b(by country|quality images|people|persons|companies|history|museums?)\b|"
                         + re.escape(GHS_CATEGORY), re.I)       # safety_signs' nine drawings: not repeated
# Words that leave a file out: poisonings, injuries, deaths, drug labs, explosives and weapons (everyday packs).
HARM = re.compile(r"\b(poison(ed|ing)s?|overdoses?|suicides?|killed|dead|deaths?|died|fatal\w*|injur\w*|burns? "
                  r"victims?|wounded|blood\w*|corpses?|meth(amphetamine)? labs?|drug labs?|clandestine|explosives?|"
                  r"bombs?|IEDs?|napalm|chemical weapons?|nerve agents?|mustard gas|agent orange|warfare|"
                  r"weapons?|terror\w*|arson|molotov)\b", re.I)


def topic(root, depth=1):
    """One Commons topic: its root category and how many levels of subcategories to walk."""
    return {"root": root, "depth": depth}


# The topics: Commons categories checked to exist on 2026-11-21 (with the number of files directly in each). Many
# subjects asked for have no Commons category of their own (pool chemicals, laundry detergents, wood stains, paint
# sheens, mould on walls, grout, oil stains, pool algae, anodising, DOT placards, among others checked): their
# pictures come only from the subcategories walked here, or not at all.
PACKAGING_TOPICS = [topic(c, d) for c, d in [
    # household cleaners
    ("Bleach bottles", 0), ("Toilet cleaners", 1), ("Oven cleaners", 0), ("Cleaning products", 1), ("Detergents", 1),
    ("Dishwashing liquids", 1), ("Disinfectants", 1), ("Hand sanitizers", 1), ("Household chemicals", 1),
    ("Air fresheners", 1),
    # lawn and garden
    ("Fertilizers", 1), ("Fertilizer bags", 0), ("Herbicides", 1), ("Roundup (herbicide)", 1), ("Insecticides", 1),
    ("Fungicides", 1), ("Pesticides", 1), ("Insect repellents", 1), ("Grass seed", 1), ("Mulch", 1),
    ("Road salt", 1), ("Rock salt", 1),
    # paints
    ("Paint cans", 0), ("Spray cans", 1), ("Paint tubes", 1),
    # oils, lubricants and automotive fluids
    ("Motor oil", 1), ("WD-40", 1), ("Grease guns", 0), ("Lubricants", 1), ("Antifreeze", 1), ("Brake fluid", 0),
    ("Fuel additives", 1),
    # adhesives, sealants, solvents
    ("Adhesives", 1), ("Silicone sealant", 1), ("Caulking guns", 0), ("Glue sticks", 0), ("Solvents", 1),
    ("Turpentine", 1), ("Acetone", 1),
    # pest control
    ("Mousetraps", 1), ("Rodent bait stations", 0), ("Insect traps", 1),
    # batteries, fuel and gas, fire extinguishers
    ("AA batteries", 1), ("AAA batteries", 1), ("Button cells", 1), ("Propane cylinders", 1), ("Jerrycans", 1),
    ("Charcoal briquettes", 1), ("Kerosene", 1), ("Gas cylinders", 1), ("Acetylene cylinders", 0),
    ("Oxygen cylinders", 1), ("Carbon dioxide fire extinguishers", 1), ("Water fire extinguishers", 0),
    ("Foam fire extinguishers", 0),
    # building, workshop and other products
    ("Cement bags", 1), ("Mineral wool", 1), ("Photographic chemicals", 1),
]]
FINISH_TOPICS = [topic(c, d) for c, d in [
    ("Rust", 1), ("Corrosion", 1), ("Verdigris", 1), ("Galvanization", 1), ("Hot-dip galvanizing", 1),
    ("Powder coating", 1), ("Chrome plating", 1), ("Brushed metal", 1),
    ("Varnish", 1), ("Shellac", 1), ("Lacquer", 1), ("Linseed oil", 1), ("Tung oil", 0),
    ("Peeling paint", 1), ("House painting", 1), ("Mildew", 1), ("Efflorescence", 1), ("Spalling", 1),
    ("Mortar joints", 1), ("Pesticide application", 1),
]]


def walk(s, root, depth, skip=SKIP):
    """[category] for a topic: the root and its subcategories down to depth levels, leaving out those skip names,
    each once."""
    found, level = [root], [root]
    for _ in range(depth):
        nxt = []
        for c in level:
            if listing_out_of_time():
                return found
            for sub in commons_members(s, c, "subcat"):
                name = sub.split(":", 1)[-1]
                if name not in found and not skip.search(name):
                    found.append(name)
                    nxt.append(name)
        level = nxt
    return found


def rule_rows(categories, rules, title=""):
    """The rows the rules give a file from its categories (the one it was found in first): one per question, the
    first matching rule winning. A product row ends with its safety note, which is also asked on its own ("How do I
    handle this safely?"). title: the file's title, also matched (a symbol's meaning is in its own name)."""
    answers, notes = collections.OrderedDict(), []
    for c in list(categories) + ([title] if title else []):
        for pattern, question, answer, key in rules:
            if pattern.search(c) and question not in answers:
                answers[question] = answer
                if key and key not in notes:
                    notes.append(key)
    rows = []
    for question, answer in answers.items():
        rows.append({"question": question, "answer": answer})
    if notes and rows:
        note = " ".join(SAFETY[k] for k in notes[:2])
        rows[0] = dict(rows[0], answer=rows[0]["answer"] + " " + note)
        rows.append({"question": SAFE_Q, "answer": note})
    return rows


def brand_rows(categories, rows):
    """"What brand is this?" when the file is in a brand's own category and another rule said what it is."""
    if not rows:
        return []
    for c in categories:
        for pattern, brand in BRANDS.items():
            if pattern.search(c):
                return [{"question": BRAND_Q, "answer": f"The brand is {brand}."}]
    return []


def caption_row(text):
    """"Describe this picture." with the file's own English caption, when it is a real, respectful description
    (this is where label text appears, when the uploader wrote it)."""
    text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else (text or "")
    if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
        return [{"question": DESCRIBE_Q, "answer": text}]
    return []


def file_rows(f, found_in, rules):
    """The rows of one Commons file (from commons_files): the rules' rows from the category it was found in and
    its other categories, the brand where its brand category says it, and its English caption; each with the
    credit and facts."""
    cats = [found_in] + [c for c in f["categories"] if c != found_in]
    title = f["title"].split(":", 1)[-1].rsplit(".", 1)[0]
    rows = rule_rows(cats, rules)
    rows += brand_rows(cats, rows)
    rows += caption_row(f.get("text", ""))
    facts = {"commons_category": found_in, "commons_title": title}
    return [dict(r, credit=f["credit"], facts=facts) for r in rows]


def refused(words):
    """Why a file is left out by its words, or ""."""
    if NUDE.search(words) or NOT_SHOWN.search(words):
        return "its words are about nudity, underwear or swimwear"
    if HARM.search(words):
        return "its words name a poisoning, an injury, a death, a drug lab, explosives or weapons"
    return ""


def topic_titles(s, t, seen, photos=True):
    """[(file title, the category it was found in)] for a topic, shuffled the same way each time (a different way on
    a top-up pass)."""
    found = {}
    for category in walk(s, t["root"], t["depth"], SKIP if photos else SYMBOL_SKIP):
        if listing_out_of_time():
            break
        for title in commons_members(s, category, "file"):
            if title not in seen and not (photos and NOT_A_PHOTO.search(title)):
                found.setdefault(title, category)
    files = list(found.items())
    pass_random(len(t["root"]) * 7907 + sum(map(ord, t["root"]))).shuffle(files)
    return files


def chem_commons(topics, rules, limit, prefix, key, row_maker=file_rows, mimes=("image/jpeg",), flatten=False,
                 photos=True, picture_making=False):
    """A Commons pack from topics, which take turns so each gets an even share. Each file's licence is checked
    (events_safety_packs.commons_files: CC0, public domain or CC BY only), files whose words name nudity or harm are
    left out, and a free file with no answer is set aside for a description. Returns the pack entries."""
    s, items, seen = session(), [], set()
    order = list(topics)
    random.Random(prefix).shuffle(order)
    share = max(3, math.ceil(limit * 1.15 / max(1, len(order))))
    want = int(limit * 1.15) + 2
    queues = [[t, None] for t in order]
    rounds = 0
    while len(items) < want and queues and rounds < 40:
        rounds += 1
        for q in list(queues):
            if len(items) >= want:
                break
            if listing_out_of_time():
                say(f"  {prefix}: stopped looking at half the time limit")
                queues = []
                break
            t, files = q
            try:
                if files is None:
                    files = topic_titles(s, t, seen, photos)
                    say(f"Commons {t['root']}: {len(files)} files")
                batch, q[1] = files[:share * 2], files[share * 2:]
                if not batch:
                    queues.remove(q)
                    continue
                found_in = dict(batch)
                got_files = commons_files(s, [title for title, _ in batch], mimes=mimes)
            except RuntimeError as e:          # Commons kept refusing: keep what was found and stop asking
                say(f"  {prefix}: {e} Keeping the {len(items)} pictures found so far.")
                queues = []
                break
            got = 0
            for f in got_files:
                title = f["title"]
                if got >= share or title in seen:
                    continue
                words = NOT_A_CHILD.sub(" ", f"{title} {f.get('text', '')} {' '.join(f['categories'])}")
                why = refused(words)
                if why:
                    considered(title, f["url"], why)
                    continue
                seen.add(title)
                rows = row_maker(f, found_in.get(title, t["root"]), rules)
                if not rows:
                    needs_description(file_name(prefix, title), f["url"], f["credit"], f["licence"],
                                      text=f.get("text", ""), title=title,
                                      reason="no label this pack can read and no English caption",
                                      page_url=f["credit"].rsplit(", ", 1)[-1],
                                      extra={"commons_category": found_in.get(title, t["root"]),
                                             "child": bool(CHILD.search(words)),
                                             "not_for_picture_making": not picture_making})
                    considered(title, f["url"], "no answer: set aside for a description")
                    continue
                items.append((file_name(prefix, title), f["url"], [mark_child(r, words) for r in rows]))
                got += 1
            if not q[1]:
                queues.remove(q)
    return finish(key, items[:want], limit, workers=3, pause=0.3, flatten=flatten)


def build_commons_household_chemicals(limit):
    """Household and garage products in their containers, with safety notes for the hazardous ones."""
    return chem_commons(PACKAGING_TOPICS, RULES, limit, "chem", "commons_household_chemicals")


def build_commons_finishes_in_use(limit):
    """Finishes, coatings, corrosion and products applied or in use."""
    return chem_commons(FINISH_TOPICS, FINISH_RULES, limit, "finish", "commons_finishes_in_use")


# ----------------------------------------------------------------- commons_hazard_symbols

WHMIS_1988 = {
    "A": "Class A, compressed gas: the container holds gas under pressure and may explode if heated or damaged.",
    "B": "Class B, flammable and combustible material: it can catch fire.",
    "C": "Class C, oxidizing material: it can make other things burn more fiercely or cause a fire.",
    "D1": "Class D1, poisonous and infectious material causing immediate and serious toxic effects: it can kill or "
          "harm quickly.",
    "D2": "Class D2, poisonous and infectious material causing other toxic effects: it can cause long-term harm, "
          "such as cancer or allergies.",
    "D3": "Class D3, biohazardous infectious material: it holds germs that can cause disease.",
    "E": "Class E, corrosive material: it can burn skin and eyes and eat away metal.",
    "F": "Class F, dangerously reactive material: it can react violently, for example with water or when shaken.",
}
DOT_CLASSES = {
    "1": "hazard class 1, explosives", "2": "hazard class 2, gases (flammable, non-flammable or poisonous)",
    "3": "hazard class 3, flammable liquids", "4": "hazard class 4, flammable solids",
    "5": "hazard class 5, oxidizers and organic peroxides", "6": "hazard class 6, poisonous (toxic) and infectious "
                                                                 "substances",
    "7": "hazard class 7, radioactive material", "8": "hazard class 8, corrosive substances",
    "9": "hazard class 9, miscellaneous dangerous goods (such as lithium batteries or dry ice)",
}
# The GHS pictograms by number, as safety_signs says them (events_safety_packs.GHS).
GHS_MEANINGS = {code[-1]: (code, meaning) for code, meaning in GHS.values()}
NFPA = ("This is an NFPA 704 hazard diamond (\"fire diamond\"), used in the US on buildings and tanks that hold "
        "chemicals. Its four squares rate the dangers from 0 (none) to 4 (severe): blue on the left for health, red at "
        "the top for flammability, yellow on the right for instability, and white at the bottom for special hazards "
        "such as W crossed out (do not use water) or OX (oxidizer).")
WHMIS_KIND = ("It is a WHMIS symbol: the Workplace Hazardous Materials Information System that Canada uses on the "
              "labels of hazardous products at work.")
DOT_KIND = ("It is a US Department of Transportation hazardous materials placard or label, a diamond shown on "
            "trucks, rail cars and packages to tell what danger they carry.")


# A title naming two classes ("Class A and B", "class 3/8"): neither meaning is said.
TWO_CLASSES = re.compile(r"\bclass(?:es)?[ _-]?(?:[A-F]|[1-9])(?:[ _-]?[123]|\.\d)?\s*(?:and|&|,|/|or|\+)\s*"
                         r"(?:class[ _-]?)?(?:[A-F]|[1-9])\b", re.I)


def symbol_rows(f, found_in, rules=None):
    """The rows of one symbol file: its meaning from its own title or category ("WHMIS Class D-2", "Hazard class 3
    placard", "NFPA 704"), else what kind of symbol it is; [] when none says. Never a guess: a WHMIS title naming
    two classes, or a placard naming two hazard classes, gives no meaning."""
    title = f["title"].split(":", 1)[-1].rsplit(".", 1)[0]
    cats = [found_in] + [c for c in f["categories"] if c != found_in]
    words = " ".join([title] + cats)
    rows = []
    whmis = re.findall(r"\bclass[ _-]?([A-F])(?:[ _-]?([123]))?\b", title, re.I) if re.search(r"whmis|simdut", words,
                                                                                               re.I) else []
    whmis = sorted({(a.upper() + b) if a.upper() == "D" and b else a.upper() for a, b in whmis})
    two = bool(TWO_CLASSES.search(title))          # "Class A and B": two classes named, so no meaning is said
    if two:
        whmis = []
    if len(whmis) == 1 and whmis[0] in WHMIS_1988:
        rows.append({"question": SYMBOL_Q, "answer": f"This is the WHMIS 1988 symbol for {WHMIS_1988[whmis[0]]}"})
    dot = set(re.findall(r"\b(?:hazard |dot |un |division |hazmat )?class[ _-]?([1-9])(?:\.\d)?\b|\bdangclass[ _-]?"
                         r"([1-9])|transport pictogram\s*-\s*([1-9])\b", title, re.I)) \
        if re.search(r"placard|hazmat|dangerous goods|hazardous materials|transport pictogram|dangclass|\bDOT\b",
                     words, re.I) else set()
    dot = {d for group in dot for d in group if d}
    if two:
        dot = set()
    if len(dot) == 1 and not whmis:
        rows.append({"question": SYMBOL_Q, "answer": f"This is the hazardous materials placard for "
                                                     f"{DOT_CLASSES[dot.pop()]}."})
    ghs = sorted(set(re.findall(r"\bGHS[ _-]?0?([1-9])\b", title, re.I)))
    if len(ghs) == 1 and not (whmis or dot or two):
        code, meaning = GHS_MEANINGS[ghs[0]]
        rows.append({"question": SYMBOL_Q, "answer": f"This is the GHS hazard pictogram {code}: {meaning}. GHS "
                                                     f"pictograms are used on chemical labels, in red diamonds."})
    if re.search(r"\bNFPA[ _-]?704\b|fire diamond", words, re.I):
        rows.append({"question": SYMBOL_Q if not rows else SYMBOL_KIND_Q, "answer": NFPA})
    if re.search(r"\bWHMIS\b|\bSIMDUT\b", words, re.I):
        rows.append({"question": SYMBOL_KIND_Q, "answer": WHMIS_KIND})
    elif re.search(r"placard|hazmat|hazardous materials (label|sign)", words, re.I):
        rows.append({"question": SYMBOL_KIND_Q, "answer": DOT_KIND})
    seen, out = set(), []
    for r in rows:
        if r["question"] not in seen:
            seen.add(r["question"])
            out.append(r)
    out += caption_row(f.get("text", "")) if out else []
    facts = {"commons_category": found_in, "commons_title": title}
    return [dict(r, credit=f["credit"], facts=facts) for r in out]


SYMBOL_TOPICS = [topic(c, d) for c, d in [
    ("WHMIS hazard symbols", 0), ("NFPA 704 images", 1), ("GHS pictograms", 1),
]]
GHS_DRAWINGS = re.compile(r"^File:GHS-pictogram-", re.I)       # safety_signs' nine drawings: not repeated


def build_commons_hazard_symbols(limit):
    """WHMIS symbols, US DOT hazmat placards, the NFPA 704 diamond and hazard symbols on packages, each meaning
    from the file's own title or category; drawings rendered by Commons and flattened onto white."""
    def rows(f, found_in, rules):
        """No GHS pictogram drawing (safety_signs has them)."""
        return [] if GHS_DRAWINGS.search(f["title"]) else symbol_rows(f, found_in)
    return chem_commons(SYMBOL_TOPICS, None, limit, "hazsym", "commons_hazard_symbols", row_maker=rows,
                        mimes=("image/svg+xml", "image/png", "image/jpeg"), flatten=True, photos=False,
                        picture_making=True)


# ----------------------------------------------------------------- the packs

COMMONS_CREDIT = ("Wikimedia Commons {what}: captions CC0; pictures CC0, public domain or CC BY, each with its author "
                  "and file page below. https://commons.wikimedia.org")
CHEMICAL_PACKS = {
    "commons_household_chemicals": (build_commons_household_chemicals, COMMONS_CREDIT.format(
        what="categories of household and garage products in their containers (cleaners, pool and garden chemicals, "
             "paints, oils, automotive fluids, glues, solvents, pest control, batteries, fuel and gas cylinders, fire "
             "extinguishers by type, building products), with safety notes for hazardous products")),
    "commons_finishes_in_use": (build_commons_finishes_in_use, COMMONS_CREDIT.format(
        what="categories of finishes and surfaces: rust, corrosion and verdigris, galvanised, powder-coated, "
             "chrome and brushed metal, wood finishes, peeling paint, mildew, efflorescence, spalling, mortar joints, "
             "and pesticides being applied")),
    "commons_hazard_symbols": (build_commons_hazard_symbols, COMMONS_CREDIT.format(
        what="categories of WHMIS hazard symbols, NFPA 704 images and GHS pictograms (not safety_signs' nine "
             "drawings); each meaning from the file's own title or category")),
}

# How many pictures a full build takes from each (Commons answers about one picture a second).
CHEMICAL_LIMITS = {
    "commons_household_chemicals": 2500,  # 59 topics: about 3,900 files directly in them, more in subcategories
    "commons_finishes_in_use": 2000,      # 20 topics: about 1,900 files directly in them (Rust alone about 770)
    "commons_hazard_symbols": 300,        # 3 topics of drawings and photos
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one household chemicals pack builder.")
    parser.add_argument("key", choices=sorted(CHEMICAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = CHEMICAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"{len(build_packs.NEEDS)} set aside for a description")
    return 0


if __name__ == "__main__":
    sys.exit(main())
