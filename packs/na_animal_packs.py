"""Pack builders for NORTH AMERICAN ANIMALS BY SPECIES (wild) and BY BREED OR KIND (domestic), used by build_packs.py
in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG bytes or None,
row)], where a row is {"question", "answer", "credit"}, plus "place" ("Pennsylvania, USA") and "facts" (the record
it came from). A picture with more than one question comes once with its JPEG and then again as (None, None, row)
rows whose "file" names the same picture (food_packs.with_twins). The limit counts pictures.

Why: the owner's picture describer should name the animal a blind person meets in the United States and Canada by
its species or breed, as a sighted friend would: "a white-tailed deer, a doe", "an eastern gray squirrel", "a
Labrador Retriever", "a Holstein Friesian cow". Answers are fixed sentences written here from each source's own
labels (the species a record is identified as, a Commons breed category), never by an AI model.

NEVER GUESS SEX OR AGE. An answer says "a doe", "a male" or "a fawn" only when the record itself states the sex or
life stage (GBIF's sex and lifeStage fields: on iNaturalist records these are the observers' own annotations); a
record that states neither gets the species only.

The packs (all open: CC0, the Public Domain Mark, public domain or CC BY, checked PHOTO BY PHOTO at the source,
November 2026):
  na_wild_mammals   Wild mammals of the US and Canada (deer, squirrels, rabbits, raccoons, foxes, bears, bats), marine
                    mammals among the first (whales, dolphins, seals, sea lions, sea otters, manatees, walrus).
  na_birds          Wild birds of the US and Canada: breeding birds, common migrants, shorebirds and seabirds.
  na_herps_fish     Reptiles (snakes, lizards, turtles, alligators), amphibians (frogs, toads, salamanders) and fish
                    (freshwater and sea fish); the venomous snakes and the Gila monster among the first.
  na_insects        Insects, spiders, ticks, scorpions and their kin, household and garden pests among the first
                    (ticks, mosquitoes, bed bugs, cockroaches, termites, fire ants, wasps, black widows, brown
                    recluses, fleas, stink bugs, spotted lanternflies).
  na_invertebrates  Snails and slugs, crabs, crayfish, shrimps, woodlice and barnacles, millipedes and centipedes,
                    earthworms and leeches, clams and mussels, sea stars, sea urchins, anemones, jellyfish,
                    Portuguese man o' war, octopuses and horseshoe crabs.
  na_animal_signs   Signs of animals and their young: tracks, scat, nests, webs, burrows, mounds and other structures,
                    eggs, shed skins (molts) and feathers ("What animal made these tracks?"), from iNaturalist's
                    "Evidence of presence" annotation (the record must say that evidence), and young animals whose
                    record gives the life stage. Bones, hair and remains are never taken.
    The six wild packs read GBIF's occurrence API (api.gbif.org, which its robots.txt allows): human observations
    recorded in the US or Canada with a photo whose OWN licence is CC0, the Public Domain Mark or CC BY (a record's
    licence alone is not trusted: an iNaturalist record can be CC BY while its photo is CC BY-NC). The species of
    each group are visited in the order of how often they are recorded there with an open photo (GBIF's facet counts),
    so the animals people meet most (backyard, park, farm and roadside animals) come first and rarer ones follow;
    every third place goes to a "priority" species (pests, venomous or dangerous animals, marine mammals). Each
    species has a cap (species_cap: twice the usual for the 50 most recorded, half past the 400th), all caps shrink
    together when a build is smaller than they allow, and one photographer gives only a few photos of a species. Most
    records are iNaturalist research-grade observations, which iNaturalist publishes to GBIF; their photos are read
    from the iNaturalist Open Dataset on Amazon's open-data programme (inaturalist-open-data.s3.amazonaws.com,
    published by iNaturalist for reuse under each photo's own licence). Neither www.inaturalist.org (whose
    robots.txt says "ai-train=no") nor api.inaturalist.org (whose robots.txt disallows every robot) is read here.
    English names: the name ITIS gives (the Integrated Taxonomic Information System of the US, Canadian and Mexican
    governments), else the name GBIF's checklists agree on most; the scientific name always.
    VENOMOUS AND DANGEROUS ANIMALS get a safety note after the name (SAFETY: rattlesnakes, copperheads, cottonmouths,
    coral snakes, the Gila monster, alligators and crocodiles, widow spiders, brown recluses, bark scorpions, ticks,
    fire ants, wasps and hornets, stinging caterpillars, bears, moose and bison, mountain lions, lionfish, stinging
    jellyfish, large sharks): "This is a Timber Rattlesnake (Crotalus horridus). Caution: ..."
    Left out: records marked dead (vitality), evidence that is not what the pack asks about (in the species packs
    anything but the animal itself), captive or cultivated animals, people (Homo sapiens), the domestic animals, and
    every record whose own words name a death, a kill, hunting, fishing catches, roadkill, an injury, blood,
    remains, a mounted or preserved specimen, entanglement, stranding or predation (HARM).
  noaa_fisheries_species  NOAA Fisheries' species profiles (www.fisheries.noaa.gov/species/..., 309 profiles of
                    whales, dolphins, seals, sea turtles, fish, sharks, corals and shellfish): the photos and drawings
                    whose own credit line is NOAA's (works of the US government, public domain; its disclaimer page
                    is checked at every build) and whose description names the profile's species, with the species
                    and that description. Pictures of tagging, fishing gear, boats, people, maps, dead or entangled
                    animals are left out.
  na_domestic_animals  Wikimedia Commons: dog breeds recognised by the AKC and the CKC (about 200, every group),
                    cat breeds, horse and pony breeds, donkeys and mules, cattle (dairy and beef), pigs, sheep, goats,
                    chickens, ducks, geese and turkeys by breed (heritage breeds included), rabbits by breed, guinea
                    pigs, hamsters, gerbils, ferrets, chinchillas, pet rats and mice, pet birds, pet reptiles and
                    exotic pets (sugar gliders, hedgehogs, axolotls, tarantulas, hermit crabs, tortoises), pet fish,
                    working and service dogs (guide dogs, assistance, therapy, police, detection, search-and-rescue,
                    herding, sled and livestock guardian dogs), animal handling equipment and pet supplies (halters,
                    saddles, bridles, harnesses, collars, leashes, carriers, cages, hutches, aquariums, terrariums,
                    litter boxes, cat trees, bowls, food, toys) and farm scenes (coops, stables, paddocks, pastures,
                    milking, sheep shearing, petting zoos). Each file's licence is checked (CC0, public domain or CC
                    BY; never BY-SA). The category names the breed or kind; the answers name the kind of animal too
                    ("This is a Jersey, a breed of dairy cattle."). Butchery, slaughter, meat, dead animals, injuries,
                    hunting, fighting, art and toys are left out by their words.
    "Calls described in text" were looked for: GBIF's photo records carry no descriptions of calls, and sound
    recordings are not pictures, so none is used.

Not repeated: inaturalist (worldwide, by votes), inaturalist_us and inaturalist_ca (iNaturalist by state and
province, all living things), gbif_species (worldwide, iNaturalist left out, two photos a species),
lila_camera_traps, commons_breeds (every breed of nine animals worldwide, four photos each), commons_disability (its
guide dogs) and usda_ars (agricultural research photos). These packs go deeper on North America by species and by
breed; a few photos may be in both a wide pack and one of these.

Safety (packs/SOURCE-RULES.md): no hunting kill photos, roadkill or graphic injury (HARM, vitality, evidence); no
sexual content (NUDE). People can appear in the domestic photos (riders, farmers, handlers, a guide dog's
handler), hold the fish, frogs and snakes of na_herps_fish, and work beside the animals in NOAA's photos, so those
three packs are never used for picture-making (the kit's PEOPLE_AND_BODILY_PACK_KEYS). Domestic rows whose own
words name a child are marked "child" (the young of animals, "goat kids", "a baby rabbit", are not counted as
children).

    python packs/na_animal_packs.py na_wild_mammals --limit 8      (prints a few rows: a quick check)
"""

import collections
import json
import math
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: food_packs and build_packs import each other
from build_packs import session, clean, say, considered, listing_out_of_time, fetch_all, pass_random
from food_packs import with_twins, count_pictures, commons_members
from home_packs import commons_fetch, file_name, NUDE, FIRST_PERSON, NOT_RESPECTFUL
from expression_packs import mark_child, child_count
from mechanical_packs import mech_entries, in_english, JUST_A_RECORD, NOT_A_PHOTO
from everyday_packs import GBIF, GBIF_GROUPS, GBIF_NOT_A_NAME, gbif_licence, a_or_an, breed_name
from places import where, place_name

USA, CANADA = "USA", "Canada"
COUNTRIES = {"US": USA, "CA": CANADA}
WHERE_Q = "Where was this photo taken?"
DESCRIBE_Q = "Describe this picture."

# ====================================================================== the wild packs (GBIF)

FISH_ORDERS = GBIF_GROUPS[4][0]          # sharks and rays and the main bony-fish orders (everyday_packs)
REPTILE_ORDERS = (11592253, 11418114, 11493978)    # lizards and snakes, turtles, crocodiles (GBIF Backbone keys)


def group(question, share, taxa=(), classes=(), priority=(), extra=None, evidence="", kind=""):
    """One group of a wild pack: its GBIF Backbone keys (taxa) or class names (classes, looked up by name), the
    question, its share of the pack, species to take first whatever their rank (priority: pests, venomous and
    dangerous species, marine mammals), extra search terms (a GBIF full-text word or a life stage), and for the signs
    pack the evidence a record must show (evidenceOfPresence) and how the answer names it (kind)."""
    return {"question": question, "share": share, "taxa": tuple(taxa), "classes": tuple(classes),
            "priority": tuple(priority), "extra": dict(extra or {}), "evidence": evidence, "kind": kind}


MARINE_MAMMALS = ("Megaptera novaeangliae", "Eschrichtius robustus", "Orcinus orca", "Tursiops truncatus",
                  "Delphinus delphis", "Phocoena phocoena", "Balaenoptera musculus", "Balaenoptera physalus",
                  "Balaenoptera acutorostrata", "Eubalaena glacialis", "Physeter macrocephalus",
                  "Delphinapterus leucas", "Monodon monoceros", "Phoca vitulina", "Halichoerus grypus",
                  "Zalophus californianus", "Eumetopias jubatus", "Callorhinus ursinus", "Mirounga angustirostris",
                  "Odobenus rosmarus", "Pusa hispida", "Pagophilus groenlandicus", "Enhydra lutris",
                  "Trichechus manatus", "Ursus maritimus", "Lontra canadensis")
PESTS = ("Ixodes scapularis", "Ixodes pacificus", "Dermacentor variabilis", "Dermacentor andersoni",
         "Amblyomma americanum", "Amblyomma maculatum", "Rhipicephalus sanguineus", "Aedes aegypti",
         "Aedes albopictus", "Culex pipiens", "Culex quinquefasciatus", "Anopheles quadrimaculatus",
         "Cimex lectularius", "Periplaneta americana", "Blattella germanica", "Blatta orientalis",
         "Reticulitermes flavipes", "Reticulitermes hesperus", "Coptotermes formosanus", "Musca domestica",
         "Solenopsis invicta", "Camponotus pennsylvanicus", "Tapinoma sessile", "Linepithema humile",
         "Halyomorpha halys", "Lycorma delicatula", "Popillia japonica", "Ctenocephalides felis", "Lepisma saccharina",
         "Vespula maculifrons", "Vespula germanica", "Vespa crabro", "Dolichovespula maculata",
         "Latrodectus mactans", "Latrodectus hesperus", "Latrodectus variolus", "Loxosceles reclusa",
         "Centruroides sculpturatus", "Megalopyge opercularis", "Agrilus planipennis", "Lymantria dispar",
         "Plodia interpunctella", "Tineola bisselliella", "Pieris rapae", "Leptinotarsa decemlineata")
VENOMOUS_HERPS = ("Crotalus horridus", "Crotalus atrox", "Crotalus adamanteus", "Crotalus oreganus",
                  "Crotalus viridis", "Crotalus scutulatus", "Crotalus cerastes", "Sistrurus miliarius",
                  "Sistrurus catenatus", "Agkistrodon contortrix", "Agkistrodon piscivorus", "Micrurus fulvius",
                  "Micrurus tener", "Heloderma suspectum", "Alligator mississippiensis", "Crocodylus acutus")
ARACHNID_GENERA = ("Ixodes", "Dermacentor", "Amblyomma", "Rhipicephalus", "Latrodectus", "Loxosceles", "Centruroides")
ARACHNID_PESTS = tuple(n for n in PESTS if n.startswith(ARACHNID_GENERA))
INSECT_PESTS = tuple(n for n in PESTS if n not in ARACHNID_PESTS)
SEA_ANIMALS = ("Pterois volitans", "Hypanus americanus", "Carcharodon carcharias", "Galeocerdo cuvier",
               "Physalia physalis", "Chrysaora quinquecirrha", "Aurelia aurita")

# Each wild pack's groups. Shares add up to 1 (of the pack's limit).
WILD = {
    "na_wild_mammals": [group("What animal is this?", 1.0, taxa=(359,), priority=MARINE_MAMMALS)],
    "na_birds": [group("What bird is this?", 1.0, taxa=(212,))],
    "na_herps_fish": [group("What animal is this?", 0.3, taxa=REPTILE_ORDERS, priority=VENOMOUS_HERPS),
                      group("What animal is this?", 0.25, taxa=(131,)),                 # frogs, toads, salamanders
                      group("What fish is this?", 0.45, taxa=FISH_ORDERS, priority=SEA_ANIMALS[:4])],
    "na_insects": [group("What insect is this?", 0.75, taxa=(216,), priority=INSECT_PESTS),
                   group("What is this creature?", 0.25, taxa=(367,), priority=ARACHNID_PESTS)],
    "na_invertebrates": [group("What is this creature?", 0.3, classes=("Gastropoda",)),        # snails and slugs
                         group("What is this creature?", 0.25, classes=("Malacostraca",)),     # crabs, crayfish ...
                         group("What is this creature?", 0.15, classes=("Diplopoda", "Chilopoda")),
                         group("What is this creature?", 0.1, classes=("Bivalvia", "Clitellata")),
                         group("What is this creature?", 0.2, classes=("Asteroidea", "Echinoidea", "Anthozoa",
                                                                        "Scyphozoa", "Hydrozoa", "Cephalopoda",
                                                                        "Merostomata", "Thecostraca"),
                               priority=SEA_ANIMALS[4:])],
    # Signs of animals and their young: GBIF full-text search for iNaturalist's "Evidence of presence" words (the
    # record must say the same evidence), and records whose life stage is juvenile.
    "na_animal_signs": [group("What animal made these tracks?", 0.22, taxa=(1,), extra={"q": "track"},
                              evidence="track", kind="tracks"),
                        group("What animal left this?", 0.12, taxa=(1,), extra={"q": "scat"}, evidence="scat",
                              kind="scat"),
                        group("What made this?", 0.16, taxa=(1,), extra={"q": "construction"},
                              evidence="construction", kind="construction"),
                        group("What animal laid these eggs?", 0.14, taxa=(1,), extra={"lifeStage": "Egg"},
                              evidence="egg", kind="eggs"),
                        group("What animal shed this?", 0.1, taxa=(1,), extra={"q": "molt"}, evidence="molt",
                              kind="molt"),
                        group("What bird did this feather come from?", 0.06, taxa=(212,), extra={"q": "feather"},
                              evidence="feather", kind="feather"),
                        group("What animal is this?", 0.2, taxa=(359, 212, 131) + REPTILE_ORDERS,
                              extra={"lifeStage": "Juvenile"}, kind="young")],
}
# The usual cap of photos per species in each pack. The 50 most recorded species get twice as many, species past
# the 400th half as many (at least 3): common animals are seen more, and rarer ones still get a few.
PER_SPECIES = {"na_wild_mammals": 25, "na_birds": 14, "na_herps_fish": 14, "na_insects": 8, "na_invertebrates": 10,
               "na_animal_signs": 6}


def species_cap(per_species, rank):
    """The most photos of the species at this rank (0 = the most recorded) in its group."""
    if rank < 50:
        return per_species * 2
    if rank < 400:
        return per_species
    return max(3, per_species // 2)


# Species these packs never name as wild animals: people, and the domestic animals (na_domestic_animals has them).
NOT_WILD = {"Homo sapiens", "Canis familiaris", "Canis lupus familiaris", "Felis catus", "Bos taurus",
            "Equus caballus", "Equus asinus", "Capra hircus", "Ovis aries", "Gallus gallus", "Gallus domesticus",
            "Cavia porcellus", "Mustela furo", "Anser anser domesticus", "Anas platyrhynchos domesticus",
            "Numida meleagris", "Pavo cristatus", "Lama glama", "Vicugna pacos"}
# A record's own words that leave it out: death, kills, hunting and fishing catches, roadkill, injuries, remains,
# preserved specimens and predation.
HARM = re.compile(r"\b(dead|death|died|dying|deceased|road ?kill\w*|road-?kill\w*|carcass\w*|corpse|kill\w*|hit by|"
                  r"struck by|run over|harvest\w*|hunt\w*|hunter|shot|trapped|trap|traps|snared?|caught|catch|"
                  r"angl(er|ers|ing)|fishing|hook(ed)?|bait|injur\w*|wound\w*|blood\w*|bleed\w*|bones?|skull\w*|"
                  r"skeleton|remains|mount(ed)?|taxiderm\w*|specimens?|preserved|pinned|museum|necropsy|dissect\w*|"
                  r"predat\w*|prey|eaten|eating (a|an|the)|dismember\w*|decompos\w*|rotting|scaveng\w*|"
                  r"entangle\w*|strand\w*|bycatch|gut pile|feather pile|plucking post)\b", re.I)
EVIDENCE = re.compile(r'"?evidenceOfPresence"?\s*:\s*(\[[^\]]*\]|"[^"]*")', re.I)
# Evidence a wild record may show: the animal itself, and in the signs pack these signs (never bones or hair).
SIGNS = {"track", "scat", "construction", "egg", "molt", "feather"}
ITIS = "Integrated Taxonomic Information System"

# Safety notes for venomous and dangerous animals, added to the answer: (genus or species, the note).
SAFETY = [
    ({"Crotalus", "Sistrurus"}, "Caution: it is a rattlesnake, venomous; keep well away (at least the snake's length "
                                "twice over) and never touch it."),
    ({"Agkistrodon contortrix"}, "Caution: copperheads are venomous; keep away and never touch it."),
    ({"Agkistrodon piscivorus"}, "Caution: cottonmouths (water moccasins) are venomous; keep away and never touch it."),
    ({"Micrurus"}, "Caution: coral snakes are venomous; never touch it."),
    ({"Heloderma"}, "Caution: the Gila monster is venomous; do not touch it."),
    ({"Alligator", "Crocodylus"}, "Caution: it is dangerous; stay well back from it and from the water's edge."),
    ({"Latrodectus"}, "Caution: widow spiders are venomous; a bite needs medical attention. Do not touch it."),
    ({"Loxosceles"}, "Caution: the brown recluse is venomous; a bite can need medical attention. Do not touch it."),
    ({"Centruroides"}, "Caution: bark scorpions sting painfully and can be dangerous to children; do not touch it."),
    ({"Ixodes", "Dermacentor", "Amblyomma", "Rhipicephalus"}, "Caution: ticks can spread diseases such as Lyme "
                                                            "disease; check your skin and remove a tick promptly."),
    ({"Solenopsis invicta"}, "Caution: fire ants sting in swarms; keep away from their mound."),
    ({"Vespula", "Dolichovespula", "Vespa"}, "Caution: it can sting, many times; keep away from its nest."),
    ({"Megalopyge"}, "Caution: this caterpillar's hairs sting badly; do not touch it."),
    ({"Ursus"}, "Caution: bears are dangerous; keep far away and never approach or feed one."),
    ({"Alces", "Bison"}, "Caution: it is large and can charge; keep far away."),
    ({"Puma concolor"}, "Caution: mountain lions are dangerous; do not approach one."),
    ({"Pterois"}, "Caution: lionfish spines are venomous; do not touch it."),
    ({"Physalia", "Chrysaora"}, "Caution: it stings, even when washed up on a beach; do not touch it."),
    ({"Carcharodon", "Galeocerdo"}, "Caution: it is a large shark that can be dangerous to swimmers."),
]

# Words for the sex or age of some animals, used only when the record states it: (taxon names, female, male,
# young). The genus or family is matched (GBIF gives both).
SEX_WORDS = [
    ({"Odocoileus"}, "doe", "buck", "fawn"),
    ({"Cervus", "Alces", "Rangifer", "Bison", "Ovibos"}, "cow", "bull", "calf"),
    ({"Ovis"}, "ewe", "ram", "lamb"),
    ({"Oreamnos", "Capra"}, "nanny", "billy", "kid"),
    ({"Ursidae"}, "sow", "boar", "cub"),
    ({"Meleagris"}, "hen", "tom", "poult"),
    ({"Cygnus"}, "pen", "cob", "cygnet"),
    ({"Anas", "Mareca", "Spatula", "Aix", "Aythya", "Bucephala", "Lophodytes", "Mergus"}, "hen", "drake", "duckling"),
    ({"Branta", "Anser"}, "goose", "gander", "gosling"),
]
LIFE_STAGES = {"larva": "a larva", "pupa": "a pupa", "nymph": "a nymph", "egg": "an egg", "eggs": "eggs",
               "teneral": "a newly emerged adult", "subimago": "a subimago (a mayfly not yet fully adult)"}
YOUNG = ("juvenile", "immature", "subadult", "young", "cub", "fawn", "calf", "chick", "hatchling", "fledgling")


def evidence_of(record):
    """The set of what iNaturalist's "Evidence of presence" says a record shows ({"organism"}, {"track"},
    {"construction", "egg"} ...), empty when it is not stated."""
    m = EVIDENCE.search(str(record.get("dynamicProperties") or ""))
    return {w.strip().lower() for w in re.findall(r'"([^"]+)"', m.group(1))} if m else set()


def record_problem(record, media, evidence=""):
    """Why a GBIF record is left out, or "" when it may be used: dead, not the animal itself (or, for a signs
    group, not the sign asked for), captive, not a wild species, or its words name harm (HARM)."""
    vitality = clean(record.get("vitality")).lower()
    if vitality and vitality != "alive":
        return f"the record says it is {vitality}"
    shown = evidence_of(record)
    if evidence and evidence not in shown:
        return f"it does not show {evidence}"
    if shown - {"organism"} - ({evidence} if evidence else set()):
        return f"it shows {', '.join(sorted(shown - {'organism'}))}, not what this pack asks about"
    captive = clean(record.get("http://unknown.org/captive_cultivated") or record.get("degreeOfEstablishment"))
    if captive.lower() in ("captive", "cultivated", "true"):
        return "a captive animal"
    if clean(record.get("species")) in NOT_WILD:
        return "a person or a domestic animal"
    words = " ".join(clean(str(x)) for x in (record.get("occurrenceRemarks"), record.get("fieldNotes"),
                                              record.get("behavior"), media.get("title"), media.get("description"),
                                              record.get("habitat")) if x)
    m = HARM.search(words)
    if m:
        return f"its words name harm or a catch ({m.group(0)})"
    return ""


def free_media(record):
    """The first photo of a record whose own licence is CC0, the Public Domain Mark or CC BY, or None."""
    for m in record.get("media") or []:
        url = m.get("identifier") or ""
        if m.get("type") == "StillImage" and url.startswith("http") and gbif_licence(m.get("license")):
            return m
    return None


def photo_url(url):
    """The address to download: iNaturalist Open Dataset photos as their "large" copy (1,024 pixels), others as
    given."""
    if "inaturalist-open-data" in url or "static.inaturalist.org" in url:
        return re.sub(r"/original\.", "/large.", url)
    return url


def english_name(results):
    """A species' English name from GBIF's vernacular names: ITIS's first, else the one most checklists mark
    preferred, else the commonest; "" when there is none or it names a disease (GBIF_NOT_A_NAME)."""
    eng = [r for r in results if r.get("language") == "eng" and clean(r.get("vernacularName"))]
    pick = next((clean(r["vernacularName"]) for r in eng if ITIS in (r.get("source") or "")), "")
    if not pick:
        for pool in ([r for r in eng if r.get("preferred")], eng):
            counts = collections.Counter(clean(r["vernacularName"]).lower().replace("-", " ") for r in pool)
            if counts:
                top = counts.most_common(1)[0][0]
                pick = next(clean(r["vernacularName"]) for r in pool
                            if clean(r["vernacularName"]).lower().replace("-", " ") == top)
                break
    return "" if GBIF_NOT_A_NAME.search(pick) or len(pick) > 60 else pick


def gbif_name(s, key, cache):
    """The English name of a GBIF species (cached), or ""."""
    if key not in cache:
        try:
            cache[key] = english_name(s.get(f"{GBIF}species/{key}/vernacularNames", params={"limit": 300},
                                            timeout=60).json().get("results", []))
        except Exception:  # noqa: BLE001 - no English name
            cache[key] = ""
    return cache[key]


def sex_age(record):
    """The words for the sex or life stage a record STATES ("a doe", "an adult male", "a fawn", "a caterpillar"),
    or "" when it states neither. Nothing is guessed."""
    sex = clean(record.get("sex")).lower()
    sex = sex if sex in ("male", "female") else ""
    stage = clean(record.get("lifeStage")).lower()
    names = {clean(record.get(k)) for k in ("genus", "family", "order")}
    words = next((w for w in SEX_WORDS if w[0] & names), None)
    if stage in YOUNG and words:
        return f"a {words[3]}" + (f" (a young {sex})" if sex else "")
    if stage in YOUNG:
        return f"a young {sex}" if sex else "a young one"
    if stage == "larva" and clean(record.get("order")) == "Lepidoptera":
        return "a caterpillar (a larva)"
    if stage == "larva" and clean(record.get("order")) == "Anura":
        return "a tadpole (a larva)"
    if stage in LIFE_STAGES:
        return LIFE_STAGES[stage]
    if sex and words:
        return f"a {words[1] if sex == 'female' else words[2]}"
    if sex:
        return f"an adult {sex}" if stage == "adult" else f"a {sex}"
    return ""


def safety_note(record):
    """The safety note for a venomous or dangerous animal (SAFETY, by its species or genus), or ""."""
    names = {clean(record.get("species")), clean(record.get("genus"))}
    return next((note for taxa, note in SAFETY if taxa & names), "")


SIGN_ANSWERS = {
    "tracks": "These are tracks of {name}.",
    "scat": "This is scat (droppings) of {name}.",
    "construction": "This was built by {name}: a nest, web, burrow, mound or other structure it made.",
    "eggs": "These are eggs of {name}.",
    "molt": "This is a shed skin (a molt) of {name}.",
    "feather": "This is a feather of {name}.",
}


def wild_answer(common, latin, record, kind=""):
    """ "This is a White-tailed Deer (Odocoileus virginianus), a doe." (the sex or age only when stated), the
    sign's sentence for the signs pack ("These are tracks of a Raccoon (Procyon lotor)."), and the safety note of a
    venomous or dangerous animal."""
    name = f"{a_or_an(common)} {common} ({latin})" if common else latin
    if kind in SIGN_ANSWERS:
        text = SIGN_ANSWERS[kind].format(name=name)
    else:
        detail = sex_age(record)
        text = f"This is {name}" + (f", {detail}." if detail else ".")
    note = safety_note(record)
    return f"{text} {note}" if note else text


def record_place(record):
    """ "Pennsylvania, USA" from a record's state or province (GADM first, then its own words), else the country."""
    country = COUNTRIES.get(record.get("countryCode"), "")
    state = clean(((record.get("gadm") or {}).get("level1") or {}).get("name") or record.get("stateProvince"))
    return place_name(state, country) if country else ""


def wild_item(record, media, common, question, prefix, dataset, kind=""):
    """(file name, photo address, rows) of one GBIF record: the species row and, when the state or province is
    known, where the photo was taken."""
    latin = clean(record.get("species"))
    who = clean(media.get("creator") or media.get("rightsHolder") or record.get("recordedBy"))
    if not re.search(r"[A-Za-z]", who):
        who = "an unnamed photographer"
    licence = gbif_licence(media.get("license"))
    link = clean(record.get("references") or record.get("occurrenceID"))
    credit = (f"Photo by {who}, {licence}, from {dataset} via GBIF, https://www.gbif.org/occurrence/{record['key']}"
              + (f" ({link})" if link.startswith("http") and "gbif.org" not in link else ""))
    place = record_place(record)
    facts = {"gbif": record["key"], "species": latin, "species_key": record.get("speciesKey"),
             "sex": clean(record.get("sex")), "life_stage": clean(record.get("lifeStage")),
             "evidence": sorted(evidence_of(record)), "observed_on": clean(record.get("eventDate"))[:10],
             "dataset": dataset}
    rows = [{"question": question, "answer": wild_answer(common, latin, record, kind), "credit": credit,
             "facts": facts, **where(place)}]
    if place and place not in (USA, CANADA):
        rows.append({"question": WHERE_Q, "answer": f"It was taken in {place}.", "credit": credit, **where(place)})
    return f"{prefix}-{record['key']}.jpg", photo_url(media["identifier"]), rows


def class_keys(s, names, cache):
    """The GBIF Backbone keys of classes named in words ("Gastropoda" -> 225), looked up once each."""
    keys = []
    for name in names:
        if name not in cache:
            try:
                m = s.get(f"{GBIF}species/match", params={"name": name, "rank": "CLASS", "strict": "true"},
                          timeout=60).json()
                cache[name] = m.get("usageKey") if m.get("rank") == "CLASS" else None
            except Exception:  # noqa: BLE001 - that class is left out
                cache[name] = None
        if cache[name]:
            keys.append(cache[name])
    return keys


def priority_species(s, names, params):
    """[(GBIF species key, records)] of the priority species that have open photos in the US and Canada."""
    out = []
    for name in names:
        try:
            m = s.get(f"{GBIF}species/match", params={"name": name, "strict": "true"}, timeout=60).json()
            key = m.get("speciesKey") if m.get("rank") in ("SPECIES", "SUBSPECIES") else None
            if not key:
                continue
            count = s.get(f"{GBIF}occurrence/search", params=dict(params, speciesKey=key, limit=0),
                          timeout=60).json().get("count", 0)
        except Exception:  # noqa: BLE001 - that species is left out
            continue
        if count:
            out.append((key, count))
        time.sleep(0.2)
    return out


def species_list(s, params, most):
    """[(GBIF species key, records)] of a group in the US and Canada with open photos, the most recorded first."""
    data = s.get(f"{GBIF}occurrence/search", timeout=120, params=dict(
        params, limit=0, facet="speciesKey", **{"speciesKey.facetLimit": most})).json()
    counts = (data.get("facets") or [{}])[0].get("counts", [])
    return [(int(c["name"]), int(c["count"])) for c in counts]


def species_photos(s, params, key, count, cap, rng, names, titles, g, prefix):
    """Up to cap items of one species: a page of its records at a random place among its first 2,000, each
    record's first open photo, at most a few per photographer (so one keen photographer does not fill a
    species)."""
    size = min(300, cap * 8)
    offset = rng.randrange(0, max(1, min(count, 2000) - size + 1))
    try:
        results = s.get(f"{GBIF}occurrence/search", timeout=120, params=dict(
            params, speciesKey=key, offset=offset, limit=size)).json().get("results", [])
    except Exception:  # noqa: BLE001 - the species is left out
        return []
    rng.shuffle(results)
    per_person = max(2, cap // 4)
    people, out = collections.Counter(), []
    for record in results:
        if len(out) >= cap:
            break
        media = free_media(record)
        if not media or record.get("taxonRank") not in ("SPECIES", "SUBSPECIES", "VARIETY") \
                or not clean(record.get("species")):
            continue
        problem = record_problem(record, media, g["evidence"])
        if not problem and g["kind"] == "young" and clean(record.get("lifeStage")).lower() not in YOUNG:
            problem = "its life stage is not young"
        if problem:
            considered(f"gbif-{record['key']}", media.get("identifier", ""), problem)
            continue
        who = clean(record.get("recordedBy") or media.get("creator")) or "?"
        if people[who] >= per_person:
            continue
        people[who] += 1
        dataset_key = record.get("datasetKey")
        if dataset_key not in titles:
            titles[dataset_key] = clean(record.get("datasetName")) or "a GBIF dataset"
        common = gbif_name(s, key, names)
        out.append(wild_item(record, media, common, g["question"], prefix, titles[dataset_key], g["kind"]))
    return out


def visit_order(first, ranked, per_species, want):
    """[(species key, records, photos to take)] in the order the species are visited: the ranked species (most
    recorded first) with every third place given to a priority species not ranked high already, each taking its
    species_cap; when all of them together would give much more than wanted, every species takes a smaller, equal
    share of its cap (at least one photo), so a smaller build still covers every listed species."""
    ranked_keys = {k: rank for rank, (k, _) in enumerate(ranked)}
    extra = [(k, n, per_species) for k, n in first if ranked_keys.get(k, 10 ** 9) >= 50]
    rest = [(k, n, species_cap(per_species, rank)) for rank, (k, n) in enumerate(ranked)
            if k not in {e[0] for e in extra}]
    order = []
    while extra or rest:
        order += rest[:2]
        rest = rest[2:]
        if extra:
            order.append(extra.pop(0))
    total = sum(cap for _, _, cap in order) or 1
    scale = min(1.0, want * 1.3 / total)
    return [(k, n, max(1, round(cap * scale))) for k, n, cap in order]


def wild_pack(key, limit, prefix):
    """A wild pack: for each of its groups, its priority species first, then the species most recorded in the US
    and Canada with an open photo, in that order, each with at most species_cap photos, until the group's share
    of the limit is found."""
    s, rng = session(), pass_random(sum(map(ord, key)))
    per_species = PER_SPECIES[key]
    names, titles, classes, items = {}, {}, {}, []
    for g in WILD[key]:
        want = math.ceil(limit * 1.15 * g["share"])
        taxa = list(g["taxa"]) + class_keys(s, g["classes"], classes)
        if not taxa:
            say(f"{key}: no GBIF keys for {g['classes']}")
            continue
        params = {"country": ["US", "CA"], "taxonKey": taxa, "mediaType": "StillImage",
                  "basisOfRecord": "HUMAN_OBSERVATION", "license": ["CC0_1_0", "CC_BY_4_0"],
                  "occurrenceStatus": "PRESENT", **g["extra"]}
        try:
            ranked = species_list(s, params, min(5000, math.ceil(want / max(3, per_species // 2) * 2) + 50))
        except Exception as e:  # noqa: BLE001 - the group is left out
            say(f"{key} group {taxa[0]}: left out ({e})")
            continue
        first = priority_species(s, g["priority"], params)
        order = visit_order(first, ranked, per_species, want)
        found, used = [], 0
        for species_key, count, cap in order:
            if len(found) >= want:
                break
            if listing_out_of_time():
                say(f"  {key}: stopped looking at half the time limit")
                break
            found += species_photos(s, params, species_key, count, cap, rng, names, titles, g, prefix)
            used += 1
            time.sleep(0.3)                       # GBIF asks clients to pace their requests
        say(f"{key} group {taxa[0]} {g['kind'] or ''}: {len(found)} photos of {used} species "
            f"({len(first)} priority, {len(ranked)} ranked)")
        items += found[:want]
    rng.shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=6, pause=0.2)[:limit]
    say(f"{key}: {len(fetched)} pictures")
    return with_twins(fetched)


def build_na_wild_mammals(limit):
    """Wild mammals of the US and Canada by species, marine mammals included (GBIF; mostly iNaturalist
    research-grade observations)."""
    return wild_pack("na_wild_mammals", limit, "namam")


def build_na_birds(limit):
    """Wild birds of the US and Canada by species: breeding birds, migrants, shorebirds and seabirds."""
    return wild_pack("na_birds", limit, "nabird")


def build_na_herps_fish(limit):
    """Reptiles, amphibians and fish of the US and Canada by species, venomous snakes flagged."""
    return wild_pack("na_herps_fish", limit, "naherp")


def build_na_insects(limit):
    """Insects, spiders, ticks and their kin of the US and Canada by species, household pests first."""
    return wild_pack("na_insects", limit, "nabug")


def build_na_invertebrates(limit):
    """Snails, slugs, crabs, crayfish, millipedes, centipedes, earthworms, clams, sea stars, jellyfish and other
    invertebrates of the US and Canada by species."""
    return wild_pack("na_invertebrates", limit, "nainv")


def build_na_animal_signs(limit):
    """Tracks, scat, nests and other structures, eggs, shed skins, feathers and young animals of the US and Canada."""
    return wild_pack("na_animal_signs", limit, "nasign")


# ====================================================================== NOAA Fisheries species photos

NOAA = "https://www.fisheries.noaa.gov"
NOAA_SITEMAP = NOAA + "/sitemap.xml"
NOAA_POLICY = NOAA + "/disclaimer"
NOAA_POLICY_TEXT = "Information created by the U.S. government and presented on U.S. government websites is not " \
                   "subject to copyright"
NOAA_IMG = re.compile(r'<img class="dam-image[^>]*>')
# Pictures whose description shows harm or people at work (an everyday pack of animals): left out.
NOAA_SKIP = re.compile(r"\b(dead|carcass|entangle\w*|strand\w*|injur\w*|wound\w*|bycatch|necropsy|caught|catch|"
                       r"hook\w*|net(s|ted)?|fisherm[ae]n|fishers?|people|person|researchers?|scientists?|divers?|"
                       r"volunteers?|staff|crew|students?|officers?|map|range|graph|chart|logo|tag|tags|tagged|tagging|"
                       r"longline|trawl\w*|deck|boat|vessel|aboard)\b", re.I)


def noaa_species_pages(s):
    """The addresses of NOAA Fisheries' species profiles (www.fisheries.noaa.gov/species/...), from its sitemap."""
    pages = []
    index = s.get(NOAA_SITEMAP, timeout=60).text
    for sub in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", index):
        if listing_out_of_time():
            break
        text = s.get(sub.replace("&amp;", "&"), timeout=60).text
        pages += re.findall(r"<loc>\s*(https://www\.fisheries\.noaa\.gov/species/[a-z0-9-]+)\s*</loc>", text)
        time.sleep(1)
    return list(dict.fromkeys(pages))


def noaa_images(page_html):
    """(common name, scientific name, [(picture address, description, credit)]) of a species profile: the pictures
    whose own credit is NOAA's (works of the US government) and whose description names the species."""
    import html as htmllib
    name = re.search(r'species-overview__header-name">\s*<span>([^<]+)</span>', page_html)
    latin = re.search(r'species-overview__header-subname">\s*([^<]+)</p>', page_html)
    if not name:
        return "", "", []
    common = clean(htmllib.unescape(name.group(1)))
    out, seen = [], set()
    named = re.compile(r"\b" + re.escape(common.lower()).replace(r"\ ", r"[\s-]+") + r"(s|es)?\b")
    for m in NOAA_IMG.finditer(page_html):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        alt = clean(htmllib.unescape((re.search(r'alt="([^"]*)"', tag) or [None, ""])[1] or ""))
        credit = re.search(r"Credit:\s*([^<\"]+)", page_html[m.start():m.start() + 1500])
        credit = clean(htmllib.unescape(credit.group(1))).rstrip(".") if credit else ""
        if not src or not credit.startswith("NOAA") or not named.search(alt.lower()) \
                or re.search(r"\.(jpe?g|png)\b", alt, re.I):
            continue
        url = NOAA + htmllib.unescape(src.group(1)) if src.group(1).startswith("/") else src.group(1)
        base = url.split("?")[0].rsplit("/", 1)[-1]
        if base in seen or NOAA_SKIP.search(alt) or not alt:
            continue
        seen.add(base)
        alt = re.sub(r"\s*Credit:.*$", "", alt).strip()
        out.append((url, alt, credit))
    return common, clean(htmllib.unescape(latin.group(1))) if latin else "", out


def build_noaa_fisheries_species(limit):
    """NOAA Fisheries' species profiles (whales, dolphins, seals, sea turtles, fish, corals and shellfish): their
    NOAA-credited photos, the species from the profile and the photo's own description."""
    s, items = session(), []
    policy = " ".join(re.sub(r"<[^>]+>", " ", s.get(NOAA_POLICY, timeout=60).text).split())
    if NOAA_POLICY_TEXT not in policy:
        say("noaa_fisheries_species: its copyright policy no longer says what was checked; left out")
        return []
    pages = noaa_species_pages(s)
    say(f"NOAA Fisheries: {len(pages)} species profiles")
    for page in pages:
        if len(items) >= limit * 1.15 or listing_out_of_time():
            break
        try:
            common, latin, images = noaa_images(s.get(page, timeout=60).text)
        except Exception:  # noqa: BLE001 - next profile
            continue
        name = f"{a_or_an(common)} {common}" + (f" ({latin})" if latin else "")
        for url, alt, credit in images[:6]:
            drawing = bool(re.search(r"\billustration\b", alt, re.I))
            line = f"{credit} (public domain, US government work), {page}"
            answer = f"This is {'an illustration of ' if drawing else ''}{name}."
            items.append((f"noaa-{len(items)}-" + re.sub(r"[^\w-]+", "_", url.split("?")[0].rsplit("/", 1)[-1].rsplit(".", 1)[0])[:60]
                          + ".jpg", url,
                          [{"question": "What animal is this?", "answer": answer, "credit": line,
                            "facts": {"species": latin, "page": page}},
                           {"question": DESCRIBE_Q, "answer": alt if alt.endswith(".") else alt + ".",
                            "credit": line, "facts": {"species": latin, "page": page}}]))
        time.sleep(1)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)[:limit]
    say(f"noaa_fisheries_species: {len(fetched)} pictures")
    return with_twins(fetched)


# ====================================================================== the domestic pack (Wikimedia Commons)

BREED_Q = "What breed of {animal} is this?"
KIND_Q = "What kind of {animal} is this?"
ANIMAL_Q = "What animal is this?"

# The breeds to take from each Commons breed list: (animal, its Commons list of breed categories, the words for its
# kind in an answer, the breeds by their usual North American names). A breed is matched to its category by name
# (breed_key), so "Boxer (dog)" and "Boxer" are the same breed. Dogs: the breeds recognised by the American Kennel
# Club and the Canadian Kennel Club that are common in North America (the AKC's yearly popularity list), and three
# popular crosses.
DOG_BREEDS = (
    "Labrador Retriever", "Golden Retriever", "German Shepherd Dog", "French Bulldog", "Bulldog", "Poodle", "Beagle",
    "Rottweiler", "German Shorthaired Pointer", "Dachshund", "Pembroke Welsh Corgi", "Cardigan Welsh Corgi",
    "Australian Shepherd", "Yorkshire Terrier", "Boxer", "Cavalier King Charles Spaniel", "Dobermann",
    "Doberman Pinscher", "Great Dane", "Miniature Schnauzer", "Standard Schnauzer", "Giant Schnauzer",
    "Siberian Husky", "Bernese Mountain Dog", "Shih Tzu", "Boston Terrier", "Havanese", "Pomeranian",
    "Cocker Spaniel", "English Cocker Spaniel", "American Cocker Spaniel", "English Springer Spaniel",
    "Shetland Sheepdog", "Border Collie", "Brittany", "Chihuahua", "Pug", "Maltese", "Basset Hound", "English Mastiff",
    "Mastiff", "Bullmastiff", "Newfoundland", "Chesapeake Bay Retriever", "Nova Scotia Duck Tolling Retriever",
    "Flat-Coated Retriever", "Weimaraner", "Vizsla", "Rough Collie", "Smooth Collie", "Alaskan Malamute", "Akita",
    "American Akita", "Saint Bernard", "St. Bernard", "Bichon Frise", "Bichon Frisé", "Bloodhound", "Belgian Malinois",
    "Malinois", "Great Pyrenees", "Pyrenean Mountain Dog", "Samoyed", "Shiba Inu", "Australian Cattle Dog",
    "Jack Russell Terrier", "Parson Russell Terrier", "Bull Terrier", "American Staffordshire Terrier",
    "Staffordshire Bull Terrier", "American Pit Bull Terrier", "Papillon", "Whippet", "Greyhound", "Italian Greyhound",
    "Dalmatian", "West Highland White Terrier", "Scottish Terrier", "Cairn Terrier", "Lhasa Apso", "Chow Chow",
    "Rhodesian Ridgeback", "Bluetick Coonhound", "Redbone Coonhound", "Treeing Walker Coonhound",
    "Black and Tan Coonhound", "American Foxhound", "Boykin Spaniel", "Catahoula Leopard Dog",
    "American Eskimo Dog", "Labradoodle", "Goldendoodle", "Cockapoo", "Cane Corso", "Portuguese Water Dog",
    "Irish Setter", "English Setter", "Gordon Setter", "Airedale Terrier", "Soft-coated Wheaten Terrier",
    "Miniature American Shepherd", "Miniature Pinscher", "Shar Pei", "Chinese Shar-Pei", "Basenji", "Keeshond",
    "Leonberger", "Old English Sheepdog", "Bearded Collie", "Australian Kelpie", "Norwegian Elkhound",
    "Brussels Griffon", "Pekingese", "Chinese Crested Dog", "Toy Fox Terrier", "Rat Terrier", "Border Terrier",
    "Wire Fox Terrier", "Smooth Fox Terrier", "Miniature Bull Terrier", "Coton de Tulear", "Bouvier des Flandres",
    "Anatolian Shepherd", "Kuvasz", "Komondor", "Tibetan Terrier", "Tibetan Mastiff", "Irish Wolfhound",
    "Scottish Deerhound", "Afghan Hound", "Saluki", "Borzoi", "Dogo Argentino", "Plott Hound", "Mountain Cur",
    "Carolina Dog", "Chinook", "Alaskan Husky", "Greater Swiss Mountain Dog", "Entlebucher Mountain Dog",
    "Belgian Tervuren", "Belgian Sheepdog", "Groenendael", "Dutch Shepherd", "English Pointer", "Pointer",
    "Wirehaired Pointing Griffon", "German Wirehaired Pointer", "Brittany Spaniel", "Field Spaniel", "Sussex Spaniel",
    "Clumber Spaniel", "Welsh Springer Spaniel", "Curly-Coated Retriever", "Irish Water Spaniel",
    "American Water Spaniel", "Lagotto Romagnolo", "Spinone Italiano", "Xoloitzcuintle", "Japanese Chin",
    "Silky Terrier", "Australian Terrier", "Norwich Terrier", "Norfolk Terrier", "Skye Terrier", "Dandie Dinmont Terrier",
    "Bedlington Terrier", "Kerry Blue Terrier", "Welsh Terrier", "Lakeland Terrier", "Manchester Terrier",
    "Affenpinscher", "Schipperke", "Finnish Spitz", "Icelandic Sheepdog", "Swedish Vallhund", "Canaan Dog",
    "Pharaoh Hound", "Ibizan Hound", "Harrier", "English Foxhound", "Otterhound", "Petit Basset Griffon Vendéen",
    "Beauceron", "Briard", "Puli", "Pumi", "Berger Picard", "Polish Lowland Sheepdog", "Neapolitan Mastiff",
    "Dogue de Bordeaux", "Boerboel", "Black Russian Terrier", "Tosa", "American Bulldog", "American English Coonhound",
    "Nederlandse Kooikerhondje", "Labrador Husky", "Tahltan Bear Dog", "Canadian Eskimo Dog", "Newfoundland dog")
CAT_BREEDS = (
    "Persian", "Maine Coon", "Ragdoll", "British Shorthair", "Siamese", "Sphynx", "Abyssinian", "Bengal",
    "Russian Blue", "Scottish Fold", "Devon Rex", "Cornish Rex", "Norwegian Forest Cat", "American Shorthair",
    "Exotic Shorthair", "Exotic", "Birman", "Burmese", "Tonkinese", "Himalayan", "Siberian", "Turkish Angora",
    "Turkish Van", "Oriental Shorthair", "Oriental", "Manx", "Savannah", "Ragamuffin", "Egyptian Mau", "Ocicat",
    "Somali", "Balinese", "Chartreux", "Selkirk Rex", "American Curl", "American Bobtail", "Japanese Bobtail",
    "Havana Brown", "Bombay", "Singapura", "LaPerm", "Toyger", "Snowshoe", "Nebelung", "Korat", "Munchkin",
    "Pixie-bob", "Cymric", "Lykoi", "Peterbald", "Don Sphynx", "Burmilla", "Chausie")
HORSE_BREEDS = (
    "American Quarter Horse", "Quarter Horse", "Thoroughbred", "Appaloosa", "American Paint Horse", "Paint Horse",
    "Morgan", "Arabian", "Arabian horse", "Standardbred", "Tennessee Walking Horse", "American Saddlebred",
    "Clydesdale", "Belgian", "Belgian Draught", "Brabant", "Percheron", "Friesian", "American Miniature Horse",
    "Miniature horse", "Falabella", "Shetland pony", "Welsh pony", "Welsh Pony and Cob", "Haflinger", "Mustang",
    "Chincoteague pony", "Canadian horse", "Newfoundland pony", "Sable Island horse", "Gypsy Cob", "Gypsy Vanner",
    "Irish Cob", "Shire", "Suffolk Punch", "Missouri Fox Trotter", "Rocky Mountain Horse", "Paso Fino",
    "Peruvian Paso", "Icelandic horse", "Fjord horse", "Norwegian Fjord", "Hanoverian", "Trakehner", "Holsteiner",
    "Oldenburg", "Dutch Warmblood", "Andalusian", "Lusitano", "Lipizzan", "Lipizzaner", "Connemara pony",
    "Pony of the Americas", "Spotted Saddle Horse", "Akhal-Teke", "Knabstrupper", "Marwari", "Mule", "Hinny",
    "Banker horse", "Florida Cracker Horse", "Pinto")
CATTLE_BREEDS = (
    ("Holstein Friesian", "dairy cattle"), ("Holstein", "dairy cattle"), ("Jersey", "dairy cattle"),
    ("Guernsey", "dairy cattle"), ("Brown Swiss", "dairy cattle"), ("Ayrshire", "dairy cattle"),
    ("Milking Shorthorn", "dairy cattle"), ("Dutch Belted", "dairy cattle"), ("Canadienne", "dairy cattle"),
    ("Angus", "beef cattle"), ("Aberdeen Angus", "beef cattle"), ("Red Angus", "beef cattle"),
    ("Hereford", "beef cattle"), ("Polled Hereford", "beef cattle"), ("Charolais", "beef cattle"),
    ("Simmental", "beef cattle"), ("Limousin", "beef cattle"), ("Shorthorn", "beef cattle"),
    ("Texas Longhorn", "beef cattle"), ("Highland", "beef cattle"), ("Scottish Highland", "beef cattle"),
    ("Brahman", "beef cattle"), ("American Brahman", "beef cattle"), ("Santa Gertrudis", "beef cattle"),
    ("Brangus", "beef cattle"), ("Beefmaster", "beef cattle"), ("Gelbvieh", "beef cattle"),
    ("Belted Galloway", "beef cattle"), ("Galloway", "beef cattle"), ("Dexter", "cattle"),
    ("Murray Grey", "beef cattle"), ("Piedmontese", "beef cattle"), ("Wagyu", "beef cattle"),
    ("Watusi", "cattle"), ("Ankole-Watusi", "cattle"), ("Pineywoods", "cattle"), ("Florida Cracker", "cattle"),
    ("Randall Lineback", "cattle"), ("Devon", "cattle"), ("Red Poll", "cattle"), ("Normande", "dairy cattle"),
    ("Montbéliarde", "dairy cattle"), ("Zebu", "cattle"), ("Miniature Zebu", "cattle"))
PIG_BREEDS = ("Yorkshire", "Large White", "Duroc", "Berkshire", "Hampshire", "Landrace", "American Landrace",
              "Chester White", "Poland China", "Spotted", "Tamworth", "Gloucestershire Old Spots", "Large Black",
              "Hereford", "Red Wattle", "Mulefoot", "Ossabaw Island", "Guinea Hog", "American Guinea Hog",
              "Kunekune", "Pot-bellied", "Vietnamese Pot-bellied", "Mangalica", "Pietrain", "Meishan")
SHEEP_BREEDS = ("Suffolk", "Dorper", "Katahdin", "Hampshire", "Hampshire Down", "Dorset", "Dorset Horn",
                "Polled Dorset", "Rambouillet", "Merino", "Jacob", "Southdown", "Icelandic", "Shetland", "Romney",
                "Corriedale", "Columbia", "Targhee", "Cheviot", "Border Leicester", "Lincoln", "Cotswold", "Navajo-Churro",
                "Gulf Coast Native", "St. Croix", "Barbados Blackbelly", "Texel", "Romanov", "Finnsheep", "Clun Forest",
                "Tunis", "Oxford", "Shropshire", "Babydoll Southdown", "East Friesian", "Lacaune", "Blue-faced Leicester",
                "Herdwick", "Wensleydale", "Karakul")
GOAT_BREEDS = ("Nubian", "Anglo-Nubian", "Boer", "LaMancha", "Lamancha", "Alpine", "French Alpine", "Saanen",
               "Nigerian Dwarf", "Pygmy", "Angora", "Toggenburg", "Oberhasli", "Kiko", "Spanish", "Myotonic",
               "Tennessee Fainting", "Sable", "Cashmere", "San Clemente Island", "Golden Guernsey", "Kinder",
               "Savanna")
CHICKEN_BREEDS = ("Rhode Island Red", "Plymouth Rock", "Barred Plymouth Rock", "Leghorn", "Orpington",
                  "Buff Orpington", "Silkie", "Wyandotte", "Australorp", "Brahma", "Cochin", "Sussex", "Ameraucana",
                  "Araucana", "Easter Egger", "Marans", "Barnevelder", "Welsummer", "Polish", "Faverolles",
                  "Jersey Giant", "New Hampshire", "Delaware", "Dominique", "Buckeye", "Chantecler", "Java",
                  "Minorca", "Ancona", "Hamburg", "Sebright", "Old English Game", "Modern Game", "Cornish",
                  "Cornish Cross", "Langshan", "Dorking", "Houdan", "Naked Neck", "Turken", "Frizzle", "Serama",
                  "Japanese Bantam", "Ayam Cemani", "Orloff", "Sultan", "Malay", "Shamo", "Black Star", "Red Star",
                  "ISA Brown", "Lohmann Brown")
DUCK_BREEDS = ("Pekin", "American Pekin", "Muscovy", "Indian Runner", "Runner", "Rouen", "Khaki Campbell", "Call",
               "Cayuga", "Swedish Blue", "Swedish", "Welsh Harlequin", "Buff", "Orpington", "Magpie", "Ancona",
               "Silver Appleyard", "Crested", "Aylesbury", "Saxony", "Black East Indian", "Duclair")
GOOSE_BREEDS = ("Embden", "Emden", "Toulouse", "African", "Chinese", "Pilgrim", "Sebastopol", "American Buff",
                "Roman", "Pomeranian", "Cotton Patch", "Shetland", "Steinbacher")
TURKEY_BREEDS = ("Broad Breasted White", "Broad Breasted Bronze", "Bronze", "Bourbon Red", "Narragansett",
                 "Royal Palm", "Black Spanish", "Norfolk Black", "Slate", "Blue Slate", "Beltsville Small White",
                 "Midget White", "White Holland", "Jersey Buff")
RABBIT_BREEDS = ("Holland Lop", "Netherland Dwarf", "Mini Rex", "Lionhead", "Flemish Giant", "New Zealand",
                 "New Zealand White", "Mini Lop", "Rex", "Dutch", "Californian", "English Lop", "French Lop",
                 "English Angora", "French Angora", "Angora", "Polish", "Himalayan", "Harlequin", "Checkered Giant",
                 "Jersey Wooly", "American Fuzzy Lop", "Dwarf Hotot", "Hotot", "Belgian Hare", "Silver Fox",
                 "American Chinchilla", "Chinchilla", "Satin", "Havana", "Florida White", "English Spot",
                 "Britannia Petite", "Champagne d'Argent", "Thrianta", "Tan", "Lop")
# (animal, Commons list, the kind in answers, breeds, the question asked)
BREED_LISTS = [
    ("dog", "Dog breeds by name", "dog", DOG_BREEDS),
    ("cat", "Cat breeds", "cat", CAT_BREEDS),
    ("horse", "Horse breeds by name", "horse", HORSE_BREEDS),
    ("cattle", "Cattle breeds by name", "cattle", CATTLE_BREEDS),
    ("pig", "Pig breeds", "pig", PIG_BREEDS),
    ("sheep", "Sheep breeds by name", "sheep", SHEEP_BREEDS),
    ("goat", "Goat breeds by name", "goat", GOAT_BREEDS),
    ("chicken", "Chicken breeds", "chicken", CHICKEN_BREEDS),
    ("duck", "Duck breeds", "domestic duck", DUCK_BREEDS),
    ("goose", "Goose breeds", "domestic goose", GOOSE_BREEDS),
    ("turkey", "Turkey breeds", "domestic turkey", TURKEY_BREEDS),
    ("rabbit", "Rabbit breeds", "rabbit", RABBIT_BREEDS),
]
# Kinds that are not breeds: (Commons category, how deep to walk its subcategories, the question, the answer).
GUIDE_DOG = ("This is a guide dog: a dog trained to lead a blind or partially sighted person safely around "
             "obstacles, across streets and through crowds, usually wearing a harness with a stiff handle.")
KINDS = [
    ("Guide dogs", 1, KIND_Q.format(animal="dog"), GUIDE_DOG),
    ("Assistance dogs", 0, KIND_Q.format(animal="dog"),
     "This is an assistance dog: a dog trained to help a disabled person, for example by guiding, alerting to "
     "sounds or a medical problem, or fetching and opening things."),
    ("Service dogs", 0, KIND_Q.format(animal="dog"),
     "This is a service dog: a dog trained to do work for a disabled person; in the US, the ADA lets it go where "
     "its handler goes."),
    ("Therapy dogs", 0, KIND_Q.format(animal="dog"),
     "This is a therapy dog: a calm, friendly dog that visits hospitals, schools or care homes to comfort people."),
    ("Police dogs", 1, KIND_Q.format(animal="dog"),
     "This is a police dog: a dog trained to help police officers track, search or detect."),
    ("Detection dogs", 1, KIND_Q.format(animal="dog"),
     "This is a detection dog (a sniffer dog): a dog trained to find things by smell, such as drugs, explosives, "
     "food at an airport, or bedbugs."),
    ("Search and rescue dogs", 1, KIND_Q.format(animal="dog"),
     "This is a search and rescue dog: a dog trained to find lost or trapped people by their scent."),
    ("Herding dogs", 0, KIND_Q.format(animal="dog"),
     "This is a herding dog: a dog that moves and gathers sheep or cattle for a farmer."),
    ("Sled dogs", 0, KIND_Q.format(animal="dog"),
     "These are sled dogs: dogs that pull a sled over snow, usually in a team harnessed in pairs."),
    ("Livestock guardian dogs", 0, KIND_Q.format(animal="dog"),
     "This is a livestock guardian dog: a large dog that lives with sheep, goats or other farm animals and protects "
     "them from predators."),
    ("Mixed-breed dogs", 0, BREED_Q.format(animal="dog"),
     "This is a mixed-breed dog: a dog of no single breed (a mutt)."),
    ("Domestic short-haired cats", 0, BREED_Q.format(animal="cat"),
     "This is a domestic shorthair: a short-haired pet cat of no particular breed."),
    ("Donkeys", 1, ANIMAL_Q, "This is a donkey: a farm animal related to the horse, smaller, with long ears."),
    ("Miniature donkeys", 0, ANIMAL_Q, "This is a miniature donkey: a small breed of donkey kept as a pet or on farms."),
    ("Mules", 0, ANIMAL_Q, "This is a mule: the offspring of a male donkey and a female horse, used for riding, "
                           "packing and farm work."),
    ("Alpacas", 1, ANIMAL_Q, "This is an alpaca: a woolly South American animal like a small llama, kept on farms "
                             "for its fleece."),
    ("Llamas", 1, ANIMAL_Q, "This is a llama: a long-necked South American animal kept as a pack animal, for wool "
                            "and as a guard for sheep."),
    ("Water buffalo", 1, ANIMAL_Q, "This is a water buffalo: a large, dark farm animal with wide curved horns, "
                                   "kept for milk and work."),
]
# Animal handling equipment, pet supplies and farm scenes: (Commons category, depth, the question, the answer).
# (Barns, silos, feedlots and cattle chutes are farm_commons_equipment's; guide dog harnesses are in "Guide dogs".)
WHAT_Q = "What is this?"
PLACE_Q = "What kind of place is this?"
EQUIPMENT = [
    ("Horse halters", 0, WHAT_Q, "This is a horse halter: a headstall of straps or rope fitted around a horse's head "
                                 "and nose, used to lead or tie it."),
    ("Halters", 0, WHAT_Q, "This is a halter: a headstall used to lead or tie an animal."),
    ("Saddles", 0, WHAT_Q, "This is a saddle: the seat strapped to a horse's back for its rider."),
    ("Bridles", 0, WHAT_Q, "This is a bridle: the headgear with a bit and reins used to steer a horse."),
    ("Horse harnesses", 0, WHAT_Q, "This is a horse harness: the straps and collar by which a horse pulls a cart, "
                                   "wagon or plough."),
    ("Horse trailers", 0, WHAT_Q, "This is a horse trailer, towed behind a truck to carry horses."),
    ("Dog harnesses", 0, WHAT_Q, "This is a dog harness: straps around a dog's chest and shoulders that a leash "
                                 "clips to."),
    ("Dog collars", 0, WHAT_Q, "This is a dog collar, worn around the neck, often with a tag and a ring for a leash."),
    ("Leashes", 0, WHAT_Q, "This is a leash (a lead): a strap or cord for walking an animal."),
    ("Pet carriers", 0, WHAT_Q, "This is a pet carrier: a box or bag with a door and air holes to carry a small "
                                "animal."),
    ("Bird cages", 0, WHAT_Q, "This is a bird cage."),
    ("Hamster cages", 0, WHAT_Q, "This is a cage for a hamster or another small pet."),
    ("Rabbit hutches", 0, WHAT_Q, "This is a rabbit hutch: a wooden pen with wire sides where rabbits are kept."),
    ("Aquariums", 0, WHAT_Q, "This is an aquarium: a glass tank of water for keeping fish."),
    ("Terrariums", 0, WHAT_Q, "This is a terrarium: a glass tank for keeping reptiles, amphibians or plants."),
    ("Litter boxes", 0, WHAT_Q, "This is a litter box: a tray of litter a cat uses as its toilet."),
    ("Cat trees", 0, WHAT_Q, "This is a cat tree: a carpeted post with platforms for a cat to climb, scratch and "
                             "rest on."),
    ("Pet bowls", 0, WHAT_Q, "This is a pet bowl, for an animal's food or water."),
    ("Dog food", 0, WHAT_Q, "This is dog food."),
    ("Cat food", 0, WHAT_Q, "This is cat food."),
    ("Dog toys", 0, WHAT_Q, "This is a dog toy."),
    ("Pet shops", 0, PLACE_Q, "This is a pet shop, which sells pets, food and supplies."),
    ("Chicken coops", 1, PLACE_Q, "This is a chicken coop: a small shed where hens roost and lay eggs."),
    ("Horse stables", 1, PLACE_Q, "This is a horse stable: a building with stalls where horses are kept."),
    ("Paddocks", 0, PLACE_Q, "This is a paddock: a small fenced field where horses or other animals are kept."),
    ("Pastures", 0, PLACE_Q, "This is a pasture: a grassy field where farm animals graze."),
    ("Milking", 1, WHAT_Q, "This shows milking: milk being taken from a cow, goat or sheep, by hand or by machine."),
    ("Sheep shearing", 1, WHAT_Q, "This shows sheep shearing: a sheep's fleece being clipped off for its wool."),
    ("Petting zoos", 1, PLACE_Q, "This is a petting zoo, where visitors can touch and feed farm animals."),
]
# Pets named by species: (Commons category, the answer). The answer says what the animal is, whether it is
# kept as a pet or met in the wild.
PETS = [
    ("Cavia porcellus", "This is a guinea pig (Cavia porcellus), a small pet rodent."),
    ("Mesocricetus auratus", "This is a Syrian hamster (Mesocricetus auratus), a small pet rodent, also called a "
                             "golden hamster."),
    ("Phodopus", "This is a dwarf hamster (Phodopus), a very small pet rodent."),
    ("Meriones unguiculatus", "This is a gerbil (a Mongolian gerbil, Meriones unguiculatus), a small pet rodent "
                              "with a long tail."),
    ("Mustela furo", "This is a ferret (Mustela furo), a long, slender pet related to weasels."),
    ("Chinchilla lanigera", "This is a chinchilla (Chinchilla lanigera), a soft-furred rodent kept as a pet."),
    ("Fancy rats", "This is a pet rat (a fancy rat)."),
    ("Fancy mice", "This is a pet mouse (a fancy mouse)."),
    ("Melopsittacus undulatus", "This is a budgerigar (a budgie or parakeet, Melopsittacus undulatus), a small "
                                "parrot often kept as a pet."),
    ("Nymphicus hollandicus", "This is a cockatiel (Nymphicus hollandicus), a small crested parrot often kept as a "
                              "pet."),
    ("Agapornis roseicollis", "This is a rosy-faced lovebird (Agapornis roseicollis), a small parrot kept as a pet."),
    ("Serinus canaria domestica", "This is a canary (a domestic canary), a small songbird kept as a pet."),
    ("Taeniopygia castanotis", "This is a zebra finch (Taeniopygia castanotis), a small finch often kept as a pet."),
    ("Psittacus erithacus", "This is an African grey parrot (Psittacus erithacus), a large grey parrot known for "
                            "talking."),
    ("Cacatua galerita", "This is a sulphur-crested cockatoo (Cacatua galerita), a large white parrot with a "
                         "yellow crest."),
    ("Ara ararauna", "This is a blue-and-yellow macaw (Ara ararauna), a large parrot."),
    ("Pogona vitticeps", "This is a bearded dragon (Pogona vitticeps), a lizard often kept as a pet."),
    ("Eublepharis macularius", "This is a leopard gecko (Eublepharis macularius), a spotted lizard often kept as a "
                               "pet."),
    ("Correlophus ciliatus", "This is a crested gecko (Correlophus ciliatus), a lizard often kept as a pet."),
    ("Python regius", "This is a ball python (Python regius), a snake often kept as a pet."),
    ("Pantherophis guttatus", "This is a corn snake (Pantherophis guttatus), a snake of the southeastern US often "
                              "kept as a pet."),
    ("Trachemys scripta elegans", "This is a red-eared slider (Trachemys scripta elegans), a turtle often kept as a "
                                  "pet and common in ponds."),
    ("Carassius auratus", "This is a goldfish (Carassius auratus), a pet fish."),
    ("Koi", "This is a koi, a coloured carp kept in garden ponds."),
    ("Betta splendens", "This is a betta (a Siamese fighting fish, Betta splendens), a pet fish with long fins."),
    ("Columba livia domestica", "This is a domestic pigeon (Columba livia domestica)."),
    # exotic pets
    ("Petaurus breviceps", "This is a sugar glider (Petaurus breviceps), a small gliding marsupial kept as an "
                           "exotic pet."),
    ("Atelerix albiventris", "This is an African pygmy hedgehog (Atelerix albiventris), a small spiny pet."),
    ("Ambystoma mexicanum", "This is an axolotl (Ambystoma mexicanum), a salamander with feathery gills often kept "
                            "in aquariums."),
    ("Brachypelma hamorii", "This is a Mexican red-knee tarantula (Brachypelma hamorii), a large hairy spider kept "
                            "as a pet."),
    ("Coenobita clypeatus", "This is a Caribbean hermit crab (Coenobita clypeatus), a land crab living in a shell, "
                            "often kept as a pet."),
    ("Centrochelys sulcata", "This is an African spurred tortoise (a sulcata, Centrochelys sulcata), a large tortoise "
                             "kept as a pet."),
    ("Tiliqua scincoides", "This is a blue-tongued skink (Tiliqua scincoides), a lizard kept as a pet."),
    ("Chamaeleo calyptratus", "This is a veiled chameleon (Chamaeleo calyptratus), a lizard kept as a pet."),
    ("Iguana iguana", "This is a green iguana (Iguana iguana), a large lizard kept as a pet and wild in Florida."),
]
# Subcategories that are not photos of the live animal: art, toys, food, history, shows of objects.
SKIP_CAT = re.compile(r"\b(in art|art|drawings?|paintings?|illustrations?|sculptures?|statues?|figurines?|toys?|"
                      r"stamps?|coins?|logos?|heraldry|postcards?|cartoons?|skulls?|skeletons?|taxiderm\w*|"
                      r"museums?|meat|dishes|cuisine|food|slaughter\w*|carcass\w*|leather|wool products|hides?|"
                      r"history|historical|videos?|sounds?|audio|maps?|people with|with people|in fiction|"
                      r"by photographer|unidentified|breeding|genetics)\b", re.I)
# A file's words that leave it out of an everyday pack: butchery, death, hunting, injuries, objects that are not
# the live animal.
DOMESTIC_HARM = re.compile(r"\b(slaughter\w*|butcher\w*|abattoir|meat|carcass\w*|dead|death|died|killed|kill\w*|"
                           r"hunt\w*|injur\w*|wound\w*|blood\w*|skinned|skull|skeleton|taxiderm\w*|stuffed|"
                           r"statue|sculpture|figurine|plush|fighting|cockfight\w*|dogfight\w*|euthan\w*|"
                           r"necropsy|disease|surgery|x-?ray)\b", re.I)
# The young of animals, taken out before the child check ("a baby rabbit", "juvenile"; "kids" where goats are named
# is taken out in domestic_rows).
ANIMAL_YOUNG = re.compile(r"\b(baby|young|newborn)\s+"
                          r"(animals?|goats?|rabbits?|bunn(y|ies)|chicks?|ducks?|ducklings?|horses?|foals?|pigs?|"
                          r"piglets?|lambs?|sheep|calf|calves|cows?|dogs?|puppies|pupp(y)|cats?|kittens?|birds?|"
                          r"turkeys?|geese|goslings?|llamas?|alpacas?|donkeys?|hamsters?|guinea pigs?)\b|"
                          r"\bjuveniles?\b", re.I)


def breed_key(name, animal=""):
    """A breed's name made comparable: lower case, accents and punctuation dropped, "(dog)" and the animal's own
    word ("cattle", "chicken") left out ("Boxer (dog)" -> "boxer", "Rhode Island Red chicken" -> "rhode island
    red")."""
    import unicodedata
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"[^a-z0-9 ]+", " ", text.replace("-", " ").replace("'", ""))
    drop = {animal, animal + "s", "breed", "breeds", "dog", "dogs", "cat", "cats", "cattle", "cow", "cows", "horse",
            "horses", "pony", "ponies", "pig", "pigs", "swine", "sheep", "goat", "goats", "chicken", "chickens",
            "fowl", "duck", "ducks", "goose", "geese", "turkey", "turkeys", "rabbit", "rabbits", "hog", "hogs",
            "the"}
    return " ".join(w for w in text.split() if w not in drop)


def wanted_breeds(categories, animal, breeds):
    """{category: the breed's name for answers} for the categories of a Commons breed list that are one of the
    wanted breeds (matched by breed_key); a breed matched by two categories keeps the first."""
    wanted = {}
    for b in breeds:
        name, kind = b if isinstance(b, tuple) else (b, "")
        wanted.setdefault(breed_key(name, animal), (name, kind))
    out, taken = {}, set()
    for c in categories:
        key = breed_key(breed_name(c, animal), animal)
        if key in wanted and key not in taken:
            taken.add(key)
            out[c] = wanted[key]
    return out


def breed_answer(breed, kind, animal_words):
    """ "This is a Labrador Retriever, a breed of dog." ("of dairy cattle" for cattle with a kind)."""
    return f"This is {a_or_an(breed)} {breed}, a breed of {kind or animal_words}."


def domestic_topics(s):
    """[(category, depth, question, answer)] of the domestic pack: the wanted breeds found in each Commons breed list,
    then the kinds (KINDS) and the pets by species (PETS)."""
    topics = []
    for animal, parent, words, breeds in BREED_LISTS:
        if listing_out_of_time():
            break
        try:
            categories = commons_members(s, parent, "subcat")
            # Lists filed one level deeper ("Chicken breeds by name", "Goat breeds by country").
            for sub in [c for c in categories if re.search(r"\bbreeds\b", c.split(":", 1)[-1], re.I)][:12]:
                categories += commons_members(s, sub.split(":", 1)[-1], "subcat")
        except RuntimeError as e:
            say(f"  Commons {parent}: {e}")
            continue
        found = wanted_breeds(categories, animal, breeds)
        say(f"Commons {parent}: {len(found)} of {len(breeds)} wanted breeds found")
        question = BREED_Q.format(animal="cattle" if animal == "cattle" else animal)
        topics += [(c.split(":", 1)[-1], 1, question, breed_answer(name, kind, words))
                   for c, (name, kind) in found.items()]
    topics += [(c, depth, q, a) for c, depth, q, a in KINDS]
    topics += [(c, 1, ANIMAL_Q, a) for c, a in PETS]
    topics += list(EQUIPMENT)
    return topics


def topic_titles(s, category, depth, seen):
    """The file titles of a topic's category and (depth 1) its subcategories that SKIP_CAT does not name, drawings
    and art left out by their names."""
    cats, titles = [category], []
    if depth:
        try:
            cats += [c.split(":", 1)[-1] for c in commons_members(s, category, "subcat")
                     if not SKIP_CAT.search(c.split(":", 1)[-1])]
        except RuntimeError:
            pass
    for c in cats[:25]:
        if listing_out_of_time():
            break
        try:
            titles += [t for t in commons_members(s, c, "file") if t not in seen and not NOT_A_PHOTO.search(t)]
        except RuntimeError:
            break
    return list(dict.fromkeys(titles))


def domestic_rows(title, credit, text, question, answer, category):
    """The rows of one domestic file: the breed or kind, and its English caption ("Describe this picture.") when it
    is a real description; each marked "child" when its words name a child (not the young of animals)."""
    facts = {"commons_category": category, "commons_title": title.split(":", 1)[-1].rsplit(".", 1)[0]}
    rows = [{"question": question, "answer": answer}]
    text = "" if JUST_A_RECORD.search(text or "") or not in_english(text) else text
    if text and not NOT_RESPECTFUL.search(text) and not FIRST_PERSON.search(text):
        rows.append({"question": DESCRIBE_Q, "answer": text})
    words = ANIMAL_YOUNG.sub(" ", f"{title} {text}")
    if re.search(r"\bgoats?\b", words, re.I):
        words = re.sub(r"\bkids?\b", " ", words, flags=re.I)          # young goats
    return [mark_child(dict(r, credit=credit, facts=facts), words) for r in rows]


def build_na_domestic_animals(limit, per_topic=None):
    """Domestic animals by breed or kind from Commons: the topics take turns in a fixed shuffled order, each giving
    at most per_topic free photos (a balanced cap)."""
    s, items, seen = session(), [], set()
    topics = domestic_topics(s)
    random.Random("na_domestic").shuffle(topics)
    per_topic = per_topic or max(3, math.ceil(limit * 1.15 / max(1, len(topics))))
    want = int(limit * 1.15) + 2
    say(f"na_domestic_animals: {len(topics)} topics, at most {per_topic} photos each")
    for category, depth, question, answer in topics:
        if len(items) >= want:
            break
        if listing_out_of_time():
            say("  na_domestic_animals: stopped looking at half the time limit")
            break
        titles = topic_titles(s, category, depth, seen)
        pass_random(sum(map(ord, category))).shuffle(titles)
        got = 0
        for start in range(0, min(len(titles), per_topic * 4), 50):
            if got >= per_topic:
                break
            try:
                entries = mech_entries(s, titles[start:start + 50])
            except RuntimeError as e:         # Commons kept refusing: keep what was found
                say(f"  na_domestic_animals: {e} Keeping the {len(items)} pictures found so far.")
                break
            for title, url, credit, text, raw in entries:
                if got >= per_topic or title in seen:
                    continue
                seen.add(title)
                words = f"{title} {text} {raw}"
                if NUDE.search(words) or DOMESTIC_HARM.search(words):
                    considered(title, url, "its words name butchery, death, harm, art or an object (an everyday pack)")
                    continue
                items.append((file_name("nadom", title), url,
                              domestic_rows(title, credit, text, question, answer, category)))
                got += 1
    random.Random("na_domestic-order").shuffle(items)
    fetched = commons_fetch(items[:want])[:limit]
    say(f"na_domestic_animals: {len(fetched)} pictures")
    return with_twins(fetched)


# ====================================================================== the packs

GBIF_CREDIT = ("GBIF (Global Biodiversity Information Facility), https://www.gbif.org: human observations in the "
               "United States and Canada of {what}, each photo's OWN licence CC0, Public Domain Mark or CC BY "
               "(checked photo by photo), each with its photographer, source dataset and GBIF record below. Most "
               "are iNaturalist research-grade observations (https://www.inaturalist.org), their photos from the "
               "iNaturalist Open Dataset (https://registry.opendata.aws/inaturalist-open-data/). English names from "
               "ITIS (https://www.itis.gov) through the GBIF Backbone Taxonomy.")
NA_ANIMAL_PACKS = {
    "na_wild_mammals": (build_na_wild_mammals, GBIF_CREDIT.format(what="wild mammals")),
    "na_birds": (build_na_birds, GBIF_CREDIT.format(what="wild birds")),
    "na_herps_fish": (build_na_herps_fish, GBIF_CREDIT.format(what="reptiles, amphibians and fish")),
    "na_insects": (build_na_insects, GBIF_CREDIT.format(what="insects, spiders, ticks and their kin")),
    "na_invertebrates": (build_na_invertebrates, GBIF_CREDIT.format(
        what="snails, slugs, crustaceans, millipedes, centipedes, worms, clams, sea stars, jellyfish and other "
             "invertebrates")),
    "na_animal_signs": (build_na_animal_signs, GBIF_CREDIT.format(
        what="animal signs (tracks, scat, nests and other structures, eggs, shed skins and feathers) and young "
             "animals")),
    "noaa_fisheries_species": (build_noaa_fisheries_species,
                               "NOAA Fisheries species profiles (https://www.fisheries.noaa.gov/species-directory): "
                               "photos credited to NOAA, works of the US government (public domain, 17 U.S.C. 105; "
                               "https://www.fisheries.noaa.gov/disclaimer: \"Information created by the U.S. "
                               "government ... is not subject to copyright\"). Courtesy: National Oceanic and "
                               "Atmospheric Administration. Photos credited to anyone else are not used."),
    "na_domestic_animals": (build_na_domestic_animals,
                            "Wikimedia Commons breed and animal categories (dog breeds recognised by the AKC and the "
                            "CKC, cat breeds, horses, cattle, pigs, sheep, goats, poultry, rabbits, pets, pet birds "
                            "and reptiles, and working and service dogs): captions CC0; pictures CC0, public domain "
                            "or CC BY, each with its author and file page below. https://commons.wikimedia.org"),
}

# How many pictures a full build takes from each (GBIF answers about one species a second; Commons about one
# picture a second).
NA_ANIMAL_LIMITS = {
    "na_wild_mammals": 7000,      # about 420 species with open photos (25 each, 50 for the commonest 50)
    "na_birds": 12000,            # about 900 species (14 each, 28 for the commonest, 7 past the 400th)
    "na_herps_fish": 10000,       # reptiles, amphibians and fish (14 each)
    "na_insects": 12000,          # thousands of species, pests first (8 each)
    "na_invertebrates": 5000,     # snails, crustaceans, millipedes, worms, sea life (10 each)
    "na_animal_signs": 5000,      # tracks, scat, nests, eggs, shed skins, feathers, young animals (6 each)
    "na_domestic_animals": 8000,  # about 500 breeds, kinds, pets and pieces of equipment, balanced
    "noaa_fisheries_species": 800,  # 309 species profiles, at most 6 NOAA photos each
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one North American animal pack builder.")
    parser.add_argument("key", choices=sorted(NA_ANIMAL_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    entries = NA_ANIMAL_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    places = collections.Counter(row.get("place", "not stated") for _, data, row in entries if data is not None)
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, {child_count(entries)} rows marked child; "
        f"places: " + ", ".join(f"{p} {n}" for p, n in places.most_common(12)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
