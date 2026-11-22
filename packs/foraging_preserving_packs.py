"""Picture packs for EDIBLE WILD PLANTS AND FORAGING and HOME FOOD PRESERVING (the owner's request of 2026-11-22). Used
by build_packs.py in the same way as its own PACKS: each builder is build_<key>(limit) and returns [(file name, JPEG
bytes or None, row)]; a picture with more than one question comes once with its JPEG and then as (None, None, row)
rows naming the same picture. The limit counts pictures.

Why: the plant identification packs (plant_id_packs.py) already hold the poisonous plants, the common mushrooms and a
few wild edibles (wild carrot, ramsons, elder, nettle, dandelion, blackberry, blueberry, staghorn sumac). These packs
add the wild foods foragers gather by region and season (greens, berries, nuts, roots, flowers and seaweeds), more
deadly lookalikes, more edible and deadly mushrooms, and the jars, pickles, jams, dried and fermented foods of home
preserving. No category, species or label of another pack is repeated (packs/test_foraging_preserving.py checks).

Answers say only what the source says (a Commons category's name; an iNaturalist observation's research-grade
species) with the lookalike or preparation warning the reference books give, and the safety rule that fits; no answer
says a wild plant or mushroom is safe to eat:
  FORAGE_NOTE    never eat a wild plant unless an expert has confirmed it in person; lookalikes.
  MUSHROOM_NOTE  never eat a wild mushroom unless an expert has confirmed it; deadly lookalikes; Poison Control.
  POISON_NOTE    poisonous: never eat, taste or touch; Poison Control 1-800-222-1222; children and pets.
  PRESERVE_NOTE  tested recipes, pressure canner for low-acid foods, altitude, throw out bulging jars (botulism).
(The kit's foraging_preserving_sources.py and textbooks/foraging.py and preserving.py say the same things.)

The packs (FORAGING_PRESERVING_PACKS):
  commons_wild_food_plants  Wikimedia Commons (CC0, public domain or CC BY files only): purslane, lamb's quarters,
                            chickweed, ramps, ostrich fern fiddleheads, milkweed, cattail, burdock, Jerusalem
                            artichoke, watercress, sorrel and wood sorrel, plantain, violets, daylilies; serviceberry,
                            pawpaw, persimmon, red mulberry, American elderberry, wild grape, lowbush blueberry,
                            cranberry, wild strawberry, wild black cherry, rose hips, hawthorn, sloes; black walnut,
                            shagbark hickory, hazel and sweet chestnut; dulse, sea lettuce, winged kelp, sugar kelp
                            and oarweed; and the lookalikes autumn crocus, lords-and-ladies, fool's parsley,
                            hemlock water-dropwort, moonseed, bracken, doll's eyes, bluebell and yellow flag iris.
  commons_wild_mushrooms    Commons: honey fungus, parasol, shaggy ink cap, lion's mane, hen of the woods,
                            cauliflower fungus, beefsteak fungus, saffron milk cap, horn of plenty, hedgehog
                            mushroom, field mushroom and the cinnabar chanterelle; and the dangerous ones: the
                            green-spored parasol (false parasol), sulphur tuft, deadly webcap, yellow stainer, livid
                            entoloma, fool's funnel, the sickener and a deadly dapperling.
  commons_home_preserving   Commons: mason, Weck, Kilner and jam jars; pickling, pickles, pickled vegetables,
                            cucumbers and eggs; sauerkraut, kimchi and fermented food; jam, jams and jellies,
                            marmalade and chutney; dried fruit, tomatoes, mushrooms, meat and fish, jerky, salted and
                            smoked fish, food drying, freeze-dried food and food preservation.
  inat_wild_edibles         iNaturalist research-grade observations of wild edible plants, mushrooms and their
                            deadly lookalikes in North America, the records from GBIF and the photos from the
                            iNaturalist Open Dataset (CC0 or CC BY photos only, each photo's own licence checked);
                            iNaturalist's website and API are never read.

Not repeated here: plant_id_packs (poison ivy, hemlocks, death cap, destroying angels, morels, chanterelles, oyster
mushrooms, porcini, chicken of the woods, puffballs, wild carrot, ramsons, elder, nettle, dandelion, blackberry,
highbush blueberry, staghorn sumac), homestead_packs (Root cellars), device_packs (Food dehydrators),
outdoor_cooking_packs (smokers, smoked meat, canned food and the Open Images labels Canning and Mason jar) and
home_packs (Pressure cookers).

    python packs/foraging_preserving_packs.py commons_home_preserving --limit 8      (prints a few rows: a quick check)
"""

import re
import sys

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, fetch_all, say, pass_random
from gaps_oi_packs import QUICK

# ----------------------------------------------------------------- the safety notes (the kit uses the same words)

FORAGE_NOTE = ("Foraging: never eat a wild plant unless an expert has confirmed it in person; deadly lookalikes "
               "exist, and a picture is never enough.")
MUSHROOM_NOTE = ("Mushrooms: never eat a wild mushroom unless an expert has confirmed it in person; deadly ones look "
                 "like edible ones, and a picture is never enough. If someone ate a wild mushroom and feels ill, call "
                 "Poison Control at 1-800-222-1222 or 911.")
POISON_NOTE = ("Poisonous: never eat, taste or touch an unknown plant, and keep children and pets away; if someone "
               "may have eaten it, call Poison Control at 1-800-222-1222 (US), or 911 if they are very ill.")
PRESERVE_NOTE = ("Home preserving: follow tested, current recipes (the USDA Complete Guide to Home Canning); process "
                 "low-acid foods such as vegetables and meat in a pressure canner, adjust for altitude, and throw away "
                 "bulging, leaking or foul-smelling jars without tasting them: botulism can kill.")
ASK_PLANT = "What plant is this?"
ASK_MUSHROOM = "What mushroom is this?"
ASK_SEAWEED = "What seaweed is this?"
ASK_FOOD = "What is this?"


def wild(category, words, note=FORAGE_NOTE, ask=ASK_PLANT, deeper=False):
    """A Commons spec: (category, deeper, [(question, "This is <words>." and the note)])."""
    return (category, deeper, [(ask, f"This is {words}. {note}")])


def jar(category, words, deeper=False):
    """A Commons spec for home preserving: "This is <words>." and the preserving note."""
    return (category, deeper, [(ASK_FOOD, f"This is {words}. {PRESERVE_NOTE}")])


# ----------------------------------------------------------------- Commons: wild food plants and lookalikes

WILD_FOOD = [
    # greens and shoots
    wild("Portulaca oleracea", "purslane (Portulaca oleracea), a fleshy-leaved wild green; spurges, which have milky "
                               "sap, can look like it"),
    wild("Chenopodium album", "lamb's quarters (Chenopodium album), a wild green"),
    wild("Stellaria media", "chickweed (Stellaria media), a small wild green"),
    wild("Allium tricoccum", "ramps or wild leeks (Allium tricoccum), which smell of onion; poisonous lily of the "
                             "valley and false hellebore look like them, and digging ramps is banned in some parks"),
    wild("Matteuccia struthiopteris", "ostrich fern fiddleheads (Matteuccia struthiopteris), which must be cooked "
                                      "well; bracken and other ferns look like them"),
    wild("Asclepias syriaca", "common milkweed (Asclepias syriaca); its young shoots look like poisonous dogbane, and "
                              "it must be cooked"),
    wild("Typha latifolia", "cattail (Typha latifolia); young poisonous irises look like its shoots"),
    wild("Arctium lappa", "greater burdock (Arctium lappa), whose root is eaten"),
    wild("Helianthus tuberosus", "Jerusalem artichoke (Helianthus tuberosus), a sunflower with edible tubers"),
    wild("Nasturtium officinale", "watercress (Nasturtium officinale); gather it only from clean water, as it grows "
                                  "beside poisonous water plants such as water hemlock"),
    wild("Rumex acetosa", "common sorrel (Rumex acetosa); poisonous lords-and-ladies leaves can look like it"),
    wild("Oxalis acetosella", "wood sorrel (Oxalis acetosella)"),
    wild("Plantago major", "broadleaf plantain (Plantago major)"),
    wild("Viola sororia", "common blue violet (Viola sororia)"),
    wild("Hemerocallis fulva", "orange daylily (Hemerocallis fulva); daylilies are deadly to cats"),
    # berries and fruit
    wild("Amelanchier", "serviceberry or juneberry (Amelanchier)", deeper=True),
    wild("Asimina triloba", "pawpaw (Asimina triloba), a native fruit tree"),
    wild("Diospyros virginiana", "American persimmon (Diospyros virginiana), whose fruit is very astringent until "
                                 "fully ripe"),
    wild("Morus rubra", "red mulberry (Morus rubra)"),
    wild("Sambucus canadensis", "American elderberry (Sambucus canadensis); its leaves, stems, roots and unripe or "
                                "raw berries are poisonous"),
    wild("Vitis riparia", "riverbank grape (Vitis riparia), a wild grape; poisonous moonseed looks like it"),
    wild("Vaccinium angustifolium", "lowbush blueberry (Vaccinium angustifolium)"),
    wild("Vaccinium macrocarpon", "American cranberry (Vaccinium macrocarpon)"),
    wild("Fragaria vesca", "wild strawberry (Fragaria vesca)"),
    wild("Prunus serotina", "black cherry (Prunus serotina); its leaves, twigs and seeds are poisonous"),
    wild("Rosa canina", "dog rose (Rosa canina), whose hips are gathered; the hairs inside the hips irritate"),
    wild("Crataegus monogyna", "common hawthorn (Crataegus monogyna); its seeds are poisonous"),
    wild("Prunus spinosa", "blackthorn (Prunus spinosa), whose fruits are sloes"),
    # nuts
    wild("Juglans nigra", "black walnut (Juglans nigra)"),
    wild("Carya ovata", "shagbark hickory (Carya ovata), with shaggy bark and edible nuts"),
    wild("Corylus avellana", "common hazel (Corylus avellana), whose nuts are hazelnuts"),
    wild("Castanea sativa", "sweet chestnut (Castanea sativa); poisonous horse chestnuts (conkers) look like its nuts"),
    # seaweeds
    wild("Palmaria palmata", "dulse (Palmaria palmata), a red seaweed; gather seaweed only from clean water where it "
                             "is allowed", ask=ASK_SEAWEED),
    wild("Ulva lactuca", "sea lettuce (Ulva lactuca), a green seaweed; gather seaweed only from clean water",
         ask=ASK_SEAWEED),
    wild("Alaria esculenta", "winged kelp (Alaria esculenta), a brown seaweed", ask=ASK_SEAWEED),
    wild("Saccharina latissima", "sugar kelp (Saccharina latissima), a brown seaweed", ask=ASK_SEAWEED),
    wild("Laminaria digitata", "oarweed (Laminaria digitata), a kelp", ask=ASK_SEAWEED),
    # deadly and poisonous lookalikes
    wild("Colchicum autumnale", "autumn crocus (Colchicum autumnale), deadly; its leaves look like wild garlic's",
         POISON_NOTE),
    wild("Arum maculatum", "lords-and-ladies (Arum maculatum), poisonous; its leaves look like sorrel's and wild "
                           "garlic's", POISON_NOTE),
    wild("Aethusa cynapium", "fool's parsley (Aethusa cynapium), poisonous; it looks like parsley and wild carrot",
         POISON_NOTE),
    wild("Oenanthe crocata", "hemlock water-dropwort (Oenanthe crocata), one of the most poisonous plants in Britain; "
                             "it looks like wild celery and parsnip", POISON_NOTE),
    wild("Menispermum canadense", "moonseed (Menispermum canadense), poisonous; its berries look like wild grapes",
         POISON_NOTE),
    wild("Pteridium aquilinum", "bracken (Pteridium aquilinum), a fern that is poisonous to eat; its shoots look like "
                                "edible fiddleheads", POISON_NOTE),
    wild("Actaea pachypoda", "doll's eyes or white baneberry (Actaea pachypoda), whose berries are poisonous",
         POISON_NOTE),
    wild("Hyacinthoides non-scripta", "bluebell (Hyacinthoides non-scripta), poisonous; its leaves grow among wild "
                                      "garlic", POISON_NOTE),
    wild("Iris pseudacorus", "yellow flag iris (Iris pseudacorus), poisonous; its young shoots look like cattail's",
         POISON_NOTE),
]

# ----------------------------------------------------------------- Commons: more wild mushrooms

MUSHROOMS = [
    wild("Armillaria mellea", "honey fungus (Armillaria mellea); the deadly Galerina looks like it", MUSHROOM_NOTE,
         ASK_MUSHROOM),
    wild("Macrolepiota procera", "a parasol mushroom (Macrolepiota procera); the poisonous green-spored parasol and "
                                 "deadly Amanitas look like it", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Coprinus comatus", "a shaggy ink cap or shaggy mane (Coprinus comatus)", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Hericium erinaceus", "lion's mane (Hericium erinaceus), a toothed fungus on trees", MUSHROOM_NOTE,
         ASK_MUSHROOM),
    wild("Grifola frondosa", "hen of the woods or maitake (Grifola frondosa)", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Sparassis crispa", "cauliflower fungus (Sparassis crispa)", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Fistulina hepatica", "beefsteak fungus (Fistulina hepatica)", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Lactarius deliciosus", "saffron milk cap (Lactarius deliciosus); other milk caps are poisonous",
         MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Craterellus cornucopioides", "horn of plenty or black trumpet (Craterellus cornucopioides)", MUSHROOM_NOTE,
         ASK_MUSHROOM),
    wild("Hydnum repandum", "a hedgehog mushroom (Hydnum repandum), with spines under its cap", MUSHROOM_NOTE,
         ASK_MUSHROOM),
    wild("Agaricus campestris", "a field mushroom (Agaricus campestris); the yellow stainer and deadly destroying "
                                "angels look like it", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Cantharellus cinnabarinus", "a cinnabar chanterelle (Cantharellus cinnabarinus)", MUSHROOM_NOTE,
         ASK_MUSHROOM),
    wild("Chlorophyllum molybdites", "the green-spored parasol or false parasol (Chlorophyllum molybdites), "
                                     "poisonous; it looks like edible parasols", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Hypholoma fasciculare", "sulphur tuft (Hypholoma fasciculare), poisonous; it grows in clusters like honey "
                                  "fungus", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Cortinarius rubellus", "the deadly webcap (Cortinarius rubellus), deadly: it harms the kidneys days after "
                                 "it is eaten", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Agaricus xanthodermus", "the yellow stainer (Agaricus xanthodermus), poisonous; it looks like field "
                                  "mushrooms", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Entoloma sinuatum", "the livid entoloma (Entoloma sinuatum), poisonous", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Clitocybe rivulosa", "the fool's funnel (Clitocybe rivulosa), poisonous", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Russula emetica", "the sickener (Russula emetica), poisonous", MUSHROOM_NOTE, ASK_MUSHROOM),
    wild("Lepiota brunneoincarnata", "a deadly dapperling (Lepiota brunneoincarnata), deadly", MUSHROOM_NOTE,
         ASK_MUSHROOM),
]

# ----------------------------------------------------------------- Commons: home preserving

PRESERVING = [
    jar("Mason jars", "a mason jar, a glass canning jar with a two-piece lid (a flat lid and a screw band)"),
    jar("Weck jars", "a Weck jar, a glass preserving jar with a glass lid, rubber ring and clips"),
    jar("Kilner jars", "a Kilner jar, a British glass preserving jar"),
    jar("Jam jars", "a jam jar", True),
    jar("Pickling", "pickling: preserving food in vinegar or brine", True),
    jar("Pickles", "pickles"),
    jar("Pickled vegetables", "pickled vegetables"),
    jar("Pickled cucumbers", "pickled cucumbers"),
    jar("Pickled eggs", "pickled eggs"),
    jar("Sauerkraut", "sauerkraut, cabbage fermented with salt"),
    jar("Kimchi", "kimchi, Korean fermented vegetables"),
    jar("Fermented food", "fermented food"),
    jar("Jam", "jam, fruit cooked with sugar"),
    jar("Jams and jellies", "jams and jellies"),
    jar("Marmalade", "marmalade, a citrus preserve"),
    jar("Chutney", "chutney"),
    jar("Dried fruit", "dried fruit"),
    jar("Dried tomatoes", "dried tomatoes"),
    jar("Dried mushrooms", "dried mushrooms"),
    jar("Dried meat", "dried meat; for jerky, meat is heated to 160 F (poultry 165 F) before or after drying"),
    jar("Jerky", "jerky, dried strips of meat; meat is heated to 160 F (poultry 165 F) before or after drying", True),
    jar("Dried fish", "dried fish"),
    jar("Salted fish", "salted fish"),
    jar("Smoked fish", "smoked fish; cold-smoked fish is not cooked"),
    jar("Food drying", "food being dried to preserve it", True),
    jar("Freeze-dried food", "freeze-dried food"),
    jar("Food preservation", "food preservation"),
]

# ----------------------------------------------------------------- iNaturalist (through GBIF)

# (scientific name, the words after "This is", the note: wild plants FORAGE_NOTE, mushrooms MUSHROOM_NOTE,
# poisonous plants POISON_NOTE). The species of plant_id_packs' Commons categories (the death cap, destroying angel
# Amanita bisporigera, deadly Galerina, false morel, water and poison hemlock, false hellebore, chicken of the woods)
# are left to it; this list takes their North American relatives and the wild foods it lacks.
INAT_WILD = [
    ("Allium tricoccum", "ramps or wild leeks; poisonous lily of the valley and false hellebore look like them",
     FORAGE_NOTE),
    ("Matteuccia struthiopteris", "ostrich fern, whose fiddleheads must be cooked well; bracken looks like it",
     FORAGE_NOTE),
    ("Asclepias syriaca", "common milkweed; its young shoots look like poisonous dogbane", FORAGE_NOTE),
    ("Typha latifolia", "cattail; young poisonous irises look like its shoots", FORAGE_NOTE),
    ("Portulaca oleracea", "purslane; spurges, which have milky sap, can look like it", FORAGE_NOTE),
    ("Nasturtium officinale", "watercress; it grows beside poisonous water plants such as water hemlock",
     FORAGE_NOTE),
    ("Asimina triloba", "pawpaw", FORAGE_NOTE),
    ("Diospyros virginiana", "American persimmon", FORAGE_NOTE),
    ("Sambucus canadensis", "American elderberry; its leaves, stems and raw berries are poisonous", FORAGE_NOTE),
    ("Vitis riparia", "riverbank grape; poisonous moonseed looks like it", FORAGE_NOTE),
    ("Juglans nigra", "black walnut", FORAGE_NOTE),
    ("Carya ovata", "shagbark hickory", FORAGE_NOTE),
    ("Amelanchier", "a serviceberry", FORAGE_NOTE),
    ("Morus rubra", "red mulberry", FORAGE_NOTE),
    ("Palmaria palmata", "dulse, a red seaweed", FORAGE_NOTE),
    ("Laetiporus cincinnatus", "white-pored chicken of the woods, a shelf fungus", MUSHROOM_NOTE),
    ("Grifola frondosa", "hen of the woods", MUSHROOM_NOTE),
    ("Hericium erinaceus", "lion's mane", MUSHROOM_NOTE),
    ("Coprinus comatus", "a shaggy mane", MUSHROOM_NOTE),
    ("Morchella americana", "a morel; poisonous false morels look like it", MUSHROOM_NOTE),
    ("Armillaria mellea", "honey fungus; the deadly Galerina looks like it", MUSHROOM_NOTE),
    ("Amanita ocreata", "the western destroying angel, a deadly white mushroom", MUSHROOM_NOTE),
    ("Chlorophyllum molybdites", "the green-spored parasol, poisonous", MUSHROOM_NOTE),
    ("Omphalotus illudens", "the eastern jack-o'-lantern mushroom, poisonous; it looks like chanterelles",
     MUSHROOM_NOTE),
    ("Gyromitra brunnea", "a false morel, poisonous; it looks like true morels", MUSHROOM_NOTE),
    ("Cicuta douglasii", "western water hemlock, deadly; it looks like wild carrot and parsnip", POISON_NOTE),
    ("Menispermum canadense", "moonseed, poisonous; its berries look like wild grapes", POISON_NOTE),
    ("Apocynum cannabinum", "dogbane, poisonous; its young shoots look like milkweed's", POISON_NOTE),
    ("Veratrum californicum", "California false hellebore (corn lily), poisonous", POISON_NOTE),
    ("Iris versicolor", "blue flag iris, poisonous; its young shoots look like cattail's", POISON_NOTE),
]
ASK_INAT = {FORAGE_NOTE: ASK_PLANT, MUSHROOM_NOTE: ASK_MUSHROOM, POISON_NOTE: ASK_PLANT}


def inat_answer(latin, words, note):
    """The answer of one iNaturalist picture: "This is <name> (<latin>)<the rest of the words>." and its note, the
    scientific name placed right after the plant's or mushroom's own name (words up to the first comma or
    semicolon): "This is ramps or wild leeks (Allium tricoccum); poisonous lily of the valley ... look like them." """
    name, rest = re.match(r"([^,;]+)(.*)", words).groups()
    return f"This is {name} ({latin}){rest}. {note}"


def build_inat_wild_edibles(limit):
    """inat_wild_edibles: for each species of INAT_WILD, research-grade iNaturalist records in the United States and
    Canada whose photo is CC0 or CC BY (each photo's own licence checked), the records from GBIF and the photos from
    the iNaturalist Open Dataset (na_animal_packs' shared reader); iNaturalist's website and API are never read."""
    from na_animal_packs import inat_taxon, inat_pages, inat_photo, inat_photo_id, inat_credit, inat_country, \
        photo_url, INAT_OPEN
    from land_industry_packs import place_row
    from food_packs import with_twins
    s, items, rng = session(), [], pass_random(1931)
    per_species = limit // len(INAT_WILD) + 1
    for latin, words, note in INAT_WILD:
        taxon = inat_taxon(s, latin)
        if not taxon:
            say(f"  GBIF: {latin} not found")
            continue
        got = 0
        for record in inat_pages(s, dict(taxon, license=INAT_OPEN, country=["US", "CA"]), rng, pages=1):
            if got >= per_species:
                break
            media, licence = inat_photo(record)
            if not media:
                continue
            row = {"question": ASK_INAT[note], "answer": inat_answer(latin, words, note),
                   "credit": inat_credit(record, media, licence), **inat_country(record)}
            rows = [row] + ([place_row(row, row["place"])] if row.get("place") else [])
            items.append((f"inat-wild-{inat_photo_id(media)}.jpg", photo_url(media["identifier"]), rows))
            got += 1
        say(f"  iNaturalist (on GBIF) {latin}: {got}")
    rng.shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit])


def build_commons_wild_food_plants(limit):
    """The commons_wild_food_plants pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(WILD_FOOD, limit, "wildfood")


def build_commons_wild_mushrooms(limit):
    """The commons_wild_mushrooms pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(MUSHROOMS, limit, "wildmush")


def build_commons_home_preserving(limit):
    """The commons_home_preserving pack (see the module docstring)."""
    from home_packs import build_commons_topic
    return build_commons_topic(PRESERVING, limit, "homepreserve")


# ----------------------------------------------------------------- the packs

COMMONS_LICENCE = ("Wikimedia Commons (https://commons.wikimedia.org): files CC0, public domain or CC BY (credited "
                   "below) of {what} categories.")
INAT_LICENCE = ("iNaturalist research-grade observations through GBIF (https://www.gbif.org), photos from the "
                "iNaturalist Open Dataset: each photo CC0 or CC BY (checked photo by photo), photographer credited "
                "below.")
FORAGING_PRESERVING_PACKS = {
    "commons_wild_food_plants": (build_commons_wild_food_plants, COMMONS_LICENCE.format(
        what="wild green, berry, nut, root, flower, seaweed and poisonous lookalike plant")),
    "commons_wild_mushrooms": (build_commons_wild_mushrooms, COMMONS_LICENCE.format(
        what="edible and poisonous wild mushroom species")),
    "commons_home_preserving": (build_commons_home_preserving, COMMONS_LICENCE.format(
        what="preserving jar, pickle, ferment, jam, dried and salted food")),
    "inat_wild_edibles": (build_inat_wild_edibles, INAT_LICENCE),
}
FORAGING_PRESERVING_LIMITS = {
    "commons_wild_food_plants": 1500,     # 47 categories
    "commons_wild_mushrooms": 800,        # 20 categories
    "commons_home_preserving": 900,       # 27 categories
    "inat_wild_edibles": 1600,            # 30 species, about 53 each
}
# The packs that read Wikimedia Commons (build_packs.COMMONS_KEYS).
FORAGING_PRESERVING_COMMONS_KEYS = ("commons_wild_food_plants", "commons_wild_mushrooms", "commons_home_preserving")
# The Commons category specs of the packs (for the self-test).
FORAGING_PRESERVING_SPECS = WILD_FOOD + MUSHROOMS + PRESERVING


def main(argv=None):
    """Build one pack with a small limit and print its rows (a quick check)."""
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Try a foraging or home preserving pack builder.")
    parser.add_argument("key", choices=sorted(FORAGING_PRESERVING_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args(argv)
    QUICK["on"] = False
    entries = FORAGING_PRESERVING_PACKS[args.key][0](args.limit)
    for name, data, row in entries:
        print(name, "(picture)" if data else "", json.dumps(row, ensure_ascii=False)[:400])
    print(f"{sum(1 for _, d, _ in entries if d)} pictures, {len(entries)} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
