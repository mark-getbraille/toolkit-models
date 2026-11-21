"""The collection "Pet and livestock supplies (manuals)" (category key pet_livestock_supplies): its makers, their
access decisions, the official guidance pages it links, and the category itself (categories.py adds it to
CATEGORIES).

Why this collection exists (the owner's request of November 2026): a blind person who keeps a dog, a cat, fish,
birds, reptiles, chickens, horses or other livestock deserves the maker's own instructions for the things they use:
crates and carriers, aquarium filters, heaters and UVB lamps, egg incubators and brooders, clippers and nail
trimmers, automatic feeders and water fountains, electric fence chargers, stock tank heaters and waterers, horse tack
and flea and tick collars. Only pet and livestock products: the household pest-control products (rodent traps,
insecticides for the home, termite and weed products) belong to another collection and are never put in this one
(PET_EXCLUDE).

Where the manuals come from (an INDEX of facts and links only; each manual belongs to its maker):
  ia        the Internet Archive's manual collections, searched by the words in IA_WORDS (its documented search
            interface, as the other collections).
  makers    makers' own libraries (MAKERS). Each maker's robots.txt was read on 2026-11-21. None is read by the builder
            in this first version ("link"): the terms of use of these makers were not checked one by one, some sites
            refuse programs (HTTP 403), Midwest's robots.txt says "ai-train=no" and Elanco's labels site disallows every
            program. So each maker's own page is only listed, for the person to open in their browser.
  guidance  official pages (US government works) on pet products, read by the person: EPA's pet pesticide pages and
            its Pesticide Product Label System (the full EPA-accepted label of every registered flea and tick
            product), CDC's Healthy Pets and USDA APHIS's animal health pages. (Animal drug labels, such as
            DailyMed's and the FDA Green Book, are another collection's: the reference library's drug labels.)
The pictures of these products (in packaging and in use) are in the picture packs: packs/na_animal_packs.py
(na_domestic_animals: equipment and pet supplies), packs/packaged_goods_packs.py (pet food, cat litter and flea and
tick treatments sold on Amazon) and the kit's Open Pet Food Facts entries.
"""

# The kinds of product a document is about, from the words of its title (build_manuals.product_type with a maker's
# "types").
TYPES = [("incubator", "egg incubator"), ("hatcher", "egg incubator"), ("brooder", "brooder"),
         ("aquarium", "aquarium equipment"), ("filter", "aquarium equipment"), ("heater", "heater"),
         ("uvb", "reptile lamp"), ("terrarium", "terrarium"), ("vivarium", "terrarium"), ("clipper", "clipper"),
         ("trimmer", "clipper"), ("grooming", "grooming tool"), ("feeder", "feeder"), ("fountain", "water fountain"),
         ("waterer", "waterer"), ("crate", "crate or carrier"), ("kennel", "crate or carrier"),
         ("carrier", "crate or carrier"), ("pet door", "pet door"), ("fence", "fence or charger"),
         ("energizer", "fence or charger"), ("charger", "fence or charger"), ("collar", "collar"),
         ("harness", "harness"), ("saddle", "horse tack"), ("bridle", "horse tack"), ("halter", "horse tack"),
         ("litter", "litter box"), ("milking", "milking equipment"), ("chute", "livestock handling")]

# Words searched in the titles of the Internet Archive's manual collections.
IA_WORDS = ["aquarium filter", "aquarium heater", "aquarium", "terrarium", "egg incubator", "incubator", "brooder",
            "pet fountain", "automatic pet feeder", "pet feeder", "dog clipper", "pet clipper", "animal clipper",
            "horse clipper", "nail grinder", "dog crate", "pet carrier", "pet door", "dog door", "bark collar",
            "training collar", "pet containment", "electric fence", "fence charger", "fence energizer",
            "livestock waterer", "stock tank heater", "poultry waterer", "milking machine", "self-cleaning litter"]

# Never in this collection: household pest control (another collection's), sales papers (categories.NOT_A_MANUAL),
# and electric fences for people's property security.
PET_EXCLUDE = (r"rodent|rat\s+trap|mouse\s+trap|mice\s+trap|insecticide|termite|herbicide|weed\s+killer|"
               r"bug\s+zapper|mosquito\s+(?:trap|fogger)|roach\s+bait|security\s+fence|razor\s+wire")

ROBOTS = "robots.txt read 2026-11-21"
NOT_CHECKED = "its terms of use were not checked one by one, so nothing is read: its own page is listed"
REFUSES = "the site refuses programs (HTTP 403), robots.txt included: its home page is listed"

# The makers: the same fields as categories.MAKERS, plus category, prefix (of the index ids) and types.
_COMMON = dict(category="pet_livestock_supplies", prefix="pl", types=TYPES, documents="instructions")
PET_MAKERS = [dict(_COMMON, **m) for m in [
    # Crates, carriers, beds and bowls.
    dict(key="petmate", maker="Petmate", type="crate or carrier", access="link", library="https://www.petmate.com/",
         site="petmate.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    dict(key="midwest", maker="MidWest Homes for Pets", type="crate or carrier", access="link",
         library="https://www.midwestpetproducts.com/", site="midwestpetproducts.com",
         reason=f"{ROBOTS}: \"Content-Signal: search=yes,ai-train=no,use=reference\", an express reservation against "
                "AI training; nothing is read: its home page is listed"),
    # Aquarium and terrarium equipment.
    dict(key="tetra", maker="Tetra", type="aquarium equipment", access="link", library="https://www.tetra-fish.com/",
         site="tetra-fish.com", reason=f"{ROBOTS}: the site did not answer programs on 2026-11-21: its home page is "
                                       "listed"),
    dict(key="fluval", maker="Fluval", type="aquarium equipment", access="link", library="https://fluvalaquatics.com/",
         site="fluvalaquatics.com", reason=f"{ROBOTS}: {REFUSES}"),
    dict(key="aqueon", maker="Aqueon", type="aquarium equipment", access="link", library="https://www.aqueon.com/",
         site="aqueon.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    dict(key="zoo-med", maker="Zoo Med", type="reptile lamp", access="link", library="https://zoomed.com/",
         site="zoomed.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    # Clippers and grooming.
    dict(key="oster", maker="Oster (animal care)", type="clipper", access="link", library="https://www.oster.com/",
         site="oster.com", reason=f"{ROBOTS}: robots.txt allows most pages but the site refuses programs (HTTP 403): "
                                  "its home page is listed"),
    dict(key="andis", maker="Andis", type="clipper", access="link", library="https://www.andis.com/",
         site="andis.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    dict(key="wahl", maker="Wahl (animal)", type="clipper", access="link", library="https://wahlusa.com/",
         site="wahlusa.com", reason=f"{ROBOTS}: robots.txt allows most pages but the site refuses programs (HTTP 403): "
                                    "its home page is listed"),
    # Poultry incubators and livestock equipment.
    dict(key="brinsea", maker="Brinsea", type="egg incubator", access="link", library="https://www.brinsea.com/",
         site="brinsea.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    dict(key="little-giant", maker="Little Giant (Miller Manufacturing)", type="waterer", access="link",
         library="https://www.millermfg.com/", site="millermfg.com", reason=f"{ROBOTS}: allows all; {NOT_CHECKED}"),
    dict(key="tarter", maker="Tarter Farm and Ranch Equipment", type="livestock handling", access="link",
         library="https://tarterusa.com/", site="tarterusa.com",
         reason=f"{ROBOTS}: shuts out AI crawlers (GPTBot, CCBot, ClaudeBot) and the site refuses programs (HTTP 403): "
                "its home page is listed"),
    dict(key="weaver-leather", maker="Weaver Leather (Weaver Equine and Livestock)", type="horse tack",
         access="link", library="https://www.weaverleather.com/", site="weaverleather.com",
         reason=f"{ROBOTS}: the site answers with a redirect only; {NOT_CHECKED}"),
    # Pet electronics: fences, doors, feeders, fountains, collars.
    dict(key="petsafe", maker="PetSafe", type="feeder", access="link", library="https://www.petsafe.com/",
         site="petsafe.com", reason=f"{ROBOTS}: allows most pages; {NOT_CHECKED}"),
    # Flea and tick collars (Seresto; Elanco's US label site).
    dict(key="elanco", maker="Elanco (Seresto and other animal health products)", type="collar", access="link",
         library="https://www.elancolabels.com/", site="elancolabels.com",
         reason=f"{ROBOTS}: \"Disallow: /\" for every program: nothing is read; its label site is listed for the "
                "person to open (each product's EPA label is also in EPA's Pesticide Product Label System)"),
]]

# Official guidance linked from the collection (US government works; the person opens them).
PET_GUIDANCE = [
    dict(title="Pets and pesticides, flea and tick products (EPA)", url="https://www.epa.gov/pets",
         by="the US Environmental Protection Agency"),
    dict(title="Pesticide Product Label System: the EPA-accepted label of every registered product, flea and tick "
               "products included", url="https://ordspub.epa.gov/ords/pesticides/f?p=PPLS:1",
         by="the US Environmental Protection Agency"),
    dict(title="Healthy Pets, Healthy People (CDC)", url="https://www.cdc.gov/healthy-pets/",
         by="the US Centers for Disease Control and Prevention"),
    dict(title="Livestock and poultry health (USDA APHIS)", url="https://www.aphis.usda.gov/livestock-poultry-disease",
         by="the US Department of Agriculture, Animal and Plant Health Inspection Service"),
]

CATEGORY = dict(
    name="Pet and livestock supplies (manuals)",
    description="Makers' own instructions for pet and livestock equipment: crates and carriers, aquarium filters, "
                "heaters and lights, terrariums and UVB lamps, egg incubators and brooders, clippers and nail "
                "grinders, automatic feeders and water fountains, pet doors and containment fences, electric fence "
                "chargers, waterers and stock tank heaters, milking equipment, horse tack and flea and tick collars; "
                "with official pages on flea and tick product labels and pet health. Links only, fetched from the "
                "maker.",
    kind="manuals", licence="CC0 (facts and links); each manual belongs to its maker",
    ia=IA_WORDS, makers=PET_MAKERS, exclude=PET_EXCLUDE, guidance=PET_GUIDANCE)
