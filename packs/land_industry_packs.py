"""Pack builders for the land and the work done on it: agriculture and farming, the environment, industry, mining,
energy, construction and transport infrastructure. Used by build_packs.py in the same way as its own PACKS: each
builder is build_<key>(limit) and returns [(file name, JPEG bytes or None, row)], where a row is {"question",
"answer", "credit"}, plus "place" where the source says where the photo was taken (places.py), "child": True where the
words name a child (the picture-making trainer leaves those rows out) and "content": "graphic" for industrial
accidents. A picture with more than one question comes once with its JPEG and then again as (None, None, row) rows
whose "file" names the same picture (food_packs.with_twins), so the zip holds each picture only once. The limit counts
pictures.

Answers are each source's own captions, or fixed sentences made from its own labels (nothing is written by an AI
model). Questions: "Describe this picture." (captions of 6 words or more), "What crop is this?", "What machine is
this?", "Where was this photo taken?" (when the record gives the place), "Is this plant healthy?" (plant-disease
sets) and "What kind of litter is this, and which bin does it go in?" (only where the dataset's own category
settles the bin).

Every licence was checked at its source in November 2026 (the Mendeley Data, Zenodo or Harvard Dataverse record, the
makers' README, or the agency's copyright page), not only on the copy the pictures are read from.

The packs (all open: CC0, public domain, CC BY, MIT or Apache):
  agml_plant_health  Crop leaves and plants, healthy or with a named disease or pest, photographed in fields in
                     Africa and Asia: 17 datasets, each CC BY 4.0 on Mendeley Data or Zenodo (iBean: MIT), read from
                     the Project-AgML copies on Hugging Face (their "raw" photos, never the augmented copies; sets
                     whose only copy mixes in augmented pictures are left out). Maize (Tanzania), beans (Uganda),
                     banana (Ethiopia), potato (Tanzania), apple (Kashmir, India), grape (Niphad, India), soybean
                     (Maharashtra, India), durian (Vietnam), date palm (Iraq), rice, sugarcane, watermelon,
                     cauliflower, cotton, aubergine, moringa and taro (West Africa). "Is this plant healthy?" and "What crop is
                     this?". (PlantVillage, PlantDoc and Pl@ntNet are already kit entries.)
  agml_weeds         Weeds where they grow: DeepWeeds (eight weeds of northern Australia, CC BY 4.0), MH-Weed16 (16
                     weeds of Indian farms, CC BY 4.0) and the rice-field weeds of Bangladesh (CC BY 4.0). "What weed
                     is this?"
  agml_harvest       Is it ready to pick? Banana bunches on the plant in Madeira (ready to cut or not) and dragon
                     fruit (ripe or not), each CC BY 4.0 on Mendeley Data.
  gwhd_wheat         Global Wheat Head Dataset 2021 (CC BY 4.0, Zenodo 5092309): wheat fields seen from above in
                     12 countries, with the growth stage and the number of ears people outlined. "What crop is this?"
                     and "Where was this photo taken?" (the country).
  poultry_droppings  Poultry fecal images from farms in Arusha and Kilimanjaro, Tanzania (CC BY 4.0, Zenodo 4628934),
                     healthy, coccidiosis, salmonella or Newcastle disease, as farmers' phones photographed them.
                     "Do these chicken droppings show signs of disease?"
  inat_crops         iNaturalist observations of cultivated crops and fruit trees (photos CC0 or CC BY only, the
                     name agreed by at least two people): wheat, rice, maize, cassava, coffee, cacao, tea, bananas,
                     apples on the tree and others. "What crop is this?" (with "with fruit" from the observer's
                     fruiting annotation), and the country where the photo was taken.
  trashnet           TrashNet (Gary Thung and Mindy Yang, MIT licence): single pieces of rubbish photographed on a
                     white board, by recycling category (cardboard, glass, metal, paper, plastic, general rubbish).
                     "What kind of litter is this, and which bin does it go in?"
  taco_litter        TACO, Trash Annotations in Context (Proenca and Simoes, CC BY 4.0, Zenodo 3587843): litter where
                     it was dropped (woods, roads, beaches), every piece outlined and named. "What litter is in this
                     picture?" and, when the pieces share one recycling stream, the bin question.
  ccsn_clouds        CCSN, Cirrus Cumulus Stratus Nimbus (Pu Liu, CC0, Harvard Dataverse): the sky in 11 cloud types
                     of the World Meteorological Organization, and aircraft contrails. "What kind of cloud is this?"
  weather_images     Multi-class Weather Dataset (Gbeminiyi Ajayi, CC BY 4.0, Mendeley Data 4drtyfjtfy): cloudy,
                     rainy, sunny and sunrise scenes. "What is the weather like in this picture?"
  eurosat            EuroSAT (Helber et al., MIT licence; Copernicus Sentinel-2 data): small satellite views of
                     European land, ten kinds (crops, forest, pasture, rivers, motorways, industry, housing ...). Only
                     a few hundred: the pictures are 64 by 64 pixels. "What does this satellite picture show?"
  commons_land_industry  Wikimedia Commons categories of farming (tractors, combine harvesters, paddy fields,
                     greenhouses, irrigation, livestock, fish farms, markets), the environment (deforestation,
                     wildfires, floods, drought, litter, plastic, oil spills, coral reefs, glaciers), industry
                     (factories, assembly lines, robots, warehouses, forklifts, welding, ports and containers), mining
                     and energy (mines, quarries, oil rigs and refineries, power stations, wind turbines, solar panels,
                     substations, pylons, pipelines) and construction (building sites, cranes, excavators, bridges,
                     dams, tunnels, railways). Pictures CC0, public domain or CC BY only (never BY-SA, NC or ND: those
                     are the kit's commons_land_industry_sa). The category's question and the file's own caption.
  loc_haer           Library of Congress, Historic American Engineering Record (HAER, 1969 onwards, US National Park
                     Service): photographs of dams, bridges, mines, mills, factories, power plants, canals and
                     railways across the USA, each with the survey's own photo caption ("DAM, VIEW EAST, VIEW
                     UPSTREAM") and the place. US government work, "No known restrictions on images made by the U.S.
                     Government"; copies of older pictures from other sources ("PHOTOCOPY OF ...") and drawings are
                     left out.
  plitter_street     pLitterStreet (Mandhati et al., Zenodo 8288500, CC BY 4.0): photos from cameras on vehicles
                     driving through towns and villages in Thailand, Sri Lanka and the Mekong region, every piece of
                     litter boxed (plastic bags, bottles, cups, face masks, sachets, straws, rope, piles). "What
                     litter is in this picture?" and "Where was this photo taken?".
  plp_floating_targets  Plastic Litter Projects 2019 and 2021 (University of the Aegean, Zenodo 3752719 and 7085112,
                     CC BY 4.0): drone photos of floating plastic test targets off Lesvos, Greece, laid out to test
                     whether satellites can see floating plastic. A few dozen photos; the satellite data is not used.
  usda_ars           US Department of Agriculture, Agricultural Research Service image gallery: field and laboratory
                     research, crops, insects and farm work, with ARS's captions. Public domain ("copyright-free,
                     public domain, images unless otherwise indicated"; pages that say otherwise are left out).

Already in the kit, so not repeated here: the Farm Security Administration photographs (documentary_packs loc_fsa),
DOCUMERICA, the EPA's 1970s survey of American life and pollution (archive_packs nara), the USGS gallery and NASA Earth
Observatory (documentary_packs), PlantVillage, PlantDoc and Pl@ntNet (training-kit/kit/extra_sources.py), cattle
foot-and-mouth and lumpy skin disease (build_packs cattle_health), fresh and rotten fruit (fresh_rotten) and the
Commons breed categories of cattle, sheep, goats, pigs and chickens (everyday_packs commons_breeds).

Share-alike, non-commercial and research collections on the same subjects, and those needing sign-up or left out, are
in training-kit/kit/land_industry_sources.py.

    python packs/land_industry_packs.py trashnet --limit 8      (prints a few rows: a quick check of one builder)
"""

import csv
import io
import json
import os
import random
import re
import sys
import time

import build_packs  # noqa: F401 - loaded first: the other pack files and build_packs import each other
from build_packs import session, clean, smaller, fetch_all, say, article, first_sentences, NARRATE, ALT_TEXT  # noqa: F401,E501
from food_packs import sentence, listed, with_twins, count_pictures, commons_members, commons_entries, commons_place
from expression_packs import CHILD
from world_life_packs import remote_zip
from documentary_packs import tidy, usable, picture_rows, finish, get_json, place_words, ASK_WHERE, LOC
from disability_packs import standard_thumb
from places import where, place_name, country_named

ASK_CROP = "What crop is this?"
ASK_MACHINE = "What machine is this?"
ASK_HEALTHY = "Is this plant healthy?"
ASK_WEED = "What weed is this?"
ASK_BIN = "What kind of litter is this, and which bin does it go in?"
ASK_LITTER = "What litter is in this picture?"
ASK_SHOWN = "What is shown in this picture?"
LOCAL_RULES = "Local recycling rules differ, so check yours."
# Words of injury or death: a row whose words have them is marked "content": "graphic".
INJURY = re.compile(r"\b(injur\w*|wounded|casualt\w*|dead|deaths?|died|killed|bod(y|ies)|blood\w*|corpses?|"
                    r"victims?|fatal\w*)\b", re.I)
NUDE = re.compile(r"\b(nude|naked|nudity|topless|undress\w*|erotic|sex\w*|porn\w*|lingerie|underwear)\b", re.I)


def a_or_an(phrase):
    """ "a" or "an" before a phrase."""
    return article(phrase)


def marked(row, *texts):
    """The row with "child": True when any of texts names a child, and "content": "graphic" when any names an injury
    or a death."""
    joined = " ".join(t or "" for t in texts)
    if CHILD.search(joined):
        row = dict(row, child=True)
    if INJURY.search(joined):
        row = dict(row, content="graphic")
    return row


def place_row(row, place):
    """The "Where was this photo taken?" twin of a row, for a picture whose source gives its place."""
    return dict(row, question=ASK_WHERE, answer=f"It was taken in {place_words(place)}.", **where(place))


# ----------------------------------------------------------------- Project-AgML copies on Hugging Face

AGML = "Project-AgML/"


def agml_label_names(pf):
    """The class names of an AgML parquet file's "label" column (from the Hugging Face features in its metadata)."""
    meta = json.loads((pf.schema_arrow.metadata or {}).get(b"huggingface", b"{}"))
    features = (meta.get("info") or {}).get("features") or {}
    label = features.get("label") or {}
    return label.get("names") or []


def agml_read(repo, config, quota, wanted, seed, label_column="label", most_groups=60):
    """Pictures of one AgML dataset: {label name: [JPEG bytes]} with at most quota of each label in wanted, read by
    row groups from its parquet files on Hugging Face (only the groups needed are downloaded, label column first).
    config: the folder of the "raw" photos ("raw/" or "data/")."""
    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    fs, rng = HfFileSystem(), random.Random(seed)
    files = [f for f in HfApi().list_repo_files(AGML + repo, repo_type="dataset")
             if f.startswith(config) and f.endswith(".parquet")]
    groups = []
    for name in files:
        try:
            pf = pq.ParquetFile(fs.open(f"datasets/{AGML}{repo}/{name}", "rb", block_size=1 << 20))
        except Exception:  # noqa: BLE001 - a file that cannot be opened is left out
            continue
        groups += [(pf, g) for g in range(pf.metadata.num_row_groups)]
    rng.shuffle(groups)
    got = {}
    for pf, g in groups[:most_groups]:
        if all(len(got.get(w, [])) >= quota for w in wanted):
            break
        try:
            labels = pf.read_row_group(g, columns=[label_column]).column(0).to_pylist()
        except Exception:  # noqa: BLE001 - next group
            continue
        names = agml_label_names(pf) if label_column == "label" else []
        values = [names[v] if names and isinstance(v, int) and v < len(names) else str(v) for v in labels]
        need = [i for i, v in enumerate(values) if v in wanted and len(got.get(v, [])) < quota]
        if not need:
            continue
        images = pf.read_row_group(g, columns=["image"]).column(0).to_pylist()
        for i in need:
            if len(got.setdefault(values[i], [])) < quota:
                data = smaller((images[i] or {}).get("bytes") or b"")
                if data:
                    got[values[i]].append(data)
    return got


# Each dataset: (Project-AgML repository, folder of its raw photos, crop, part of the plant shown, place or "",
# credit, {label: "" for healthy, a disease or pest in words, or None to leave the label out}).
AGML_HEALTH = [
    ("rice_disease_classification_bangladesh", "raw/", "rice", "plant", "",
     "Rice Leaf Disease and Pest Dataset, Mendeley Data vwv3nry3wr, CC BY 4.0",
     {"Healthy": "", "Insect": "insect damage", "Leaf Scald": "leaf scald", "Rice": None, "Rice Blast": "rice blast",
      "Rice Leaffolder": "damage by rice leaffolder caterpillars", "Rice Stripes": "rice stripe disease",
      "Rice Tungro": "rice tungro disease"}),
    ("maize_disease_classification", "data/", "maize", "plant", "Tanzania",
     "Maize Imagery Dataset - Tanzania (Mduma and Mayo), Mendeley Data fkw49mz3xs, CC BY 4.0",
     {"Healthy": "", "MLN": "maize lethal necrosis", "MSV": "maize streak virus"}),
    ("bean_disease_uganda", "data/", "bean", "leaf", "Uganda",
     "iBean dataset (Makerere AI Lab), MIT licence, https://github.com/AI-Lab-Makerere/ibean",
     {"healthy": "", "angular_leaf_spot": "angular leaf spot", "bean_rust": "bean rust"}),
    ("banana_leaf_disease_classification", "data/", "banana", "leaf", "Ethiopia",
     "Banana Leaf Disease Images, Mendeley Data rjykr62kdh, CC BY 4.0",
     {"healthy": "", "segatoka": "Sigatoka leaf spot", "xamthomonas": "Xanthomonas wilt"}),
    ("sugarcane_leaf_disease_classification", "data/", "sugarcane", "leaf", "",
     "Sugarcane Leaf Image Dataset, Mendeley Data 9twjtv92vk, CC BY 4.0",
     {"Healthy": "", "Banded Chlorosis": "banded chlorosis", "Brown Spot": "brown spot", "BrownRust": "brown rust",
      "Grassy shoot": "grassy shoot disease", "Pokkah Boeng": "pokkah boeng disease", "Sett Rot": "sett rot",
      "Smut": "smut", "Viral Disease": "a virus disease", "Yellow Leaf": "yellow leaf disease", "Dried": None}),
    ("grape_leaf_disease_classification", "data/", "grape", "leaf", "Niphad, India",
     "Niphad Grape Leaf Disease Dataset (NGLD), Mendeley Data 8nnd2ypcv3, CC BY 4.0",
     {"Healthy Leaves": "", "Bacterial Leaf Spot": "bacterial leaf spot", "Downy Mildew": "downy mildew",
      "Powdery Mildew": "powdery mildew"}),
    ("apple_leaf_disease_classification", "data/", "apple", "leaf", "Jammu and Kashmir, India",
     "Indigenous Dataset for Apple Leaf Disease Detection and Classification, Mendeley Data 9m2dcb5mmr, CC BY 4.0",
     {"Healthy": "", "Alternaria": "Alternaria leaf blotch", "Apple_Mosaic": "apple mosaic virus"}),
    ("soybean_leaf_disease_classification", "data/", "soybean", "leaf", "Maharashtra, India",
     "An India soyabean leaf dataset, Mendeley Data bshkvgbzpt, CC BY 4.0",
     {"Healthy": "", "Bacterial leaf Blight": "bacterial leaf blight", "Septoria_Brown_Spot": "Septoria brown spot",
      "Vein Necrosis": "vein necrosis", "Dry_leaf": None, "Root_images": None}),
    ("watermelon_disease_classification", "raw/", "watermelon", "plant", "",
     "Watermelon Disease Recognition Dataset, Mendeley Data ntzym554jp, CC BY 4.0",
     {"Healthy": "", "Anthracnose": "anthracnose", "Downy_Mildew": "downy mildew", "Mosaic_Virus": "mosaic virus"}),
    ("cauliflower_leaf_disease_classification", "data/", "cauliflower", "leaf", "",
     "Cauliflower Leaf Diseases dataset, Mendeley Data x995snz7p3, CC BY 4.0",
     {"Healthy": "", "Black Rot": "black rot", "Insect Hole": "insect damage: holes eaten in the leaf"}),
    ("durian_disease_classification_vietnam", "data/", "durian", "leaf", "Vietnam",
     "A Durian Leaf Image Dataset of Common Diseases in Vietnam, Mendeley Data pxzvksbwnj, CC BY 4.0",
     {"Leaf_Healthy": "", "Leaf_Algal": "algal leaf spot", "Leaf_Blight": "leaf blight",
      "Leaf_Colletotrichum": "anthracnose (Colletotrichum)", "Leaf_Phomopsis": "Phomopsis leaf spot",
      "Leaf_Rhizoctonia": "Rhizoctonia leaf blight"}),
    ("date_palm_leaf_disease_classification_iraq", "data/", "date palm", "leaf", "Iraq",
     "Image dataset of infected date palm leaves by dubas insects, Mendeley Data 2nh364p2bc, CC BY 4.0",
     {"Healthy": "", "Dubas": "dubas bugs and their honeydew", "Bug": "dubas bugs",
      "Honey": "honeydew left by dubas bugs"}),
    ("cotton_leaf_disease_classification", "raw/", "cotton", "leaf", "",
     "Cotton Leaf Image Dataset for Disease Classification, Mendeley Data t9hgvk2h9p, CC BY 4.0",
     {"Healthy_Leaf": "", "Alternaria_Leaf": "Alternaria leaf spot", "Bacterial_Blight": "bacterial blight",
      "Fusarium_Wilt": "Fusarium wilt", "Verticillium_Wilt": "Verticillium wilt"}),
    ("eggplant_leaf_disease_classification", "raw/", "aubergine (eggplant)", "leaf", "",
     "Eggplant Dataset, Mendeley Data 5drkk544k8, CC BY 4.0",
     {"Fresh Eggplant Leaf": "", "Aphids": "aphids", "Cercospora Leaf Spot": "Cercospora leaf spot",
      "Flea Beetles": "flea beetle damage", "Leaf Wilt": "leaf wilt", "Phytophthora Blight": "Phytophthora blight",
      "Powdery Mildew": "powdery mildew", "Tobacco Mosaic Virus": "tobacco mosaic virus", "Defect Eggplant": None,
      "Fresh Eggplant": None}),
    ("MoringaLeafNet_disease_classification", "raw/", "moringa", "leaf", "",
     "MoringaLeafNet, Mendeley Data w8sr775pjb, CC BY 4.0",
     {"Healthy": "", "Bacterial Leaf Spot": "bacterial leaf spot", "Cercospora Leaf Spot": "Cercospora leaf spot",
      "Yellow": "yellowing of the leaves"}),
    ("taro_blight_stage_classification", "data/", "taro", "leaf", "",
     "An Image Dataset of Taro Leaf Blight Disease Collected from the West African Sub-Region, Mendeley Data "
     "3knm93dkc5, CC BY 4.0",
     {"Healthy": "", "Early_Blight": "taro leaf blight at an early stage", "Mid_Blight": "taro leaf blight at a "
      "middle stage", "Late_Blight": "taro leaf blight at a late stage"}),
]
# Irish potato leaves from Mbeya, Tanzania (Zenodo 8286529, CC BY 4.0): one zip per class, read piece by piece.
POTATO = "https://zenodo.org/records/8286529/files/{}.zip?download=1"
POTATO_CLASSES = {"healthy": "", "earlyblt": "early blight", "lateblt": "late blight"}
POTATO_CREDIT = "Irish Potato Imagery Dataset for Early Detection of Crop Diseases (Zenodo 8286529), CC BY 4.0"


def health_rows(crop, part, disease, credit, place):
    """The two rows of a plant-health picture: "Is this plant healthy?" and "What crop is this?"."""
    if disease == "":
        healthy = f"Yes: this {crop} {part} looks healthy."
    else:
        healthy = f"No: this {crop} {part} shows signs of {disease}."
    name = crop.split(" (")[0]
    rows = [{"question": ASK_HEALTHY, "answer": healthy, "credit": credit},
            {"question": ASK_CROP, "answer": f"{name[:1].upper() + name[1:]}: this is {a_or_an(crop)} {crop} {part}.",
             "credit": credit}]
    return [dict(r, **where(place)) for r in rows]


def build_agml_plant_health(limit):
    """The plant-health pack: an equal share of each dataset in AGML_HEALTH (and the Tanzanian potato leaves), split
    evenly between its labels, each picture with "Is this plant healthy?" and "What crop is this?"."""
    per_set = limit // (len(AGML_HEALTH) + 1) + 1
    out = []
    for repo, config, crop, part, place, credit, labels in AGML_HEALTH:
        wanted = [k for k, v in labels.items() if v is not None]
        quota = max(1, per_set // len(wanted) + 1)
        try:
            got = agml_read(repo, config, quota, wanted, repo, most_groups=max(4, per_set // 20 + 3))
        except Exception as e:  # noqa: BLE001 - one dataset failing does not stop the pack
            say(f"  {repo}: not read ({str(e)[:100]})")
            continue
        found = 0
        for label, pictures in got.items():
            for data in pictures:
                out.append((f"agml-{repo[:30]}-{len(out)}.jpg", data,
                            health_rows(crop, part, labels[label], credit + f" (Project-AgML copy, "
                                        f"https://huggingface.co/datasets/{AGML}{repo})", place)))
                found += 1
        say(f"  {repo}: {found} pictures")
    try:
        quota = per_set // len(POTATO_CLASSES) + 1
        for cls, disease in POTATO_CLASSES.items():
            z = remote_zip(POTATO.format(cls))
            names = [n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))]
            random.Random(cls).shuffle(names)
            for n in names[:quota]:
                data = smaller(z.read(n))
                if data:
                    out.append((f"potato-{cls}-{len(out)}.jpg", data,
                                health_rows("potato", "leaf", disease, POTATO_CREDIT, "Mbeya, Tanzania")))
        say("  Tanzanian potato leaves read")
    except Exception as e:  # noqa: BLE001 - the rest of the pack is kept
        say(f"  potato leaves: not read ({str(e)[:100]})")
    random.Random(501).shuffle(out)
    return with_twins(out[:limit])


# ----------------------------------------------------------------- weeds

DEEPWEEDS = {"Chinee apple": "Chinee apple (Ziziphus mauritiana), a thorny shrub",
             "Lantana": "lantana (Lantana camara), a flowering shrub",
             "Parkinsonia": "parkinsonia (Parkinsonia aculeata), a thorny shrub or small tree",
             "Parthenium": "parthenium weed (Parthenium hysterophorus)",
             "Prickly acacia": "prickly acacia (Vachellia nilotica), a thorny tree",
             "Rubber vine": "rubber vine (Cryptostegia grandiflora), a climbing vine",
             "Siam weed": "Siam weed (Chromolaena odorata), a scrambling shrub",
             "Snake weed": "snakeweed (Stachytarpheta), a low, woody weed"}
MH_WEED16 = {"Asian_Pigeonwings_(Clitoria Ternatea)": "Asian pigeonwings (Clitoria ternatea)",
             "Bilayat_(Mexicana_Argemone)": "Mexican prickly poppy (Argemone mexicana)",
             "Choti_dudhi_(Euphorbia_hirta)": "asthma plant (Euphorbia hirta)",
             "Digitaria_SP_(Digitaria Sanguinalis )": "hairy crabgrass (Digitaria sanguinalis)",
             "Dwarf_cassia_(Chamaecrista pumila)": "dwarf cassia (Chamaecrista pumila)",
             "Gajar_gavat_(Parthenium hysterophorus)": "parthenium weed (Parthenium hysterophorus)",
             "Graceful_Sandmart_(Euphorbia hypericifolia)": "graceful spurge (Euphorbia hypericifolia)",
             "Harali_(Cynodon_dactylon)": "Bermuda grass (Cynodon dactylon)",
             "Kena_(Commplina_benghalensio)": "Benghal dayflower (Commelina benghalensis)",
             "Lamber_Quarter_plant(Chenopodium )": "lamb's quarters (Chenopodium)",
             "Lavhala_(Cyperus_Rotundus)": "nut grass (Cyperus rotundus)",
             "Little_Mallow(Malva parviflora)": "little mallow (Malva parviflora)",
             "Moti_dudhi(Euphorbia_geneculata_L)": "wild poinsettia (Euphorbia geniculata)",
             "Obscure_morning _glory(Ipomoea obscura)": "obscure morning glory (Ipomoea obscura)",
             "Punarnava _(Boerhaavia diffusa)": "red spiderling (Boerhavia diffusa)",
             "Sicklepod_(Senna obtusifolia)": "sicklepod (Senna obtusifolia)"}
RICE_WEEDS = {"Alternanthera philoxeroide": "alligator weed (Alternanthera philoxeroides)",
              "Centella asiatica": "Asiatic pennywort (Centella asiatica)",
              "Commelina benghalensis": "Benghal dayflower (Commelina benghalensis)",
              "Cyperus ochraceus": "pale flatsedge (Cyperus ochraceus)",
              "Fimbristylis littoralis": "grasslike fimbry (Fimbristylis littoralis)",
              "Ipomoea aquatic": "water spinach (Ipomoea aquatica)",
              "Marsilea minuta": "dwarf water clover (Marsilea minuta)",
              "Panicum repens": "torpedo grass (Panicum repens)",
              "Paspalum scrobiculatum": "kodo millet grass (Paspalum scrobiculatum)",
              "Pteris vittata": "Chinese brake fern (Pteris vittata)",
              "Synedrella nodiflora": "nodeweed (Synedrella nodiflora)"}
# (repository, folder, label column, names, where it grows, place, credit)
WEED_SETS = [
    ("DeepWeeds_classification", "data/", "species", DEEPWEEDS, "in the rangelands of northern Australia",
     "Queensland, Australia", "DeepWeeds (Olsen et al., 2019), CC BY 4.0, https://github.com/AlexOlsen/DeepWeeds"),
    ("MH_Weed16_weed_variety_classification", "data/", "label", MH_WEED16, "on a farm in India", "India",
     "MH-Weed16: An Indian Multiclass Annotated Weed Dataset, Mendeley Data d3n3mgjjbv, CC BY 4.0"),
    ("rice_field_weed_classification", "data/", "label", RICE_WEEDS, "in a rice field in Bangladesh",
     "Bangladesh", "A comprehensive dataset of rice field weed detection from Bangladesh, Mendeley Data mt72bmxz73, "
                   "CC BY 4.0"),
]


def build_agml_weeds(limit):
    """The weeds pack: an equal share of each set in WEED_SETS, split evenly between its weeds: "What weed is
    this?"."""
    out = []
    per_set = limit // len(WEED_SETS) + 1
    for repo, config, column, names, grows, place, credit in WEED_SETS:
        quota = per_set // len(names) + 1
        try:
            got = agml_read(repo, config, quota, list(names), repo, label_column=column,
                            most_groups=max(4, per_set // 20 + 3))
        except Exception as e:  # noqa: BLE001 - one set failing does not stop the pack
            say(f"  {repo}: not read ({str(e)[:100]})")
            continue
        for label, pictures in got.items():
            for data in pictures:
                answer = f"This is {names[label]}, a weed growing {grows}."
                out.append((f"weed-{repo[:20]}-{len(out)}.jpg", data,
                            {"question": ASK_WEED, "answer": answer, "credit": credit + f" (Project-AgML copy, "
                             f"https://huggingface.co/datasets/{AGML}{repo})", **where(place)}))
        say(f"  {repo}: {sum(len(p) for p in got.values())} pictures")
    random.Random(502).shuffle(out)
    return out[:limit]


# (repository, folder, question, {label: answer}, place, credit)
HARVEST_SETS = [
    ("banana_bunch_maturity_classification", "data/", "Is this banana bunch ready to harvest?",
     {"Cut": "Yes: this bunch of bananas is ready to be cut.",
      "Keep": "No: this bunch of bananas should be left on the plant to grow a little longer."},
     "Madeira, Portugal", "Banana Bunch Harvesting Dataset, Mendeley Data kjrsb7ztr9, CC BY 4.0"),
    ("dragonfruit_maturity_classification", "raw/", "Is this dragon fruit ripe?",
     {"Mature Dragon Fruit": "Yes: this dragon fruit is ripe.",
      "Immature Dragon Fruit": "No: this dragon fruit is not ripe yet."},
     "", "Dragon Fruit Maturity Detection and Quality Grading Dataset, Mendeley Data 2jpzbx8tm6, CC BY 4.0"),
]


def build_agml_harvest(limit):
    """The harvest pack: banana bunches (ready to cut or not) and dragon fruit (ripe or not), half each."""
    out = []
    for repo, config, question, answers, place, credit in HARVEST_SETS:
        quota = limit // (len(HARVEST_SETS) * len(answers)) + 1
        got = agml_read(repo, config, quota, list(answers), repo, most_groups=max(4, quota // 10 + 3))
        for label, pictures in got.items():
            out += [(f"harvest-{repo[:20]}-{len(out) + i}.jpg", data,
                     {"question": question, "answer": answers[label], "credit": credit + f" (Project-AgML copy, "
                      f"https://huggingface.co/datasets/{AGML}{repo})", **where(place)})
                    for i, data in enumerate(pictures)]
        say(f"  {repo}: {sum(len(p) for p in got.values())} pictures")
    random.Random(503).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- Global Wheat Head Dataset 2021

GWHD = "https://zenodo.org/records/5092309/files/gwhd_2021.zip?download=1"
GWHD_CREDIT = "Global Wheat Head Dataset 2021 (David et al.), Zenodo 5092309, CC BY 4.0"
GWHD_COUNTRIES = {"UK": "the UK", "USA": "the USA"}


def gwhd_stage(stage):
    """A growth stage of the dataset's metadata as words after "at" or "in" ("Filling - Ripening" -> "between grain
    filling and ripening"; "Filling" -> "at the grain-filling stage"); "" when none is given."""
    words = {"filling": "grain filling", "ripening": "ripening", "flowering": "flowering",
             "post-flowering": "flowering", "heading": "heading"}
    low = stage.strip().lower()
    if not low:
        return ""
    if low == "post-flowering":
        return "just after flowering"
    parts = [words.get(p.strip(), p.strip()) for p in low.split(" - ") if p.strip()]
    if len(parts) == 2:
        return f"between {parts[0]} and {parts[1]}"
    return f"at the {parts[0].replace(' ', '-')} stage"


def build_gwhd_wheat(limit):
    """The wheat pack: GWHD 2021 photos (1024 pixels square, from above) picked evenly from its 47 sessions, with
    the growth stage and country of each session and the number of wheat ears people outlined in the photo."""
    z = remote_zip(GWHD)
    meta = {}
    for r in csv.DictReader(io.StringIO(z.read("gwhd_2021/metadata_dataset.csv").decode("utf-8", "replace")),
                            delimiter=";"):
        meta[r["name"].strip()] = (r["country"].strip(), r["development_stage"].strip())
    sessions = {}
    for part in ("train", "val", "test"):
        for r in csv.DictReader(io.StringIO(z.read(f"gwhd_2021/competition_{part}.csv").decode())):
            boxes = r["BoxesString"].strip()
            count = 0 if boxes in ("", "no_box") else len(boxes.split(";"))
            sessions.setdefault(r["domain"], []).append((r["image_name"], count))
    rng, items = random.Random(504), []
    per = limit // max(1, len(sessions)) + 1
    for domain, images in sorted(sessions.items()):
        rng.shuffle(images)
        country, stage = meta.get(domain, ("", ""))
        for name, count in images[:per]:
            data = smaller(z.read(f"gwhd_2021/images/{name}"))
            if not data:
                continue
            stage_words = gwhd_stage(stage)
            ears = ("No ears of wheat can be seen." if count == 0 else
                    f"About {count} ear{'s' if count != 1 else ''} of wheat can be seen.")
            answer = "Wheat, seen from straight above in a field" + (f", {stage_words}" if stage_words else "") \
                + f". {ears}"
            place = country_named(country) or country
            rows = [{"question": ASK_CROP, "answer": answer, "credit": f"{GWHD_CREDIT}, session {domain}",
                     **where(place)}]
            if place:
                rows.append(place_row(rows[0], place))
            items.append((f"gwhd-{name[:24]}.jpg", data, rows))
    rng.shuffle(items)
    say(f"GWHD: {len(items[:limit])} wheat photos from {len(sessions)} sessions")
    return with_twins(items[:limit])


# ----------------------------------------------------------------- poultry droppings (Tanzania)

POULTRY = "https://zenodo.org/records/4628934/files/{}.zip?download=1"
POULTRY_CLASSES = {"healthy": "No: these look like normal, healthy chicken droppings.",
                   "cocci": "Yes: they show signs of coccidiosis, a parasite disease of the gut.",
                   "salmo": "Yes: they show signs of salmonella infection.",
                   "ncd": "Yes: they show signs of Newcastle disease, a virus disease of birds."}
POULTRY_CREDIT = ("Machine Learning Dataset for Poultry Diseases Diagnostics (Machuve et al.), Zenodo 4628934, "
                  "CC BY 4.0")


def build_poultry_droppings(limit):
    """The poultry pack: an equal share of each class (each class is its own zip, 0.4 to 3 GB, read piece by
    piece): "Do these chicken droppings show signs of disease?"."""
    out, quota = [], limit // len(POULTRY_CLASSES) + 1
    for cls, answer in POULTRY_CLASSES.items():
        try:
            z = remote_zip(POULTRY.format(cls))
        except Exception as e:  # noqa: BLE001 - the other classes are kept
            say(f"  poultry {cls}: not read ({str(e)[:100]})")
            continue
        names = [n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))]
        random.Random(cls).shuffle(names)
        for n in names[:quota]:
            data = smaller(z.read(n))
            if data:
                out.append((f"poultry-{cls}-{len(out)}.jpg", data,
                            {"question": "Do these chicken droppings show signs of disease?", "answer": answer,
                             "credit": POULTRY_CREDIT, **where("Tanzania")}))
    random.Random(505).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- iNaturalist cultivated crops

# (scientific name, the crop as said after "This is", True for fruit trees and plants that may be shown fruiting)
INAT_CROPS = [("Triticum aestivum", "wheat", False), ("Oryza sativa", "rice", False),
              ("Zea mays", "maize (corn)", False), ("Hordeum vulgare", "barley", False), ("Avena sativa", "oats", False),
              ("Sorghum bicolor", "sorghum", False), ("Manihot esculenta", "cassava", False),
              ("Solanum tuberosum", "potato", False), ("Ipomoea batatas", "sweet potato", False),
              ("Glycine max", "soybean", False), ("Arachis hypogaea", "groundnut (peanut)", False),
              ("Gossypium hirsutum", "cotton", False), ("Saccharum officinarum", "sugarcane", False),
              ("Helianthus annuus", "a sunflower crop", False), ("Brassica napus", "rapeseed (canola)", False),
              ("Coffea arabica", "a coffee plant", True), ("Theobroma cacao", "a cacao tree", True),
              ("Camellia sinensis", "a tea bush", False), ("Musa", "a banana plant", True),
              ("Elaeis guineensis", "an oil palm", True), ("Malus domestica", "an apple tree", True),
              ("Citrus sinensis", "an orange tree", True), ("Mangifera indica", "a mango tree", True),
              ("Olea europaea", "an olive tree", True), ("Vitis vinifera", "a grapevine", True),
              ("Cocos nucifera", "a coconut palm", True), ("Phoenix dactylifera", "a date palm", True),
              ("Prunus avium", "a cherry tree", True), ("Pyrus communis", "a pear tree", True),
              ("Solanum lycopersicum", "a tomato plant", True), ("Capsicum annuum", "a pepper (capsicum) plant", True),
              ("Cucurbita pepo", "a squash (courgette) plant", True), ("Brassica oleracea", "cabbage", False),
              ("Allium cepa", "onion", False), ("Phaseolus vulgaris", "a bean plant", False),
              ("Cicer arietinum", "chickpea", False), ("Medicago sativa", "alfalfa (lucerne)", False),
              ("Ananas comosus", "a pineapple plant", True), ("Carica papaya", "a papaya tree", True),
              ("Fragaria × ananassa", "a strawberry plant", True)]
INAT_FRUITING = {"term_id": 12, "term_value_id": 14}          # iNaturalist's "Plant Phenology: Fruiting" annotation


def inat_row(o, crop, fruit, fruiting):
    """(picture address, row) of an iNaturalist observation of a cultivated crop, or None."""
    from build_packs import inat_place
    photo = next((ph for ph in o.get("photos") or [] if (ph.get("license_code") or "") in ("cc0", "cc-by")), None)
    if not photo:
        return None
    latin = (o.get("taxon") or {}).get("name") or ""
    answer = f"This is {crop} ({latin})" + (", with fruit" if fruit and fruiting else "") + ", grown as a crop."
    login = (o.get("user") or {}).get("login", "an iNaturalist user")
    credit = (f"Photo by {login} on iNaturalist, {photo['license_code'].upper()}, "
              f"https://www.inaturalist.org/observations/{o['id']}")
    return photo["url"].replace("/square.", "/large."), {"question": ASK_CROP, "answer": answer, "credit": credit,
                                                          **inat_place(o)}


def build_inat_crops(limit):
    """The crops pack: for each crop in INAT_CROPS, observations marked cultivated whose photo is CC0 or CC BY and
    whose name at least two people agreed on; for fruit trees, those the observer marked as fruiting first."""
    s, items = session(), []
    per_crop = limit // len(INAT_CROPS) + 1
    for latin, crop, fruit in INAT_CROPS:
        found = 0
        for fruiting in ((True, False) if fruit else (False,)):
            params = {"taxon_name": latin, "captive": "true", "photo_license": "cc0,cc-by", "per_page": 100,
                      "identified": "true", "order_by": "votes", "photos": "true"}
            if fruiting:
                params.update(INAT_FRUITING)
            data = get_json(s, "https://api.inaturalist.org/v1/observations", params) or {}
            time.sleep(1.1)                    # iNaturalist asks for at most about one request a second
            for o in data.get("results") or []:
                if found >= per_crop or (o.get("num_identification_agreements") or 0) < 1:
                    continue
                got = inat_row(o, crop, fruit, fruiting)
                if got and not any(i[0] == f"inat-crop-{o['id']}.jpg" for i in items):
                    rows = [got[1]] + ([place_row(got[1], got[1]["place"])] if got[1].get("place") else [])
                    items.append((f"inat-crop-{o['id']}.jpg", got[0], rows))
                    found += 1
        say(f"  iNaturalist {crop}: {found}")
    random.Random(506).shuffle(items)
    return with_twins(fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.3)[:limit])


# ----------------------------------------------------------------- litter: TrashNet and TACO

TRASHNET = "https://huggingface.co/datasets/garythung/trashnet/resolve/main/dataset-original.zip"
TRASHNET_ANSWERS = {
    "cardboard": f"It is cardboard. It goes in the recycling for paper and cardboard. {LOCAL_RULES}",
    "paper": f"It is paper. It goes in the recycling for paper and cardboard. {LOCAL_RULES}",
    "glass": f"It is a glass bottle or jar. It goes in the glass recycling (a bottle bank). {LOCAL_RULES}",
    "metal": f"It is a metal can or tin. It goes in the recycling for cans and metal packaging. {LOCAL_RULES}",
    "plastic": f"It is plastic packaging. It goes in the recycling for plastic packaging. {LOCAL_RULES}",
    "trash": f"It is general rubbish that cannot be recycled, so it goes in the general waste bin. {LOCAL_RULES}",
}


def build_trashnet(limit):
    """The TrashNet pack: its original photos (3.6 GB zip on Hugging Face, read piece by piece), an equal share of
    each of its six categories."""
    z = remote_zip(TRASHNET)
    groups = {}
    for n in z.namelist():
        parts = n.split("/")
        if len(parts) >= 2 and parts[-2] in TRASHNET_ANSWERS and n.lower().endswith(".jpg") and "__MACOSX" not in n:
            groups.setdefault(parts[-2], []).append(n)
    out, quota = [], limit // len(TRASHNET_ANSWERS) + 1
    for cls, names in sorted(groups.items()):
        random.Random(cls).shuffle(names)
        for n in names[:quota]:
            data = smaller(z.read(n))
            if data:
                out.append((f"trashnet-{cls}-{len(out)}.jpg", data,
                            {"question": ASK_BIN, "answer": TRASHNET_ANSWERS[cls],
                             "credit": "TrashNet (Gary Thung and Mindy Yang, 2017), MIT licence, "
                                       "https://github.com/garythung/trashnet"}))
    random.Random(507).shuffle(out)
    return out[:limit]


TACO_ANNOTATIONS = "https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json"
TACO_CREDIT = ("TACO: Trash Annotations in Context (Pedro F. Proenca and Pedro Simoes, 2020), CC BY 4.0, "
               "https://doi.org/10.5281/zenodo.3587843")
# TACO category -> (the words for one piece, its recycling stream or None when the bin is not clear from the name).
TACO_WORDS = {
    "Aluminium foil": ("a piece of aluminium foil", "metal"), "Battery": ("a battery", "battery"),
    "Aluminium blister pack": ("an aluminium blister pack", None), "Carded blister pack": ("a blister pack", None),
    "Other plastic bottle": ("a plastic bottle", "plastic"), "Clear plastic bottle": ("a clear plastic bottle",
                                                                                       "plastic"),
    "Glass bottle": ("a glass bottle", "glass"), "Plastic bottle cap": ("a plastic bottle cap", "plastic"),
    "Metal bottle cap": ("a metal bottle cap", "metal"), "Broken glass": ("some broken glass", None),
    "Food Can": ("a food tin", "metal"), "Aerosol": ("an aerosol can", None), "Drink can": ("a drink can", "metal"),
    "Toilet tube": ("a toilet-roll tube", "paper"), "Other carton": ("a carton", None),
    "Egg carton": ("an egg box", "paper"), "Drink carton": ("a drink carton", None),
    "Corrugated carton": ("a piece of corrugated cardboard", "paper"), "Meal carton": ("a takeaway carton", None),
    "Pizza box": ("a pizza box", None), "Paper cup": ("a paper cup", None),
    "Disposable plastic cup": ("a disposable plastic cup", None), "Foam cup": ("a foam cup", "general"),
    "Glass cup": ("a drinking glass", None), "Other plastic cup": ("a plastic cup", None),
    "Food waste": ("some food waste", None), "Glass jar": ("a glass jar", "glass"),
    "Plastic lid": ("a plastic lid", "plastic"), "Metal lid": ("a metal lid", "metal"),
    "Other plastic": ("a piece of plastic", None), "Magazine paper": ("a magazine page", "paper"),
    "Tissues": ("a tissue", "general"), "Wrapping paper": ("a piece of wrapping paper", None),
    "Normal paper": ("a piece of paper", "paper"), "Paper bag": ("a paper bag", "paper"),
    "Plastified paper bag": ("a plastic-coated paper bag", None), "Plastic film": ("a piece of plastic film", None),
    "Six pack rings": ("a six-pack ring", None), "Garbage bag": ("a rubbish bag", None),
    "Other plastic wrapper": ("a plastic wrapper", None), "Single-use carrier bag": ("a plastic carrier bag", None),
    "Polypropylene bag": ("a woven plastic bag", None), "Crisp packet": ("a crisp packet", "general"),
    "Spread tub": ("a spread tub", "plastic"), "Tupperware": ("a plastic food box", None),
    "Disposable food container": ("a disposable food container", None),
    "Foam food container": ("a foam food container", "general"),
    "Other plastic container": ("a plastic container", None), "Plastic glooves": ("a plastic glove", "general"),
    "Plastic utensils": ("a plastic fork or spoon", "general"), "Pop tab": ("a can ring-pull", "metal"),
    "Rope & strings": ("a piece of rope or string", "general"), "Scrap metal": ("a piece of scrap metal", None),
    "Shoe": ("a shoe", None), "Squeezable tube": ("a squeezable tube", None), "Plastic straw": ("a plastic straw",
                                                                                                "general"),
    "Paper straw": ("a paper straw", None), "Styrofoam piece": ("a piece of polystyrene foam", "general"),
    "Unlabeled litter": ("a piece of litter", None), "Cigarette": ("a cigarette end", "general"),
}
TACO_BINS = {
    "plastic": "It goes in the recycling for plastic packaging.",
    "metal": "It goes in the recycling for cans and metal packaging.",
    "glass": "It goes in the glass recycling (a bottle bank).",
    "paper": "It goes in the recycling for paper and cardboard.",
    "general": "It cannot be recycled, so it goes in the general waste bin.",
    "battery": "Batteries go to a battery collection point, never in the household bins.",
}
TACO_SCENES = {"Pavement": "on a pavement", "Sand, Dirt, Pebbles": "on sand, earth or pebbles",
               "Vegetation": "among plants", "Water": "in or by water", "Indoor, Man-made": "indoors",
               "Trash": "among other rubbish"}


def taco_count(words, n):
    """ "a drink can" or "3 drink cans": a piece's words with how many there are."""
    if n == 1:
        return words
    rest = re.sub(r"^(a|an|some)\s+", "", words)
    if rest.startswith("piece of "):
        return f"{n} pieces of {rest[9:]}"
    head, _, tail = rest.partition(" of ")
    plural = head + ("es" if head.endswith(("s", "x", "ch", "sh")) else "s")
    return f"{n} {plural}" + (f" of {tail}" if tail else "")


def build_taco_litter(limit):
    """The TACO pack: every photo's pieces of litter counted by kind ("What litter is in this picture?", with where
    it lies when the photo's scene was labelled), and, when every piece shares one recycling stream, the bin
    question. Photos from TACO's own server."""
    s = session()
    a = s.get(TACO_ANNOTATIONS, timeout=120).json()
    cats = {c["id"]: c["name"] for c in a["categories"]}
    scenes = {c["id"]: c["name"] for c in a.get("scene_categories") or []}
    pieces, scene_of = {}, {}
    for ann in a["annotations"]:
        pieces.setdefault(ann["image_id"], []).append(cats[ann["category_id"]])
    for sa in a.get("scene_annotations") or []:
        names = [scenes.get(i) for i in sa.get("background_ids") or [] if scenes.get(i) in TACO_SCENES]
        if names:
            scene_of[sa["image_id"]] = TACO_SCENES[names[0]]
    items = []
    for im in a["images"]:
        found = pieces.get(im["id"])
        if not found or not im.get("flickr_url"):
            continue
        counts = {}
        for name in found:
            counts[name] = counts.get(name, 0) + 1
        words = [taco_count(TACO_WORDS.get(n, (n.lower(), None))[0], c) for n, c in
                 sorted(counts.items(), key=lambda x: -x[1])]
        where_words = f", {scene_of[im['id']]}" if im["id"] in scene_of else ""
        rows = [{"question": ASK_LITTER, "answer": sentence(f"There is litter here{where_words}: {listed(words)}"),
                 "credit": TACO_CREDIT}]
        streams = {TACO_WORDS.get(n, ("", None))[1] for n in counts}
        if len(streams) == 1 and None not in streams:
            stream = streams.pop()
            rows.append({"question": ASK_BIN, "answer": sentence(listed(words)) + f" {TACO_BINS[stream]} "
                                                                                 f"{LOCAL_RULES}",
                         "credit": TACO_CREDIT})
        items.append((f"taco-{im['id']}.jpg", im["flickr_url"], rows))
    random.Random(508).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=4, pause=0.2)[:limit]
    say(f"TACO: {len(fetched)} photos, {sum(1 for _, _, r in fetched if len(r) > 1)} with the bin question")
    return with_twins(fetched)


# ----------------------------------------------------------------- street litter and floating plastic

PLITTER = "https://zenodo.org/records/8288500/files/{}?download=1"
PLITTER_CREDIT = ("pLitterStreet: Street Level Plastic Litter Detection Dataset (Mandhati, Deshapriya, Mendis and "
                  "Gunasekara), Zenodo 8288500, CC BY 4.0")
# The dataset's folders (the start of each file name) and where they were filmed; "" when the record does not say.
PLITTER_PLACES = {"Rangsit_2021": "Rangsit, Pathum Thani, Thailand", "Taladthai_2021": "Pathum Thani, Thailand",
                  "Chiangrai_2021": "Chiang Rai, Thailand", "Ubon_2022": "Ubon Ratchathani, Thailand",
                  "Hanwella_2022": "Hanwella, Sri Lanka", "Mawanella_2022": "Mawanella, Sri Lanka",
                  "Mekong_2020": ""}
# The 10 classes: the words for one, and for several.
PLITTER_WORDS = {"litter": ("a piece of litter", "pieces of litter"), "pile": ("a pile of rubbish", "piles of rubbish"),
                 "face mask": ("a face mask", "face masks"), "plastic bag": ("a plastic bag", "plastic bags"),
                 "bottle": ("a bottle", "bottles"), "cup": ("a cup", "cups"), "rope": ("a piece of rope",
                                                                                     "pieces of rope"),
                 "sachet": ("a sachet (a small plastic packet)", "sachets (small plastic packets)"),
                 "straw": ("a drinking straw", "drinking straws")}


def plitter_answer(counts):
    """The answer for one street photo from {class name: count}: the litter, most first, then any rubbish bin."""
    words = [PLITTER_WORDS[n][0] if c == 1 else f"{c} {PLITTER_WORDS[n][1]}"
             for n, c in sorted(counts.items(), key=lambda x: -x[1]) if n in PLITTER_WORDS]
    bins = counts.get("trash bin", 0)
    answer = f"There is litter beside the street: {listed(words)}." if words else \
        "No litter is marked beside the street here."
    if bins:
        answer += " There is also a rubbish bin." if bins == 1 else f" There are also {bins} rubbish bins."
    return answer


def build_plitter_street(limit):
    """The street-litter pack: pLitterStreet photos from cameras on vehicles driving through towns and villages in
    Thailand, Sri Lanka and the Mekong region, every piece of litter boxed by people (its 10-class annotations), an
    equal share from each place (the photos are frames of drives, so one place would otherwise fill the pack). The
    pictures are read out of the 13.7 GB images.zip by HTTP ranges. "What litter is in this picture?" and, where
    known, "Where was this photo taken?"."""
    import zipfile
    s = session()
    notes = zipfile.ZipFile(io.BytesIO(s.get(PLITTER.format("annotations.zip"), timeout=300).content))
    data = json.loads(notes.read("annotations/10_class_splits/annotations_all.json"))
    cats = {c["id"]: c["name"] for c in data["categories"]}
    counts = {}
    for a in data["annotations"]:
        one = counts.setdefault(a["image_id"], {})
        one[cats[a["category_id"]]] = one.get(cats[a["category_id"]], 0) + 1
    z = remote_zip(PLITTER.format("images.zip"))
    inside = {n.rsplit("/", 1)[-1]: n for n in z.namelist() if n.lower().endswith((".jpg", ".jpeg", ".png"))}
    groups = {}
    for im in data["images"]:
        folder = (im.get("path") or "").split("/")[2] if (im.get("path") or "").count("/") >= 3 else ""
        if im["id"] in counts and im["file_name"] in inside and folder in PLITTER_PLACES:
            groups.setdefault(folder, []).append(im)
    out, rng = [], random.Random(515)
    quota = limit // max(1, len(groups)) + 1
    for folder, images in sorted(groups.items()):
        rng.shuffle(images)
        place = PLITTER_PLACES[folder]
        for im in images[:quota]:
            picture = smaller(z.read(inside[im["file_name"]]))
            if not picture:
                continue
            rows = [{"question": ASK_LITTER, "answer": plitter_answer(counts[im["id"]]), "credit": PLITTER_CREDIT,
                     **where(place)}]
            if place:
                rows.append(place_row(rows[0], place))
            out.append((f"plitter-{re.sub(r'[^\w.-]', '_', im['file_name'].rsplit('.', 1)[0])[:80]}.jpg", picture,
                        rows))
        say(f"  pLitterStreet {folder}: {min(quota, len(images))} photos")
    rng.shuffle(out)
    return with_twins(out[:limit])


PLP2019 = "https://zenodo.org/records/3752719/files/PLP2019_dataset.rar?download=1"
PLP2021 = "https://zenodo.org/records/7085112/files/{}.zip?download=1"
PLP2021_DATES = ("20210611", "20210621", "20210626", "20210701", "20210706", "20210711", "20210716", "20210721",
                 "20210726", "20210731", "20210805", "20210810", "20210815", "20210820", "20210825", "20210830",
                 "20210904", "20210909", "20210914", "20210919", "20210924", "20211004")
PLP_ASK = "What is floating on the water here?"
PLP_ANSWER = ("Test targets floating on the sea near the coast: rafts made of plastic and other materials, laid out "
              "by scientists to check whether satellites can spot floating plastic litter.")


def plp_2019_photos():
    """[(file name, JPEG bytes)] of PLP2019's drone photos: its 68 MB RAR archive is downloaded and the photos taken
    out with bsdtar or 7-Zip (Python cannot read RAR itself); [] when neither program is there. The 2018 "photo"
    is a 250-megapixel orthophoto map and is left out by smaller()."""
    import shutil
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        archive = f"{folder}/plp2019.rar"
        with open(archive, "wb") as f:
            f.write(session().get(PLP2019, timeout=600).content)
        if shutil.which("bsdtar"):
            command = ["bsdtar", "-xf", archive, "-C", folder]
        elif shutil.which("7z"):
            command = ["7z", "x", "-y", f"-o{folder}", archive]
        else:
            say("  PLP2019: neither bsdtar nor 7z is installed, so its RAR archive cannot be opened")
            return []
        subprocess.run(command, check=True, capture_output=True)
        out = []
        for root, _, files in os.walk(folder):
            for name in sorted(files):
                if "UAV_photos" in root and name.lower().endswith((".jpg", ".jpeg")):
                    with open(f"{root}/{name}", "rb") as f:
                        picture = smaller(f.read())
                    if picture:
                        out.append((name, picture))
        return out


def build_plp_floating_targets(limit):
    """The floating-plastic pack: drone photos of the Plastic Litter Projects of the University of the Aegean's
    Marine Remote Sensing Group off Lesvos, Greece: PLP2019 (Zenodo 3752719, CC BY 4.0) and PLP2021 (Zenodo 7085112,
    CC BY 4.0; one photo of the targets inside each date's 5-10 GB zip, read by HTTP ranges). "What is floating on
    the water here?"."""
    out = []
    try:
        for name, picture in plp_2019_photos():
            out.append((f"plp2019-{name.rsplit('.', 1)[0]}.jpg", picture,
                        [{"question": PLP_ASK, "answer": PLP_ANSWER,
                          "credit": "PLP2019 dataset (Konstantinos Topouzelis, Marine Remote Sensing Group, University "
                                    "of the Aegean), Zenodo 3752719, CC BY 4.0"}]))
    except Exception as e:  # noqa: BLE001 - the 2021 photos are still taken
        say(f"  PLP2019: not read ({str(e)[:100]})")
    say(f"  PLP2019: {len(out)} drone photos")
    place = "Gulf of Gera, Lesvos, Greece"
    for date in PLP2021_DATES:
        if len(out) >= limit:
            break
        try:
            z = remote_zip(PLP2021.format(date))
            names = [n for n in z.namelist() if re.search(r"_(UAS_RGB|field)[^/]*\.jpe?g$", n, re.I)]
            for n in names[:1]:
                picture = smaller(z.read(n))
                if picture:
                    rows = [{"question": PLP_ASK, "answer": PLP_ANSWER, **where(place),
                             "credit": f"Plastic Litter Project 2021 dataset (Dimitris Papageorgiou and Konstantinos "
                                       f"Topouzelis), Zenodo 7085112, CC BY 4.0, acquisition {date}"}]
                    out.append((f"plp2021-{date}.jpg", picture, rows + [place_row(rows[0], place)]))
        except Exception as e:  # noqa: BLE001 - the next date
            say(f"  PLP2021 {date}: not read ({str(e)[:100]})")
    say(f"  PLP 2019 and 2021: {len(out)} photos in all")
    return with_twins(out[:limit])


# ----------------------------------------------------------------- weather and clouds

CCSN = "https://dataverse.harvard.edu/api/access/datafile/3569338"
CCSN_CREDIT = "Cirrus Cumulus Stratus Nimbus (CCSN) Database (Pu Liu), Harvard Dataverse doi:10.7910/DVN/CADDPD, CC0"
CCSN_ANSWERS = {
    "Ci": "These are cirrus clouds: thin, wispy streaks high in the sky.",
    "Cs": "This is cirrostratus: a thin, high veil of cloud that can make a halo round the sun or moon.",
    "Cc": "This is cirrocumulus: small, high puffs of cloud in rows or ripples.",
    "Ac": "This is altocumulus: middle-level clouds in white or grey patches, rolls or rows.",
    "As": "This is altostratus: a grey or bluish middle-level sheet of cloud through which the sun looks dim.",
    "Cu": "These are cumulus clouds: puffy, white heaps with flat bases, usually in fair weather.",
    "Cb": "This is cumulonimbus: a towering storm cloud that can bring thunder, lightning and heavy rain.",
    "Ns": "This is nimbostratus: a thick, dark grey layer of cloud that brings steady rain or snow.",
    "Sc": "This is stratocumulus: low, lumpy grey and white clouds in patches or a layer.",
    "St": "This is stratus: a flat, grey layer of low cloud, like high fog.",
    "Ct": "These are contrails: straight white trails of cloud left by aircraft high in the sky.",
}


def build_ccsn_clouds(limit):
    """The clouds pack: CCSN's 2,543 sky photos (a 98 MB zip), an equal share of each of the 11 kinds: "What kind
    of cloud is this?"."""
    z = remote_zip(CCSN)
    groups = {}
    for n in z.namelist():
        parts = n.split("/")
        if "__MACOSX" not in n and len(parts) == 3 and parts[1] in CCSN_ANSWERS and n.lower().endswith(".jpg"):
            groups.setdefault(parts[1], []).append(n)
    out, quota = [], limit // len(CCSN_ANSWERS) + 1
    for cls, names in sorted(groups.items()):
        random.Random(cls).shuffle(names)
        for n in names[:quota]:
            data = smaller(z.read(n))
            if data:
                out.append((f"ccsn-{cls}-{len(out)}.jpg", data, {"question": "What kind of cloud is this?",
                                                                  "answer": CCSN_ANSWERS[cls], "credit": CCSN_CREDIT}))
    random.Random(509).shuffle(out)
    return out[:limit]


MWD = "4drtyfjtfy"
MWD_ANSWERS = {"cloudy": "It is cloudy: the sky is covered with cloud.", "rain": "It is raining.",
               "shine": "It is sunny, with the sun shining.",
               "sunrise": "The sun is low on the horizon: it is sunrise or sunset."}
MWD_CREDIT = "Multi-class Weather Dataset for Image Classification (Gbeminiyi Ajayi), Mendeley Data 4drtyfjtfy, CC BY 4.0"


def build_weather_images(limit):
    """The weather pack: the Multi-class Weather Dataset's four kinds (about 1,100 photos), equal shares: "What is
    the weather like in this picture?"."""
    from build_packs import mendeley_zip
    z = mendeley_zip(MWD)
    groups = {}
    for n in z.namelist():
        m = re.match(r"(?:.*/)?(cloudy|rain|shine|sunrise)\d+\.(jpe?g|png)$", n, re.I)
        if m and "__MACOSX" not in n:
            groups.setdefault(m.group(1).lower(), []).append(n)
    out, quota = [], limit // len(MWD_ANSWERS) + 1
    for cls, names in sorted(groups.items()):
        random.Random(cls).shuffle(names)
        for n in names[:quota]:
            data = smaller(z.read(n))
            if data:
                out.append((f"weather-{cls}-{len(out)}.jpg", data,
                            {"question": "What is the weather like in this picture?", "answer": MWD_ANSWERS[cls],
                             "credit": MWD_CREDIT}))
    random.Random(510).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- EuroSAT

EUROSAT = "https://huggingface.co/datasets/torchgeo/eurosat/resolve/main/EuroSAT.zip"
EUROSAT_CREDIT = ("EuroSAT (Helber, Bischke, Dengel and Borth, 2019), MIT licence, https://github.com/phelber/EuroSAT; "
                  "contains modified Copernicus Sentinel data")
EUROSAT_ANSWERS = {
    "AnnualCrop": "fields of crops that are sown and harvested every year",
    "Forest": "forest", "HerbaceousVegetation": "rough grassland and other low wild plants",
    "Highway": "a motorway or main road crossing the land", "Industrial": "an industrial area of large buildings",
    "Pasture": "pasture: grassland for grazing animals", "PermanentCrop": "orchards, vineyards or other long-lived crops",
    "Residential": "a residential area of houses and streets", "River": "a river winding through the land",
    "SeaLake": "open water: the sea or a lake",
}


def build_eurosat(limit):
    """The EuroSAT pack: a few hundred of its 27,000 small RGB satellite views (64 by 64 pixels, each about 640
    metres across), equal shares of the ten kinds."""
    z = remote_zip(EUROSAT)
    groups = {}
    for n in z.namelist():
        parts = n.split("/")
        if len(parts) >= 2 and parts[-2] in EUROSAT_ANSWERS and n.lower().endswith((".jpg", ".png", ".tif")):
            groups.setdefault(parts[-2], []).append(n)
    out, quota = [], limit // len(EUROSAT_ANSWERS) + 1
    for cls, names in sorted(groups.items()):
        random.Random(cls).shuffle(names)
        for n in names[:quota]:
            data = smaller(z.read(n))
            if data:
                out.append((f"eurosat-{cls}-{len(out)}.jpg", data,
                            {"question": "What does this satellite picture show?",
                             "answer": f"A satellite view, from straight above, of {EUROSAT_ANSWERS[cls]}. It is "
                                       "small and blurry: about 640 metres across, somewhere in Europe.",
                             "credit": EUROSAT_CREDIT}))
    random.Random(511).shuffle(out)
    return out[:limit]


# ----------------------------------------------------------------- Wikimedia Commons categories

# Each category: (question, answer, whether one level of its subcategories is used too, content). The question is
# ASK_MACHINE, ASK_CROP or ASK_SHOWN; content is "" or "graphic".
COMMONS_LAND = {
    # agriculture and farming
    "Tractors": (ASK_MACHINE, "A tractor: a farm vehicle with big rear wheels that pulls and powers farm tools.",
                 True, ""),
    "Combine harvesters": (ASK_MACHINE, "A combine harvester: a big farm machine that cuts a grain crop and "
                                        "separates the grain from the straw as it drives.", True, ""),
    "Ploughs": (ASK_MACHINE, "A plough: a farm tool with blades that turn over the soil before sowing.", True, ""),
    "Ploughing": (ASK_SHOWN, "A field being ploughed: the soil is being turned over before sowing.", True, ""),
    "Seed drills": (ASK_MACHINE, "A seed drill: a farm machine that sows seeds in rows.", False, ""),
    "Balers": (ASK_MACHINE, "A baler: a farm machine that presses hay or straw into bales.", False, ""),
    "Agricultural aircraft": (ASK_MACHINE, "An agricultural aircraft, used to spray or spread crops from the air.",
                              False, ""),
    "Threshing": (ASK_SHOWN, "Threshing: separating the grain from the stalks after harvest.", True, ""),
    "Harvesting": (ASK_SHOWN, "A harvest: a crop being gathered in.", False, ""),
    "Haymaking": (ASK_SHOWN, "Haymaking: grass being cut, dried and gathered as hay.", False, ""),
    "Hay bales": (ASK_SHOWN, "Bales of hay or straw in a field.", False, ""),
    "Round bales": (ASK_SHOWN, "Round bales of hay or straw.", False, ""),
    "Paddy fields": (ASK_CROP, "Rice, growing in flooded paddy fields.", False, ""),
    "Wheat fields": (ASK_CROP, "Wheat, growing in a field.", False, ""),
    "Maize fields": (ASK_CROP, "Maize (corn), growing in a field.", False, ""),
    "Rapeseed fields": (ASK_CROP, "Rapeseed (canola), a field of bright yellow flowers.", False, ""),
    "Sunflower fields": (ASK_CROP, "Sunflowers, growing in a field.", False, ""),
    "Cotton fields": (ASK_CROP, "Cotton, growing in a field.", False, ""),
    "Tea plantations": (ASK_CROP, "Tea: rows of tea bushes on a plantation.", False, ""),
    "Coffee plantations": (ASK_CROP, "Coffee, growing on a plantation.", False, ""),
    "Oil palm plantations": (ASK_CROP, "Oil palms, growing on a plantation.", False, ""),
    "Vineyards": (ASK_CROP, "Grapevines, growing in rows in a vineyard.", False, ""),
    "Orchards": (ASK_SHOWN, "An orchard: fruit trees planted in rows.", False, ""),
    "Apples on trees": (ASK_CROP, "Apples, growing on the tree.", False, ""),
    "Greenhouses": (ASK_SHOWN, "A greenhouse: a building of glass or clear plastic where plants are grown.", False,
                    ""),
    "Polytunnels": (ASK_SHOWN, "Polytunnels: long tunnels of plastic sheeting over hoops, for growing crops.",
                    False, ""),
    "Center pivot irrigation": (ASK_SHOWN, "Centre-pivot irrigation: a long sprinkler arm on wheels that turns round "
                                           "a field, watering a circle.", False, ""),
    "Drip irrigation": (ASK_SHOWN, "Drip irrigation: thin pipes that drip water at the roots of the plants.", False,
                        ""),
    "Irrigation canals": (ASK_SHOWN, "An irrigation canal, bringing water to the fields.", False, ""),
    "Agricultural terraces": (ASK_SHOWN, "Terraced fields: steps cut into a hillside for farming.", False, ""),
    "Grain silos": (ASK_SHOWN, "Grain silos: tall containers for storing grain.", False, ""),
    "Grain elevators": (ASK_SHOWN, "A grain elevator: a tall building where grain is stored and loaded.", False, ""),
    "Scarecrows": (ASK_SHOWN, "A scarecrow: a figure dressed in old clothes, put in a field to scare birds away.",
                   False, ""),
    "Grazing cattle": (ASK_SHOWN, "Cattle grazing in a field.", False, ""),
    "Cattle feedlots": (ASK_SHOWN, "A cattle feedlot: many cattle kept in pens and fed for meat.", False, ""),
    "Milking machines": (ASK_MACHINE, "A milking machine, which milks cows through cups on the udder.", False, ""),
    "Sheep shearing": (ASK_SHOWN, "Sheep shearing: a sheep's wool being clipped off.", False, ""),
    "Poultry farming": (ASK_SHOWN, "Poultry farming: chickens or other birds kept for eggs or meat.", True, ""),
    "Battery cages": (ASK_SHOWN, "Battery cages: rows of small wire cages where laying hens are kept.", False, ""),
    "Pig farms": (ASK_SHOWN, "A pig farm.", False, ""),
    "Fish farming": (ASK_SHOWN, "A fish farm, where fish are raised in ponds, tanks or net pens.", True, ""),
    "Aquaculture": (ASK_SHOWN, "Aquaculture: fish, shellfish or seaweed being farmed in water.", False, ""),
    "Beekeeping": (ASK_SHOWN, "Beekeeping: beehives, or a beekeeper looking after the bees.", False, ""),
    "Farmers' markets": (ASK_SHOWN, "A farmers' market, where farmers sell their produce at stalls.", False, ""),
    "Livestock markets": (ASK_SHOWN, "A livestock market, where farm animals are bought and sold.", True, ""),
    # the environment
    "Deforestation": (ASK_SHOWN, "Deforestation: forest being cut down or cleared.", False, ""),
    "Clearcutting": (ASK_SHOWN, "A clear-cut: a stretch of forest where every tree has been felled.", False, ""),
    "Slash-and-burn": (ASK_SHOWN, "Slash-and-burn: forest or scrub being cut and burned to clear land for farming.",
                       False, ""),
    "Wildfires": (ASK_SHOWN, "A wildfire, or the smoke or burnt land it leaves.", False, ""),
    "Floods": (ASK_SHOWN, "A flood: water covering land, roads or buildings that are normally dry.", False, ""),
    "Drought": (ASK_SHOWN, "Drought: dry, cracked ground or a dried-up river, lake or field after a long time "
                           "without rain.", False, ""),
    "Soil erosion": (ASK_SHOWN, "Soil erosion: ground washed or blown away, leaving gullies or bare earth.", False,
                     ""),
    "Litter": (ASK_SHOWN, "Litter: rubbish dropped and left lying about.", False, ""),
    "Plastic pollution": (ASK_SHOWN, "Plastic pollution: plastic rubbish left in nature.", False, ""),
    "Marine debris": (ASK_SHOWN, "Marine debris: rubbish washed up on a beach or floating in the sea.", False, ""),
    "Landfills": (ASK_SHOWN, "A landfill: a site where rubbish is dumped and buried.", False, ""),
    "Waste sorting": (ASK_SHOWN, "Waste sorting: rubbish separated into bins or piles for recycling.", False, ""),
    "Recycling centres": (ASK_SHOWN, "A recycling centre, with containers for different kinds of waste.", False, ""),
    "Air pollution": (ASK_SHOWN, "Air pollution: smoke, smog or fumes in the air.", False, ""),
    "Smog": (ASK_SHOWN, "Smog: a haze of polluted air over a city.", False, ""),
    "Oil spills": (ASK_SHOWN, "An oil spill: oil spread over water or a shore.", False, ""),
    "Coral reefs": (ASK_SHOWN, "A coral reef under the sea.", False, ""),
    "Coral bleaching": (ASK_SHOWN, "Bleached coral: coral that has turned white because the water became too warm.",
                        False, ""),
    "Glaciers": (ASK_SHOWN, "A glacier: a huge, slowly moving river of ice.", False, ""),
    "Mangroves": (ASK_SHOWN, "Mangroves: trees growing in salty water on a tropical coast, on tangled roots.", False,
                  ""),
    "Wetlands": (ASK_SHOWN, "A wetland: marshy land with shallow water and reeds.", False, ""),
    # industry and manufacturing
    "Factories": (ASK_SHOWN, "A factory.", False, ""),
    "Assembly lines": (ASK_SHOWN, "An assembly line, where products are put together step by step.", False, ""),
    "Industrial robots": (ASK_MACHINE, "An industrial robot: a machine arm that welds, lifts or assembles in a "
                                       "factory.", False, ""),
    "Warehouses": (ASK_SHOWN, "A warehouse, where goods are stored on racks.", False, ""),
    "Forklifts": (ASK_MACHINE, "A forklift truck, which lifts and moves loads on two forks.", False, ""),
    "Welding": (ASK_SHOWN, "Welding: metal being joined with great heat, often with bright sparks.", False, ""),
    "Steel mills": (ASK_SHOWN, "A steelworks, where iron is made into steel.", False, ""),
    "Foundries": (ASK_SHOWN, "A foundry, where molten metal is poured into moulds.", False, ""),
    "Sawmills": (ASK_SHOWN, "A sawmill, where logs are cut into timber.", False, ""),
    "Textile mills": (ASK_SHOWN, "A textile mill, where yarn or cloth is made.", True, ""),
    "Workshops": (ASK_SHOWN, "A workshop, with a workbench and tools.", False, ""),
    "Lathes": (ASK_MACHINE, "A lathe: a machine that spins wood or metal while a cutting tool shapes it.", False, ""),
    "Container ships": (ASK_SHOWN, "A container ship, loaded with stacks of shipping containers.", False, ""),
    "Container terminals": (ASK_SHOWN, "A container port, where cranes load shipping containers on and off ships.",
                            False, ""),
    "Intermodal containers": (ASK_SHOWN, "Shipping containers: big steel boxes for carrying goods by ship, train "
                                         "or lorry.", False, ""),
    "Container cranes": (ASK_MACHINE, "A container crane, which lifts shipping containers on and off ships.", False,
                         ""),
    "Shipyards": (ASK_SHOWN, "A shipyard, where ships are built or repaired.", False, ""),
    "Industrial accidents": (ASK_SHOWN, "The scene of an industrial accident.", True, "graphic"),
    # mining and energy
    "Coal mines": (ASK_SHOWN, "A coal mine.", False, ""),
    "Underground mining": (ASK_SHOWN, "Underground mining: a tunnel deep in a mine.", False, ""),
    "Quarries": (ASK_SHOWN, "A quarry, where stone is cut or dug from the ground.", False, ""),
    "Mining equipment": (ASK_MACHINE, "Mining equipment: a machine used to dig or carry rock in a mine.", False, ""),
    "Haul trucks": (ASK_MACHINE, "A haul truck: a giant dump truck that carries rock in a mine.", True, ""),
    "Bucket-wheel excavators": (ASK_MACHINE, "A bucket-wheel excavator: a huge mining machine with a turning wheel "
                                             "of buckets that digs coal or earth.", False, ""),
    "Oil platforms": (ASK_SHOWN, "An oil platform: a structure at sea for drilling for oil or gas.", False, ""),
    "Oil refineries": (ASK_SHOWN, "An oil refinery, with towers, tanks and pipes, where crude oil is made into "
                                  "fuels.", False, ""),
    "Oil wells": (ASK_SHOWN, "An oil well, often with a nodding pump on top.", False, ""),
    "Gas flares": (ASK_SHOWN, "A gas flare: a flame burning off unwanted gas at an oil or gas site.", False, ""),
    "Pipelines": (ASK_SHOWN, "A pipeline, carrying oil, gas or water over long distances.", False, ""),
    "Coal-fired power stations": (ASK_SHOWN, "A coal-fired power station, with tall chimneys.", False, ""),
    "Nuclear power plants": (ASK_SHOWN, "A nuclear power station.", False, ""),
    "Cooling towers": (ASK_SHOWN, "Cooling towers: huge, wide chimneys of a power station, often letting out "
                                  "steam.", False, ""),
    "Hydroelectric power stations": (ASK_SHOWN, "A hydroelectric power station, which makes electricity from "
                                                "flowing water.", False, ""),
    "Geothermal power stations": (ASK_SHOWN, "A geothermal power station, which uses heat from under the ground.",
                                  False, ""),
    "Wind turbines": (ASK_MACHINE, "A wind turbine: a tall tower with turning blades that makes electricity from the "
                                   "wind.", False, ""),
    "Wind farms": (ASK_SHOWN, "A wind farm: many wind turbines together.", False, ""),
    "Offshore wind farms": (ASK_SHOWN, "An offshore wind farm: wind turbines standing in the sea.", False, ""),
    "Solar panels": (ASK_SHOWN, "Solar panels, which make electricity from sunlight.", False, ""),
    "Photovoltaic power stations": (ASK_SHOWN, "A solar farm: rows and rows of solar panels.", False, ""),
    "Electrical substations": (ASK_SHOWN, "An electrical substation, with transformers and switchgear behind a "
                                          "fence.", False, ""),
    "Electricity pylons": (ASK_SHOWN, "Electricity pylons: tall steel towers carrying power lines.", False, ""),
    # construction and infrastructure
    "Construction sites": (ASK_SHOWN, "A building site.", False, ""),
    "Tower cranes": (ASK_MACHINE, "A tower crane: a tall crane with a long horizontal arm, used on building sites.",
                     False, ""),
    "Mobile cranes": (ASK_MACHINE, "A mobile crane: a crane on a lorry or tracks.", False, ""),
    "Excavators": (ASK_MACHINE, "An excavator (a digger): a machine with a long arm and a bucket that digs.", False,
                   ""),
    "Backhoe loaders": (ASK_MACHINE, "A backhoe loader: a digger with a bucket at the front and a digging arm at the "
                                     "back.", False, ""),
    "Bulldozers": (ASK_MACHINE, "A bulldozer: a tracked machine with a wide blade at the front that pushes earth.",
                   False, ""),
    "Dump trucks": (ASK_MACHINE, "A dump truck, which tips its load out of the back.", False, ""),
    "Concrete mixer trucks": (ASK_MACHINE, "A concrete mixer lorry, with a turning drum on the back.", False, ""),
    "Road rollers": (ASK_MACHINE, "A road roller: a heavy machine with smooth drums that flattens a new road "
                                  "surface.", False, ""),
    "Tunnel boring machines": (ASK_MACHINE, "A tunnel boring machine: a giant machine with a turning cutting wheel "
                                            "that digs tunnels.", False, ""),
    "Scaffolding": (ASK_SHOWN, "Scaffolding: a frame of poles and planks put up round a building for workers.",
                    False, ""),
    "Bridges under construction": (ASK_SHOWN, "A bridge being built.", False, ""),
    "Suspension bridges": (ASK_SHOWN, "A suspension bridge: its deck hangs from cables between tall towers.", False,
                           ""),
    "Viaducts": (ASK_SHOWN, "A viaduct: a long bridge of many arches or spans carrying a road or railway.", False,
                 ""),
    "Dams": (ASK_SHOWN, "A dam: a wall built across a river to hold back water.", False, ""),
    "Canal locks": (ASK_SHOWN, "A canal lock, with gates that raise or lower boats.", False, ""),
    "Tunnels": (ASK_SHOWN, "A tunnel.", False, ""),
    "Level crossings": (ASK_SHOWN, "A level crossing, where a road crosses a railway.", False, ""),
    "Water treatment plants": (ASK_SHOWN, "A water treatment works, where water is cleaned for drinking.", False,
                               ""),
    "Wastewater treatment plants": (ASK_SHOWN, "A sewage works, where waste water is cleaned.", False, ""),
}
# Subcategories and file names that are not photos of the thing (drawings, models, toys, logos ...).
COMMONS_NOT_IT = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|svg|sculptures?|statues?|"
                            r"videos?|audio|maps?|diagrams?|stamps?|coins?|advertis\w*|posters?|cartoons?|comics?|"
                            r"toys?|models?|scale models?|lego|miniatures?|in literature|manufacturers?|companies|"
                            r"museums?|collections?|logos?|charts?|patents?|schematics?|games?|simulat\w*|"
                            r"nude|naked)\b", re.I)


ENGLISH_WORDS = re.compile(r"\b(the|a|an|of|and|in|with|on|at|from|near|view|is|are|by|for|to)\b", re.I)


def looks_english(text):
    """True for text in English: Latin letters only (no other script) and at least one common English word."""
    return not re.search(r"[^\x00-\u024f\u2010-\u2027]", text) and bool(ENGLISH_WORDS.search(text))


def commons_land_rows(category, question, answer, content, title, text, credit):
    """The rows for one Commons file: the category's question and, where the file has a caption or description of 6
    words or more, "Describe this picture."; then "Where was this photo taken?" from the camera's coordinates. [] when
    the file's words name nudity."""
    if NUDE.search(f"{title} {text}"):
        return []
    place = commons_place(title).get("place", "")
    rows = [{"question": question, "answer": answer, "credit": credit}]
    caption = tidy(text) if text else ""
    if caption and usable(caption) and looks_english(caption):
        rows.append({"question": NARRATE, "answer": caption, "credit": credit})
    if place:
        rows.append(place_row(rows[0], place))
    rows = [dict(marked(r, title, text), **where(place)) for r in rows]
    if content:
        rows = [dict(r, content=content) for r in rows]
    return rows


def build_commons_land_industry(limit):
    """The Commons land and industry pack: for each category of COMMONS_LAND its files (and those of its
    subcategories where it says so, leaving out drawings, models and logos), the free ones (CC0, public domain, CC
    BY), each with the category's question and its caption. The categories share the limit; a file is used once."""
    s, items, seen = session(), [], set()
    per_category = max(4, limit // len(COMMONS_LAND) * 2)
    for category, (question, answer, deeper, content) in COMMONS_LAND.items():
        try:
            titles = commons_members(s, category, "file")
            if deeper:
                for sub in commons_members(s, category, "subcat")[:30]:
                    sub = sub.split(":", 1)[-1]
                    if not COMMONS_NOT_IT.search(sub):
                        titles += commons_members(s, sub, "file")
        except RuntimeError as e:                 # Commons kept refusing: keep what was found
            say(f"  Commons {category}: stopped ({e})")
            break
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not COMMONS_NOT_IT.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_entries(s, titles[:per_category * 3]):
            rows = commons_land_rows(category, question, answer, content, title, text, credit)
            if not rows or found >= per_category:
                continue
            seen.add(title)
            name = re.sub(r"[^\w.-]+", "_", title.split(":", 1)[-1].rsplit(".", 1)[0])[:80]
            items.append((f"commons-land-{name}.jpg", standard_thumb(url), rows))
            found += 1
        say(f"Commons {category}: {found} free pictures ({len(titles)} files)")
    random.Random(512).shuffle(items)
    fetched = fetch_all(items[:int(limit * 1.1) + 2], workers=2, pause=0.5)
    return with_twins(fetched[:limit])


# ----------------------------------------------------------------- Library of Congress: HAER

HAER = "collections/historic-american-buildings-landscapes-and-engineering-records/"
HAER_TERMS = ("dam", "bridge", "mine", "mill", "factory", "power plant", "canal", "railroad", "tunnel", "steel",
              "furnace", "smelter", "oil", "refinery", "kiln", "quarry", "shipyard", "lock", "aqueduct",
              "irrigation", "grain elevator", "water tower", "pumping station", "foundry", "cannery", "brewery",
              "lumber", "ranch", "barn", "dairy", "sugar", "cotton gin", "wharf", "pier", "trestle", "viaduct",
              "roundhouse", "substation", "hydroelectric", "spillway", "levee", "airport", "highway")
# Captions that are copies of older pictures or drawings, not the survey's own photographs.
HAER_NOT_OWN = re.compile(r"\b(photocopy|photocopied|copy of|reproduction|drawing|drawn|plan|plans|elevation|"
                          r"section|sketch|map|postcard|lithograph|engraving|rendering|blueprint|diagram|"
                          r"courtesy|original in|source:)\b", re.I)
HAER_CREDIT = ("Historic American Engineering Record, Library of Congress, Prints and Photographs Division, no known "
               "restrictions on images made by the U.S. Government")


def haer_case(text):
    """Capital-letter caption text in sentence case: each sentence starts with a capital letter, the rest small."""
    text = text.lower()
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), text)


def haer_caption(text, title):
    """A HAER photo caption as an answer: "1. DAM, VIEW EAST, VIEW UPSTREAM - Gallipolis Locks & Dam, ..." becomes
    "Dam, view east, view upstream. Gallipolis Locks & Dam, ..."; "" when it is not the survey's own photograph.
    A photographer's note in front ("Historic American Buildings Survey January 1937 DETAIL OF ...") is dropped."""
    text = clean(text)
    text = re.sub(r"^\s*\d+[A-Z]?\.\s*", "", text)
    if HAER_NOT_OWN.search(text):
        return ""
    what, _, site = text.partition(" - ")
    what = what.strip(" .")
    capitals = re.search(r"\b[A-Z]{2,}[A-Z0-9 ,.;:'()&/\-]{8,}$", what)
    if capitals and capitals.start() > 0:
        what = capitals.group(0)
    if sum(c.isupper() for c in what) > sum(c.islower() for c in what):
        what = haer_case(what)
    site = site.strip(" .") or clean(title)
    return tidy(f"{what}. {site}") if what else ""


US_STATE_CODES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
                  "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
                  "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana",
                  "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
                  "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
                  "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
                  "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
                  "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
                  "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
                  "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin",
                  "WY": "Wyoming", "PR": "Puerto Rico", "GU": "Guam", "VI": "US Virgin Islands"}


def haer_place(record, item):
    """Where a HAER item is, from its place heading ("West Virginia -- Mason County -- Gallipolis") as "Gallipolis,
    West Virginia, USA", or else from the state code that ends its title ("..., Benson, Cache County, UT"); "" when
    neither is there."""
    for rec in (item, record):
        for p in (rec.get("place") or []):
            parts = [x.strip(" .") for x in clean((p or {}).get("title")).split("--") if x.strip(" .")]
            if parts and parts[0] in US_STATE_CODES.values():
                town = [x for x in parts[1:] if not re.search(r"\b(county|parish|borough)$", x, re.I)]
                return place_name(*(town[-1:] + [parts[0], "USA"]))
    parts = [x.strip(" .") for x in clean(record.get("title")).split(",")]
    if len(parts) >= 3 and parts[-1] in US_STATE_CODES:
        town = parts[-3] if re.search(r"\b(county|parish|borough)$", parts[-2], re.I) else parts[-2]
        return place_name(town, US_STATE_CODES[parts[-1]], "USA")
    return ""


def haer_items(s, term, want, rng):
    """[(name, picture address, rows)] for HAER items found by a search word: up to two photos from each item, each
    with its caption as "Describe this picture." and the item's place."""
    from documentary_packs import loc_free
    data = get_json(s, LOC + HAER, {"fo": "json", "c": 100, "q": term, "sp": rng.randint(1, 3),
                                    "fa": "online-format:image", "at": "results"}, pause=15)
    results = (data or {}).get("results") or []
    rng.shuffle(results)
    items = []
    for record in results:
        if len(items) >= want:
            break
        url = record.get("url") or record.get("id") or ""
        if not loc_free(record) or "/item/" not in url:
            continue
        time.sleep(1.5)                                  # the Library asks for about one request a second
        item = get_json(s, re.sub(r"^(https?:)?//", "https://", url), {"fo": "json"}, pause=15) or {}
        place = haer_place(record, item.get("item") or {})
        taken = 0
        photos = []
        for resource in item.get("resources") or []:
            for files in resource.get("files") or []:
                pics = [f for f in files if f.get("mimetype") in ("image/jpeg", "image/jpg") and f.get("width")]
                cap = next((f.get("title") for f in files if f.get("use") == "caption"), "")
                if pics and cap:
                    best = max((f for f in pics if f["width"] <= 2100), key=lambda f: f["width"], default=None)
                    if best:
                        photos.append((best["url"], cap))
        rng.shuffle(photos)
        for picture, cap in photos:
            answer = haer_caption(cap, record.get("title"))
            if not usable(answer) or taken >= 2:
                continue
            taken += 1
            credit = f"{clean(cap)[:150]}, {HAER_CREDIT}, {re.sub(r'^(https?:)?//', 'https://', url)}"
            stem = re.sub(r"\W", "", picture.rsplit("/", 1)[-1].rsplit(".", 1)[0])
            items.append((f"haer-{stem}.jpg", picture, picture_rows(answer, credit, place)))
    return items


def build_loc_haer(limit):
    """The HAER pack: for each search word in HAER_TERMS, items of the HABS/HAER/HALS collection, two photos each
    at most, the survey's caption and the place."""
    s, rng, items = session(), random.Random(513), []
    per_term = limit // len(HAER_TERMS) + 2
    for term in HAER_TERMS:
        found = haer_items(s, term, int(per_term * 1.3), rng)
        items += [i for i in found if i[0] not in {x[0] for x in items}]
        say(f"  HAER '{term}': {len(found)} photos")
        if len(items) >= limit * 1.3:
            break
    return finish("loc_haer", items, limit, workers=3, pause=0.5)


# ----------------------------------------------------------------- USDA Agricultural Research Service

ARS = "https://www.ars.usda.gov"
ARS_CATEGORIES = ("photo-natural-resources", "photos-field-research", "photos-plants", "photos-insects",
                  "photos-people", "photos-lab-research", "photos-food", "photos-digital-assets")
# A caption that describes the photo, not a story about the research ("There was a time, a half century ago ...").
ARS_DESCRIBES = re.compile(r"^(?!(there|it|this|they|in|when|for|if|once|today) )(an? |the |\w+ (is|are|was|were) |\w+ \w+ (is|are) |close-up|aerial|view|scientists? |"
                           r"technicians? |researchers? |entomologists? |geneticists? |agronomists? |\w+ing |"
                           r"[A-Z][a-z]+ [A-Z][a-z]+ (is|are|was|uses?|checks?|examines?|inspects?|holds?|measures?)\b)",
                           re.I)
ARS_NOT_FREE = re.compile(r"\b(copyright(ed)?|courtesy of|used with permission|all rights reserved)\b", re.I)


def ars_page(s, path):
    """(caption, photographer, picture address) of an ARS image page, or None (also when it says it is not free)."""
    try:
        page = s.get(ARS + path, timeout=60).text
    except Exception:  # noqa: BLE001 - left out
        return None
    m = re.search(r"Image Number\s*([A-Z]?\d[\w-]*)\s*</?\w[^>]*>(.*?)(?:640 pixels|Please visit)", page, re.S | re.I)
    if not m:
        return None
    text = clean(re.sub(r"<[^>]+>", " ", m.group(2)))
    who = ""
    w = re.search(r"\s*Photo by ([^.]+)\.?\s*$", text)
    if w:
        who, text = w.group(1).strip(), text[:w.start()].strip()
    if ARS_NOT_FREE.search(text):
        return None
    stem = path.rstrip("/").rsplit("/", 1)[-1]
    pictures = re.findall(r'/ARSUserFiles/oc/graphics/photos/[^"\']*?/' + re.escape(stem) + r'\.jpg', page)
    best = next((p for p in pictures if "/300dpi/" in p), pictures[0] if pictures else "")
    return (text, who, ARS + best) if best else None


def build_usda_ars(limit):
    """The ARS pack: every photo page linked from the gallery's category pages (a few hundred), ARS's caption as
    "Describe this picture."."""
    s, items, paths = session(), [], []
    for category in ARS_CATEGORIES:
        try:
            page = s.get(f"{ARS}/oc/images/photos/{category}/", timeout=60).text
        except Exception:  # noqa: BLE001 - next category
            continue
        paths += re.findall(r'href="(/oc/images/photos/(?:[a-z]{3}\d{2}/)?[a-z]?\d[\w-]*)"', page, re.I)
        time.sleep(1)
    paths = list(dict.fromkeys(paths))
    random.Random(514).shuffle(paths)
    for path in paths:
        if len(items) >= limit * 1.2:
            break
        time.sleep(0.5)
        info = ars_page(s, path)
        if not info:
            continue
        answer = tidy(first_sentences(info[0], 45))
        if not usable(answer) or not ARS_DESCRIBES.search(answer):
            continue
        credit = ("USDA Agricultural Research Service" + (f", photo by {info[1]}" if info[1] else "")
                  + f", public domain, {ARS}{path}")
        rows = [marked(r, answer) for r in picture_rows(answer, credit)]
        items.append((f"ars-{path.rsplit('/', 1)[-1]}.jpg", info[2], rows))
    say(f"USDA ARS: {len(items)} usable photos of {len(paths)} pages")
    return finish("usda_ars", items, limit, workers=3, pause=0.3)


# ----------------------------------------------------------------- the packs

LAND_PACKS = {
    "agml_plant_health": (build_agml_plant_health, "Crop leaves and plants, healthy or diseased: datasets each CC BY "
                                                   "4.0 on Mendeley Data or Zenodo (iBean: MIT licence), read from the "
                                                   "Project-AgML copies on Hugging Face "
                                                   "(https://huggingface.co/Project-AgML); each picture's dataset is "
                                                   "credited below."),
    "agml_weeds": (build_agml_weeds, "DeepWeeds (CC BY 4.0, https://github.com/AlexOlsen/DeepWeeds), MH-Weed16 "
                                     "(Mendeley Data d3n3mgjjbv, CC BY 4.0) and rice-field weeds of Bangladesh "
                                     "(Mendeley Data mt72bmxz73, CC BY 4.0), from the Project-AgML copies."),
    "agml_harvest": (build_agml_harvest, "Banana Bunch Harvesting Dataset (Mendeley Data kjrsb7ztr9) and Dragon Fruit "
                                         "Maturity dataset (Mendeley Data 2jpzbx8tm6), both CC BY 4.0, from the "
                                         "Project-AgML copies."),
    "gwhd_wheat": (build_gwhd_wheat, "Global Wheat Head Dataset 2021 (David et al.), CC BY 4.0, "
                                     "https://doi.org/10.5281/zenodo.5092309"),
    "poultry_droppings": (build_poultry_droppings, "Machine Learning Dataset for Poultry Diseases Diagnostics "
                                                   "(Machuve et al.), CC BY 4.0, "
                                                   "https://doi.org/10.5281/zenodo.4628934"),
    "inat_crops": (build_inat_crops, "iNaturalist observations of cultivated crops: photos CC0 or CC BY, each with its "
                                     "photographer below. https://www.inaturalist.org"),
    "trashnet": (build_trashnet, "TrashNet (Gary Thung and Mindy Yang), MIT licence, "
                                 "https://github.com/garythung/trashnet"),
    "taco_litter": (build_taco_litter, "TACO: Trash Annotations in Context (Proenca and Simoes), CC BY 4.0, "
                                       "https://doi.org/10.5281/zenodo.3587843 ; http://tacodataset.org"),
    "ccsn_clouds": (build_ccsn_clouds, "Cirrus Cumulus Stratus Nimbus (CCSN) Database (Pu Liu), CC0 1.0, "
                                       "https://doi.org/10.7910/DVN/CADDPD"),
    "weather_images": (build_weather_images, "Multi-class Weather Dataset for Image Classification (Gbeminiyi Ajayi), "
                                             "CC BY 4.0, https://data.mendeley.com/datasets/4drtyfjtfy/1"),
    "eurosat": (build_eurosat, "EuroSAT (Helber et al.), MIT licence, https://github.com/phelber/EuroSAT ; contains "
                               "modified Copernicus Sentinel data."),
    "commons_land_industry": (build_commons_land_industry, "Wikimedia Commons: captions CC0; pictures CC0, public "
                                                           "domain or CC BY, each with its author and file page "
                                                           "below. https://commons.wikimedia.org"),
    "loc_haer": (build_loc_haer, "Historic American Engineering Record, Library of Congress, Prints and Photographs "
                                 "Division, https://www.loc.gov/collections/historic-american-buildings-landscapes-"
                                 "and-engineering-records/ : 'No known restrictions on images made by the U.S. "
                                 "Government' (https://www.loc.gov/rr/print/res/114_habs.html). Captions from the "
                                 "survey records."),
    "plitter_street": (build_plitter_street, "pLitterStreet: Street Level Plastic Litter Detection Dataset (Mandhati, "
                                             "Deshapriya, Mendis and Gunasekara), CC BY 4.0, "
                                             "https://doi.org/10.5281/zenodo.8288500"),
    "plp_floating_targets": (build_plp_floating_targets, "PLP2019 dataset (Topouzelis), CC BY 4.0, "
                                                         "https://doi.org/10.5281/zenodo.3752719 ; Plastic Litter "
                                                         "Project 2021 dataset (Papageorgiou and Topouzelis), CC BY "
                                                         "4.0, https://doi.org/10.5281/zenodo.7085112 ; Marine Remote "
                                                         "Sensing Group, University of the Aegean."),
    "usda_ars": (build_usda_ars, "USDA Agricultural Research Service image gallery, "
                                 "https://www.ars.usda.gov/oc/images/image-gallery/ : public domain "
                                 "(https://www.ars.usda.gov/oc/images/copyright/); credit: USDA ARS."),
}

# How many pictures a full build takes from each collection.
LAND_LIMITS = {
    "agml_plant_health": 6000,        # about 350 from each of 17 datasets (they hold 1,000 to 18,000 each)
    "agml_weeds": 3000,               # DeepWeeds 8,400 weed photos, MH-Weed16 19,000, rice-field weeds 3,600
    "agml_harvest": 1200,             # banana bunches 2,685, dragon fruit about 1,000 raw photos
    "gwhd_wheat": 2000,               # of 6,500 photos in 47 sessions
    "poultry_droppings": 2000,        # of about 6,800 photos in four classes (Newcastle disease: about 370)
    "inat_crops": 2400,               # about 60 a crop (one page of results each, two for fruit trees)
    "trashnet": 1500,                 # of 2,527 photos
    "taco_litter": 1500,              # all of TACO's 1,500 photos
    "ccsn_clouds": 2500,              # all of CCSN's 2,543 photos
    "weather_images": 1100,           # all of the 1,125 photos
    "eurosat": 600,                   # of 27,000, kept few: 64 by 64 pixels
    "commons_land_industry": 4000,    # the free files of about 125 categories
    "loc_haer": 3000,                 # two photos from each of about 1,500 items
    "plitter_street": 2500,           # of about 13,000 annotated photos, an equal share from each of 7 places
    "plp_floating_targets": 30,       # all there are: about 5 drone photos of 2019 and one a date in 2021 (22 dates)
    "usda_ars": 300,                  # the whole gallery (a few hundred photo pages)
}


def main(argv=None):
    """Run one builder with a small limit and print its rows (a quick check, writes nothing)."""
    import argparse
    parser = argparse.ArgumentParser(description="Try one land and industry pack builder.")
    parser.add_argument("key", choices=sorted(LAND_PACKS))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--show", type=int, default=0, help="print only this many rows (0: all)")
    args = parser.parse_args(argv)
    entries = LAND_PACKS[args.key][0](args.limit)
    for name, data, row in entries[:args.show or None]:
        say(json.dumps({"file": name, "bytes": len(data) if data else None, **row}, ensure_ascii=False))
    say(f"{len(entries)} entries, {count_pictures(entries)} pictures, "
        f"{sum(1 for _, _, r in entries if r.get('child'))} rows marked child, "
        f"{sum(1 for _, _, r in entries if r.get('content'))} marked graphic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
