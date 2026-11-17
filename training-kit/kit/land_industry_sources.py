"""Land and industry picture collections for the Picture Model Training Kit (agriculture and farming, the
environment, industry, mining, energy, construction and transport infrastructure) that cannot be ready-made packs
because of their licence: share-alike, non-commercial, or terms that forbid passing the data on. The open ones (crop
diseases, weeds, wheat, poultry droppings, iNaturalist crops, TrashNet, TACO litter, clouds, weather, EuroSAT, the
Commons CC0/PD/CC BY files, the Historic American Engineering Record and the USDA ARS gallery) are packs in
packs/land_industry_packs.py.

As in extra_sources.py, nothing here is re-shared by the kit's makers: each collection is downloaded by the kit on the
user's own computer, straight from where its makers publish it (or, where the makers' own copy cannot be fetched by a
program, the copy named), only when the user ticks the matching choice. Every licence was checked at its source in
November 2026.

Groups (Source.group, as in sources.py):
  "share-alike"    CC BY-SA and GFDL: only with the share-alike choice (--with-wikipedia); an add-on trained with them
                   is CC BY-SA.
  "noncommercial"  CC BY-NC, BY-NC-SA and other non-commercial terms: personal use only (--personal-noncommercial).
  "research"       research or academic terms: personal use only (--personal-research with --accept-research-terms).

The collections (LAND_SOURCES):
  share-alike
    commons_land_industry_sa  Wikimedia Commons categories of farming, the environment, industry, mining, energy and
                              construction: files under CC BY-SA or GFDL, with the category's question and the file's
                              caption.
    plant_seedlings_sa        Plant Seedlings Dataset (Aarhus University, CC BY-SA 4.0): seedlings of maize, wheat and
                              sugar beet and of nine common weeds, photographed from above at Flakkebjerg, Denmark.
                              "What crop or weed seedling is this?" The makers' own download link is behind a web form,
                              so the Project-AgML copy on Hugging Face is used.
  noncommercial
    soybean_weeds_nc          Weed Detection in Soybean Crops (dos Santos Ferreira et al., Mendeley Data 3fmjm7ncc6,
                              CC BY-NC 3.0): drone photos of soybean fields in Brazil, cut into tiles of soybean, grass
                              weeds, broadleaf weeds or bare soil.
    weed_growth_stage_nc      Weed Growth Stage Dataset (Southern Illinois University, Zenodo 15808623, CC BY-NC-SA
                              4.0): 16 weeds of American fields photographed every week from 1 to 11 weeks after
                              sowing. "What weed is this, and how old is it?"
    cropandweed_nc            CropAndWeed (AIT Austrian Institute of Technology, 2023; its own non-commercial terms,
                              no redistribution): field photos with every crop and weed plant outlined and named,
                              many with the growth stage. "What crops and weeds are in this picture?"
  research
    agriculture_vision        Agriculture-Vision 2021 (IntelinAir and the Agriculture-Vision Workshop): aerial tiles of
                              US farmland with field problems outlined (weed clusters, standing water, nutrient
                              deficiency, planter skips, storm damage ...). The owner agrees to the workshop's terms
                              and gets the 21 GB archive, then tells the kit where it is: a path or link in the
                              AGRICULTURE_VISION setting, or on the first line of agriculture-vision.txt in the
                              downloads folder, or the archive itself in the downloads folder's agriculture_vision
                              folder. Its terms are narrow (the challenge only; no derivative works): read them first.

Every picture in these collections shows plants, fields, machines or buildings; Commons rows whose words name a child
carry "child": True, and rows that name an injury or a death carry "content": "graphic" (only the share-alike Commons
entry can have them). LAND_PICTURE_MAKING_OK holds the collections of landscapes, plants and machines without people:
all but commons_land_industry_sa (whose photos may show workers and farmers).

Needing sign-up (cannot be downloaded automatically; LAND_SIGN_UP has the links), and looked at and not included
(LAND_NOT_INCLUDED, with the reason of each).

    python kit/land_industry_sources.py weed_growth_stage_nc --cap 8     (a quick check; prints a few rows)
"""

import csv
import io
import os
import random
import re
import tarfile

import sources
from big_sources import even_pick, mendeley_files
from extra_sources import (NUDE, commons_file_name, commons_members, commons_sa_entries, commons_session,
                           per_label, zenodo)
from more_sources import fetch_shared
from personal_sources import CHILD_WORDS, listed, remote_zip, zip_members
from sources import NARRATE, USER_AGENT, Source, clean, have, smaller

ASK_MACHINE = "What machine is this?"
ASK_CROP = "What crop is this?"
ASK_SHOWN = "What is shown in this picture?"
INJURY = re.compile(r"\b(injur\w*|wounded|casualt\w*|dead|deaths?|died|killed|bod(y|ies)|blood\w*|corpses?|"
                    r"victims?|fatal\w*)\b", re.I)


def say(text):
    """Say text through the kit's own say (train.py replaces sources.say after this module is imported)."""
    sources.say(text)


def sentence(text):
    """Text with a capital first letter and a full stop."""
    text = clean(text).strip()
    if not text:
        return ""
    text = text[0].upper() + text[1:]
    return text if text[-1] in ".!?" else text + "."


# ----------------------------------------------------------------- share-alike: Wikimedia Commons

# Each category: (question, answer, whether one level of its subcategories is used too). The same subjects as the
# open commons_land_industry pack, shortened.
COMMONS_LAND_SA = {
    "Tractors": (ASK_MACHINE, "A tractor: a farm vehicle that pulls and powers farm tools.", True),
    "Combine harvesters": (ASK_MACHINE, "A combine harvester, which cuts a grain crop and separates the grain.", True),
    "Ploughing": (ASK_SHOWN, "A field being ploughed.", True),
    "Paddy fields": (ASK_CROP, "Rice, growing in flooded paddy fields.", False),
    "Wheat fields": (ASK_CROP, "Wheat, growing in a field.", False),
    "Maize fields": (ASK_CROP, "Maize (corn), growing in a field.", False),
    "Tea plantations": (ASK_CROP, "Tea: rows of tea bushes on a plantation.", False),
    "Vineyards": (ASK_CROP, "Grapevines, growing in rows in a vineyard.", False),
    "Apples on trees": (ASK_CROP, "Apples, growing on the tree.", False),
    "Greenhouses": (ASK_SHOWN, "A greenhouse, where plants are grown under glass or plastic.", False),
    "Center pivot irrigation": (ASK_SHOWN, "Centre-pivot irrigation: a long sprinkler arm turning round a field.",
                                False),
    "Agricultural terraces": (ASK_SHOWN, "Terraced fields: steps cut into a hillside for farming.", False),
    "Grazing cattle": (ASK_SHOWN, "Cattle grazing in a field.", False),
    "Poultry farming": (ASK_SHOWN, "Poultry farming: chickens kept for eggs or meat.", True),
    "Fish farming": (ASK_SHOWN, "A fish farm.", True),
    "Farmers' markets": (ASK_SHOWN, "A farmers' market.", False),
    "Deforestation": (ASK_SHOWN, "Deforestation: forest being cut down or cleared.", False),
    "Wildfires": (ASK_SHOWN, "A wildfire, or the smoke or burnt land it leaves.", False),
    "Floods": (ASK_SHOWN, "A flood: water covering land that is normally dry.", False),
    "Drought": (ASK_SHOWN, "Drought: dry, cracked ground after a long time without rain.", False),
    "Litter": (ASK_SHOWN, "Litter: rubbish dropped and left lying about.", False),
    "Marine debris": (ASK_SHOWN, "Rubbish washed up on a beach or floating in the sea.", False),
    "Landfills": (ASK_SHOWN, "A landfill, where rubbish is dumped and buried.", False),
    "Oil spills": (ASK_SHOWN, "An oil spill: oil spread over water or a shore.", False),
    "Coral reefs": (ASK_SHOWN, "A coral reef under the sea.", False),
    "Glaciers": (ASK_SHOWN, "A glacier: a huge, slowly moving river of ice.", False),
    "Factories": (ASK_SHOWN, "A factory.", False),
    "Assembly lines": (ASK_SHOWN, "An assembly line.", False),
    "Industrial robots": (ASK_MACHINE, "An industrial robot arm.", False),
    "Warehouses": (ASK_SHOWN, "A warehouse.", False),
    "Forklifts": (ASK_MACHINE, "A forklift truck.", False),
    "Welding": (ASK_SHOWN, "Welding: metal being joined with great heat.", False),
    "Container terminals": (ASK_SHOWN, "A container port.", False),
    "Coal mines": (ASK_SHOWN, "A coal mine.", False),
    "Quarries": (ASK_SHOWN, "A quarry.", False),
    "Mining equipment": (ASK_MACHINE, "Mining equipment.", False),
    "Oil platforms": (ASK_SHOWN, "An oil platform at sea.", False),
    "Oil refineries": (ASK_SHOWN, "An oil refinery.", False),
    "Nuclear power plants": (ASK_SHOWN, "A nuclear power station.", False),
    "Cooling towers": (ASK_SHOWN, "Cooling towers of a power station.", False),
    "Hydroelectric power stations": (ASK_SHOWN, "A hydroelectric power station.", False),
    "Wind turbines": (ASK_MACHINE, "A wind turbine.", False),
    "Solar panels": (ASK_SHOWN, "Solar panels.", False),
    "Electrical substations": (ASK_SHOWN, "An electrical substation.", False),
    "Electricity pylons": (ASK_SHOWN, "Electricity pylons carrying power lines.", False),
    "Pipelines": (ASK_SHOWN, "A pipeline.", False),
    "Construction sites": (ASK_SHOWN, "A building site.", False),
    "Tower cranes": (ASK_MACHINE, "A tower crane.", False),
    "Excavators": (ASK_MACHINE, "An excavator (a digger).", False),
    "Bulldozers": (ASK_MACHINE, "A bulldozer.", False),
    "Bridges under construction": (ASK_SHOWN, "A bridge being built.", False),
    "Dams": (ASK_SHOWN, "A dam across a river.", False),
    "Tunnels": (ASK_SHOWN, "A tunnel.", False),
    "Industrial accidents": (ASK_SHOWN, "The scene of an industrial accident.", True),
}
GRAPHIC_CATEGORIES = {"Industrial accidents"}
ENGLISH_WORDS = re.compile(r"\b(the|a|an|of|and|in|with|on|at|from|near|view|is|are|by|for|to)\b", re.I)
COMMONS_NOT_IT = re.compile(r"\b(art|drawings?|illustrations?|paintings?|logos?|icons?|svg|sculptures?|statues?|"
                            r"videos?|audio|maps?|diagrams?|stamps?|coins?|advertis\w*|posters?|cartoons?|comics?|"
                            r"toys?|models?|lego|miniatures?|in literature|manufacturers?|companies|museums?|"
                            r"collections?|charts?|patents?|games?|nude|naked)\b", re.I)


def prepare_commons_land_industry_sa(source, data_dir, work, cap):
    """Wikimedia Commons land and industry categories (COMMONS_LAND_SA): files under CC BY-SA or GFDL, each with the
    category's question and, where it has one, its caption ("Describe this picture."). The categories share the cap;
    rows whose words name a child are marked "child", those naming an injury or death (and every industrial accident)
    "content": "graphic"."""
    s, items, seen = commons_session(), [], set()
    per_category = per_label(int((cap + source.test) * 0.9), len(COMMONS_LAND_SA))
    for category, (question, answer, deeper) in COMMONS_LAND_SA.items():
        titles = commons_members(s, category, "file")
        if deeper:
            for sub in commons_members(s, category, "subcat")[:30]:
                sub = sub.split(":", 1)[-1]
                if not COMMONS_NOT_IT.search(sub):
                    titles += commons_members(s, sub, "file")
        titles = [t for t in dict.fromkeys(titles) if t not in seen and not COMMONS_NOT_IT.search(t)]
        random.Random(category).shuffle(titles)
        found = 0
        for title, url, credit, text in commons_sa_entries(s, titles[:per_category * 4]):
            if found >= per_category or NUDE.search(f"{title} {text}"):
                continue
            seen.add(title)
            marks = {}
            if CHILD_WORDS.search(f"{title} {text}"):
                marks["child"] = True
            if category in GRAPHIC_CATEGORIES or INJURY.search(f"{title} {text}"):
                marks["content"] = "graphic"
            name = commons_file_name("land-sa", title)
            url = re.sub(r"/\d+px-([^/]+)$", r"/960px-\1", url)      # a width Wikimedia keeps ready
            items.append((name, url, {"question": question, "answer": answer, "split": "", "credit": credit,
                                      **marks}))
            if text and len(text.split()) >= 6 and not re.search(r"[^\x00-\u024f\u2010-\u2027]", text) \
                    and ENGLISH_WORDS.search(text):
                items.append((name, url, {"question": NARRATE, "answer": text, "split": "", "credit": credit,
                                          **marks}))
            found += 1
        say(f"  Commons {category}: {found} photos")
    return fetch_shared(items, os.path.join(data_dir, source.key), workers=2)


# ----------------------------------------------------------------- share-alike: Plant Seedlings (Aarhus)

SEEDLINGS_REPO = "Project-AgML/plant_seedlings_aarhus"
SEEDLINGS = {"black_grass": "black-grass, a grass weed", "charlock": "charlock (wild mustard), a weed",
             "cleavers": "cleavers (goosegrass), a weed", "common_chickweed": "common chickweed, a weed",
             "common_wheat": "wheat, a crop", "fat_hen": "fat hen, a weed", "loose_silkybent": "loose silky-bent, a "
             "grass weed", "maize": "maize, a crop", "scentless_mayweed": "scentless mayweed, a weed",
             "shepherds_purse": "shepherd's purse, a weed", "smallflowered_cranesbill": "small-flowered cranesbill, "
             "a weed", "sugar_beet": "sugar beet, a crop"}


def prepare_plant_seedlings_sa(source, data_dir, work, cap):
    """Plant Seedlings Dataset (Giselsson et al., 2017; CC BY-SA 4.0): single seedlings photographed from above,
    an equal share of the 12 kinds, read from the Project-AgML parquet files (the makers' download link is behind a
    web form): the label column of every row group first, then the pictures of only the rows picked. "What crop or
    weed seedling is this?" """
    import json

    import pyarrow.parquet as pq
    from huggingface_hub import HfApi, HfFileSystem
    fs = HfFileSystem()
    groups, files = {}, {}
    for name in sorted(f for f in HfApi().list_repo_files(SEEDLINGS_REPO, repo_type="dataset")
                       if f.endswith(".parquet")):
        pf = pq.ParquetFile(fs.open(f"datasets/{SEEDLINGS_REPO}/{name}", "rb", block_size=1 << 20))
        files[name] = pf
        meta = json.loads((pf.schema_arrow.metadata or {}).get(b"huggingface", b"{}"))
        names = (((meta.get("info") or {}).get("features") or {}).get("label") or {}).get("names") or []
        for g in range(pf.metadata.num_row_groups):
            for i, v in enumerate(pf.read_row_group(g, columns=["label"]).column(0).to_pylist()):
                label = names[v] if names and isinstance(v, int) and v < len(names) else ""
                if label in SEEDLINGS:
                    groups.setdefault(label, []).append((name, g, i))
    picked = even_pick(groups, cap + source.test, 307)
    label_of = {item: label for label, items in groups.items() for item in items}
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows, by_group = [], {}
    for name, g, i in picked:
        by_group.setdefault((name, g), []).append(i)
    for (name, g), wanted in sorted(by_group.items()):
        images = files[name].read_row_group(g, columns=["image"]).column(0).to_pylist()
        for i in wanted:
            label = label_of[(name, g, i)]
            target = os.path.join(folder, f"seedling-{label}-{os.path.basename(name).split('.')[0]}-{g}-{i}.jpg")
            if have(target) or smaller((images[i] or {}).get("bytes") or b"", target):
                rows.append({"picture": target, "question": "What crop or weed seedling is this?",
                             "answer": f"This is a seedling of {SEEDLINGS[label]}.", "split": "",
                             "credit": "Plant Seedlings Dataset (Aarhus University and University of Southern "
                                       "Denmark), CC BY-SA 4.0, https://vision.eng.au.dk/plant-seedlings-dataset/ "
                                       "(Project-AgML copy)", **sources.place_fields({"place": "Flakkebjerg, Denmark"})})
    say(f"  Plant Seedlings: {len(rows)} pictures of {len(groups)} kinds.")
    return rows


# ----------------------------------------------------------------- non-commercial: soybean field weeds (Brazil)

SOYBEAN_WEEDS = "3fmjm7ncc6"
SOYBEAN_ANSWERS = {"soybean": "Soybean plants, a crop.", "grass": "Grass weeds growing among the crop.",
                   "broadleaf": "Broadleaf weeds growing among the crop.", "soil": "Bare soil, with no plants."}


def prepare_soybean_weeds_nc(source, data_dir, work, cap):
    """Weed Detection in Soybean Crops (dos Santos Ferreira et al., 2017; CC BY-NC 3.0): tiles of drone photos of
    soybean fields in Campo Grande, Brazil, by kind (soybean, grass weeds, broadleaf weeds, soil), an equal share of
    each, read out of the 1.3 GB zip by HTTP ranges. "What is growing here?" """
    url = next(u for u, name, _ in mendeley_files(SOYBEAN_WEEDS, 2) if name.lower().endswith(".zip"))
    z = remote_zip(url)
    groups = {}
    for n in z.namelist():
        parts = n.lower().split("/")
        if len(parts) >= 2 and parts[-2] in SOYBEAN_ANSWERS and parts[-1].endswith((".tif", ".jpg", ".png")):
            groups.setdefault(parts[-2], []).append(n)
    z.close()
    chosen = []
    for n in even_pick(groups, cap + source.test, 311):
        chosen.append((n, {"question": "What is growing here?", "answer": SOYBEAN_ANSWERS[n.lower().split("/")[-2]],
                           "split": "", "credit": "Weed Detection in Soybean Crops (dos Santos Ferreira et al.), "
                                                  "Mendeley Data 3fmjm7ncc6, CC BY-NC 3.0",
                           **sources.place_fields({"place": "Campo Grande, Brazil"})}))
    say(f"  Soybean weeds: reading {len(chosen)} drone tiles from {len(groups)} kinds.")
    return zip_members(source, data_dir, work, lambda: remote_zip(url), chosen)


# ----------------------------------------------------------------- non-commercial: Weed Growth Stage (SIU)

WEED_GROWTH = "15808623"
# EPPO codes of the 16 weeds, as the file names start ("ABUTH_week_10_IMG_1656_frame_0006.jpeg").
EPPO_WEEDS = {"ABUTH": "velvetleaf (Abutilon theophrasti)", "AMAPA": "Palmer amaranth (Amaranthus palmeri)",
              "AMARE": "redroot pigweed (Amaranthus retroflexus)", "AMATA": "waterhemp (Amaranthus tuberculatus)",
              "AMBEL": "common ragweed (Ambrosia artemisiifolia)", "CHEAL": "lamb's quarters (Chenopodium album)",
              "CYPES": "yellow nutsedge (Cyperus esculentus)", "DIGSA": "large crabgrass (Digitaria sanguinalis)",
              "ECHCG": "barnyard grass (Echinochloa crus-galli)", "ERICA": "horseweed (Erigeron canadensis)",
              "PANDI": "fall panicum (Panicum dichotomiflorum)", "SETFA": "giant foxtail (Setaria faberi)",
              "SETPU": "yellow foxtail (Setaria pumila)", "SIDSP": "prickly sida (Sida spinosa)",
              "SORHA": "johnsongrass (Sorghum halepense)", "SORVU": "shattercane (Sorghum bicolor)"}


def prepare_weed_growth_stage_nc(source, data_dir, work, cap):
    """Weed Growth Stage Dataset (Southern Illinois University Horticulture Research Center, 2024; CC BY-NC-SA
    4.0): frames of 16 weeds filmed every week for 11 weeks after sowing. Only the pictures used are read out of the
    50 GB zip by HTTP ranges, an equal share of each weed and week; frames of the "test" part are test pictures.
    "What weed is this, and how old is it?" """
    url = zenodo(WEED_GROWTH, "weed_dataset.zip")
    z = remote_zip(url)
    groups = {}
    for n in z.namelist():
        m = re.match(r"([A-Z]+)_week_(\d+)_", n.rsplit("/", 1)[-1])
        if m and m.group(1) in EPPO_WEEDS and "/images/" in n:
            groups.setdefault(f"{m.group(1)}-{int(m.group(2)):02d}", []).append(n)
    z.close()
    chosen = []
    for n in even_pick(groups, cap + source.test, 313):
        m = re.match(r"([A-Z]+)_week_(\d+)_", n.rsplit("/", 1)[-1])
        weeks = int(m.group(2))
        answer = (f"This is {EPPO_WEEDS[m.group(1)]}, a weed, {weeks} week{'s' if weeks != 1 else ''} after it was "
                  "sown.")
        chosen.append((n, {"question": "What weed is this, and how old is it?", "answer": answer,
                           "split": "test" if "/test/" in n else "",
                           "credit": "Weed Growth Stage Dataset (SIU Horticulture Research Center), Zenodo 15808623, "
                                     "CC BY-NC-SA 4.0",
                           **sources.place_fields({"place": "Carbondale, Illinois, USA"})}))
    say(f"  Weed Growth Stage: reading {len(chosen)} pictures from {len(groups)} weeds and weeks.")
    return zip_members(source, data_dir, work, lambda: remote_zip(url), chosen)


# ----------------------------------------------------------------- non-commercial: CropAndWeed (AIT)

CNW = "https://vitro-testing.com/wp-content/uploads/2022/12/"
CNW_LABELS = "https://raw.githubusercontent.com/cropandweed/cropandweed-dataset/main/cnw/utilities/datasets.py"
CNW_TERMS = "https://github.com/cropandweed/cropandweed-dataset/blob/main/LICENCE"


def cnw_label_names():
    """{label id: name} of the full CropAndWeed label set, read from the makers' own datasets.py."""
    import requests
    text = requests.get(CNW_LABELS, timeout=60, headers={"User-Agent": USER_AGENT}).text
    block = text.split("DATASETS['CropAndWeed'] = Dataset({", 1)[1].split("})", 1)[0]
    return {int(i): name for i, name in re.findall(r"(\d+):\s*\('([^']+)'", block)}


# First words of plant names that keep their capital letter ("German chamomile").
PROPER_FIRST = {"German", "Canadian", "Italian", "Persian", "Russian", "Hungarian", "Spanish", "Japanese", "Chinese",
                "African", "American", "Indian", "English", "French", "Swedish", "Mexican", "Australian"}


def cnw_answer(counts, names):
    """The answer for one photo from {label id: count}: "The plants outlined here are maize at the four-leaf stage (3
    plants) and German chamomile (2 plants)."."""
    parts = []
    for label, n in sorted(counts.items(), key=lambda x: -x[1]):
        name = names.get(label, "")
        if not name or name.lower() in ("soil", "vegetation") or label >= 250:
            continue
        name = re.sub(r"\s+max$", ", fully grown", name, flags=re.I)
        name = re.sub(r"\s+(two|four|six|eight)-leaf stage$", r" at the \1-leaf stage", name)
        if name.split()[0] not in PROPER_FIRST and not name[:2].isupper():
            name = name[0].lower() + name[1:]
        parts.append(f"{name} ({n} plant{'s' if n != 1 else ''})")
    return sentence("The plants outlined here are " + listed(parts[:8])) if parts else ""


def prepare_cropandweed_nc(source, data_dir, work, cap):
    """CropAndWeed (Steininger et al., WACV 2023; AIT's non-commercial terms): field photos with every plant boxed
    and named. The annotations (110 MB tar) are read first; then the image tars (about 3 GB each, four of them) are
    read from the web, every other photo or so, until enough pictures are taken. "What crops and weeds are in this picture?" """
    import requests
    names = cnw_label_names()
    boxes = {}
    say("  Reading the CropAndWeed annotations (110 MB).")
    with requests.get(CNW + "cropandweed_annotations.tar", stream=True, timeout=120,
                      headers={"User-Agent": USER_AGENT}) as r:
        r.raise_for_status()
        with tarfile.open(fileobj=r.raw, mode="r|") as tar:
            for member in tar:
                if member.isfile() and "/bboxes/" in "/" + member.name and member.name.endswith(".csv"):
                    counts = {}
                    text = tar.extractfile(member).read().decode("utf-8", "replace")
                    for row in csv.reader(io.StringIO(text)):
                        if len(row) >= 5 and row[4].strip().isdigit():
                            counts[int(row[4])] = counts.get(int(row[4]), 0) + 1
                    boxes[os.path.basename(member.name)[:-4]] = counts
    folder = os.path.join(data_dir, source.key)
    os.makedirs(folder, exist_ok=True)
    rows, want = [], cap + source.test
    rng = random.Random(317)
    for part in ("cropandweed_images1of4", "cropandweed_images2of4", "cropandweed_images3of4",
                 "cropandweed_images4of4"):
        if len(rows) >= want:
            break
        with requests.get(CNW + part + ".tar", stream=True, timeout=120, headers={"User-Agent": USER_AGENT}) as r:
            r.raise_for_status()
            with tarfile.open(fileobj=r.raw, mode="r|") as tar:
                for member in tar:
                    stem = os.path.splitext(os.path.basename(member.name))[0]
                    if not member.isfile() or stem not in boxes or rng.random() > 0.5:
                        continue
                    answer = cnw_answer(boxes[stem], names)
                    target = os.path.join(folder, f"cnw-{stem}.jpg")
                    if answer and (have(target) or smaller(tar.extractfile(member).read(), target)):
                        rows.append({"picture": target, "question": "What crops and weeds are in this picture?",
                                     "answer": answer, "split": "",
                                     "credit": "CropAndWeed dataset (Steininger et al., AIT Austrian Institute of "
                                               "Technology, 2023), non-commercial use only, " + CNW_TERMS})
                    if len(rows) >= want:
                        break
    say(f"  CropAndWeed: {len(rows)} pictures.")
    return rows


# ----------------------------------------------------------------- research: Agriculture-Vision

AGVISION_TERMS = "https://drive.google.com/file/d/1tiJpMjcr8mlF1pYU-6U6ZY5jnNgbn9XF/view"
AGVISION_PAGE = "https://www.agriculture-vision.com/agriculture-vision-2021/dataset-2021"
AGVISION_HF = "https://huggingface.co/datasets/shi-labs/Agriculture-Vision"
AGVISION_FILE = "agriculture-vision.txt"           # the owner's note of where the archive is (a path or a link)
# The field problems people outlined (each a folder of masks), in words.
AGVISION_LABELS = {"double_plant": "double planting (rows sown twice over)",
                   "drydown": "drydown (crops drying out early)",
                   "endrow": "crowded end rows, where the planter turned",
                   "nutrient_deficiency": "nutrient deficiency (pale, poorly fed patches)",
                   "planter_skip": "planter skips (gaps in the rows)", "water": "standing water",
                   "waterway": "a grassed waterway", "weed_cluster": "clusters of weeds",
                   "storm_damage": "storm damage (flattened crop)"}
AGVISION_VAL = 18_334                               # tiles in the val part, which comes first in the archive


def agvision_location(work):
    """Where the owner's copy of Agriculture-Vision-2021.tar.gz is, after agreeing to the workshop's terms: the
    AGRICULTURE_VISION setting (a path or a web link), or the first line of agriculture-vision.txt in the downloads
    folder (or its agriculture_vision folder), or a .tar.gz put in that agriculture_vision folder. Raises a
    RuntimeError saying what to do when none is there."""
    folder = os.path.join(work, "agriculture_vision")
    given = os.environ.get("AGRICULTURE_VISION", "").strip()
    for note in (os.path.join(work, AGVISION_FILE), os.path.join(folder, AGVISION_FILE)):
        if not given and os.path.exists(note):
            with open(note, encoding="utf-8-sig") as f:
                given = (f.readline() or "").strip().strip('"')
    if not given and os.path.isdir(folder):
        given = next((os.path.join(folder, n) for n in sorted(os.listdir(folder)) if n.endswith(".tar.gz")), "")
    if not given:
        raise RuntimeError(
            "Agriculture-Vision needs your own copy. Read and agree to the workshop's terms (" + AGVISION_TERMS + "), "
            "get Agriculture-Vision-2021.tar.gz (21 GB) from " + AGVISION_PAGE + " or " + AGVISION_HF + ", then either "
            "put it in " + folder + ", or write its path or download link on the first line of a text file named "
            + AGVISION_FILE + " in " + work + ".")
    return given


def agvision_stream(location):
    """The archive as a stream (a local file, or a web link read as it downloads)."""
    if re.match(r"https?://", location):
        import requests
        r = requests.get(location, stream=True, timeout=120, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        return r.raw
    return open(location, "rb")


def agvision_answer(found):
    """The answer for one tile from the problems found on it."""
    if not found:
        return "This is an aerial view of farmland. No field problems are marked on it."
    return sentence("This is an aerial view of farmland showing " + listed([AGVISION_LABELS[k] for k in sorted(found)]))


def prepare_agriculture_vision(source, data_dir, work, cap):
    """Agriculture-Vision 2021 (Chiu et al., CVPR 2020; IntelinAir's workshop terms): 512-pixel aerial tiles of US
    farmland, with nine kinds of field problem outlined by agronomists. The archive is read once from start to end
    (its order is: each part's masks, then its colour tiles, then its near-infrared tiles, then its labels): a random
    share of the colour tiles is kept in the downloads folder until their labels have been read, and reading stops
    after the first part (val) when it gave enough. "What problems can be seen in this field from the air?" """
    import hashlib
    from PIL import Image
    location = agvision_location(work)
    keep = os.path.join(work, source.key)
    folder = os.path.join(data_dir, source.key)
    os.makedirs(keep, exist_ok=True)
    os.makedirs(folder, exist_ok=True)
    want = cap + source.test
    share = min(1.0, want * 1.3 / AGVISION_VAL)        # enough from the val part alone, for caps up to 14,000
    say(f"  Reading Agriculture-Vision from {location} (it is read once, from start to end).")
    tiles, found, part = {}, {}, ""

    def chosen(stem):
        """True for the tiles kept: a fixed share of them, picked by their name."""
        return int(hashlib.md5(stem.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF < share

    def finish():
        """Rows for the kept tiles whose labels have been read."""
        rows = []
        for (split, stem), path in sorted(tiles.items()):
            target = os.path.join(folder, f"agv-{split}-{stem}.jpg")
            with open(path, "rb") as f:
                if have(target) or smaller(f.read(), target):
                    rows.append({"picture": target, "question": "What problems can be seen in this field from the "
                                                                "air?",
                                 "answer": agvision_answer(found.get((split, stem), set())), "split": "",
                                 "credit": "Agriculture-Vision 2021 (Chiu et al., IntelinAir and the Agriculture-Vision "
                                           "Workshop), " + AGVISION_PAGE})
        return rows

    stream = agvision_stream(location)
    try:
        with tarfile.open(fileobj=stream, mode="r|gz") as tar:
            for member in tar:
                parts = member.name.split("/")
                if len(parts) < 4 or not member.isfile():
                    continue
                split, stem = parts[1], os.path.splitext(parts[-1])[0]
                if split not in ("train", "val"):
                    continue
                if part and split != part and len(tiles) >= want:
                    break                                   # the first part gave enough
                part = split
                if parts[2] == "images" and parts[3] == "rgb" and chosen(stem):
                    path = os.path.join(keep, f"{split}-{stem}.jpg")
                    if not os.path.exists(path):
                        with open(path, "wb") as f:
                            f.write(tar.extractfile(member).read())
                    tiles[(split, stem)] = path
                elif parts[2] == "labels" and parts[3] in AGVISION_LABELS and (split, stem) in tiles:
                    mask = Image.open(io.BytesIO(tar.extractfile(member).read()))
                    if mask.getbbox():
                        found.setdefault((split, stem), set()).add(parts[3])
    finally:
        stream.close()
    rows = finish()
    random.Random(319).shuffle(rows)
    say(f"  Agriculture-Vision: {len(rows)} tiles.")
    return rows[:want]


# ----------------------------------------------------------------- needing sign-up, and not included

LAND_SIGN_UP = {
    "Flickr: USDA, US Forest Service, Bureau of Land Management, US Department of Energy, NREL, IRRI (International "
    "Rice Research Institute), CGIAR centres (CIMMYT, ILRI, CIAT, IITA, WorldFish), FAO and the NOAA Photo Library":
        "https://www.flickr.com/services/api/misc.api_keys.html : a free Flickr API key is needed to list and download "
        "them. USDA, DOE and NOAA photos are mostly public domain; IRRI, CGIAR and FAO photos are mostly CC BY-NC-SA "
        "(personal use). Check each photo's licence on its page.",
    "MVTec AD and MVTec LOCO AD (industrial product defects; CC BY-NC-SA 4.0)":
        "https://www.mvtec.com/company/research/datasets/mvtec-ad/downloads : fill in the download form (name and "
        "e-mail). Non-commercial: personal use only. Describe the pictures as product close-ups, faulty or not.",
    "Kaggle sets (tea leaf diseases, iCassava, solar-panel dust and defect sets, construction equipment, tool "
    "recognition and others)":
        "https://www.kaggle.com : a Kaggle account is needed; check each set's licence and where its pictures came "
        "from (many are copied from web searches).",
    "Roboflow Universe sets (construction-site equipment and safety gear, excavators, solar-panel faults, litter)":
        "https://universe.roboflow.com : a free Roboflow account and API key are needed; each set shows its own "
        "licence, and many hold photos copied from the web.",
    "ACID (Alberta Construction Image Dataset) and MOCS (Moving Objects in Construction Sites)":
        "https://www.acidb.ca and the MOCS paper's page: ask the authors; no open licence is published with the "
        "pictures.",
}

LAND_NOT_INCLUDED = {
    "NOAA Photo Library": "public domain, but its new home (www.noaa.gov/digital-library) refused this machine (403); "
                          "its Flickr copy needs a key (LAND_SIGN_UP).",
    "NREL image gallery (images.nrel.gov)": "did not answer from this machine; NREL's Flickr copy needs a key.",
    "More US National Archives series (Bureau of Reclamation, TVA, Soil Conservation Service, Bureau of Mines)":
        "public domain, but the catalogue's search answered this machine with a web page instead of data; DOCUMERICA "
        "(the EPA's 1970s survey of pollution and American life) is already in the open nara pack.",
    "European Environment Agency photo library": "its pictures carry their own copyright notices and no open "
                                                 "licence for re-use in bulk.",
    "Sets that mix in augmented pictures (JMuBEN arabica coffee, lentil, sunflower, and the CS-D tea leaves, whose "
    "13,500 pictures a class were evened out by augmentation)":
        "CC BY 4.0, but their only copies mix the original photos with rotated and flipped copies, which teach "
        "nothing new.",
    "Project-AgML licence tags": "several copies are tagged with a different licence from their source (cotton, "
                                 "aubergine and moringa leaves are tagged CC BY-NC but are CC BY 4.0 on Mendeley Data; "
                                 "the wheat heads are tagged CC BY-SA but GWHD 2021 is CC BY 4.0 on Zenodo): the "
                                 "source's licence is used.",
    "SIMPD medicinal plants (CC BY-NC 3.0)": "medicinal plants rather than farming; outside this subject.",
}


# ----------------------------------------------------------------- the table

LAND_SOURCES = [
    # ---- share-alike
    Source("commons_land_industry_sa", "Wikimedia Commons: farming, environment, industry, mining, energy and "
                                       "construction, files under CC BY-SA or GFDL (share-alike)",
           "Each file CC BY-SA or GFDL (its Commons page); captions CC0",
           "Wikimedia Commons authors, CC BY-SA or GFDL, each credited in its row, https://commons.wikimedia.org",
           "share-alike", 2000, 20, prepare_commons_land_industry_sa, "about 200 MB"),
    Source("plant_seedlings_sa", "Plant Seedlings: crop and weed seedlings from above, Denmark (share-alike)",
           "CC BY-SA 4.0 (vision.eng.au.dk/plant-seedlings-dataset)",
           "Plant Seedlings Dataset (Giselsson, Jorgensen, Jensen, Dyrmann, Midtiby, Aarhus University and University "
           "of Southern Denmark, 2017), CC BY-SA 4.0, https://vision.eng.au.dk/plant-seedlings-dataset/ ; Project-AgML "
           "copy https://huggingface.co/datasets/Project-AgML/plant_seedlings_aarhus", "share-alike", 1500, 20,
           prepare_plant_seedlings_sa, "about 100 MB, read in parts"),
    # ---- non-commercial
    Source("soybean_weeds_nc", "Soybean fields in Brazil from a drone: soybean, grass weeds, broadleaf weeds or soil "
                               "(personal use)",
           "CC BY-NC 3.0 (Mendeley Data 3fmjm7ncc6)",
           "Weed Detection in Soybean Crops (Alessandro dos Santos Ferreira et al., 2017), Mendeley Data 3fmjm7ncc6, "
           "CC BY-NC 3.0", "noncommercial", 1000, 20, prepare_soybean_weeds_nc,
           "about 100 MB of tiles, read out of a 1.3 GB zip",
           terms="https://data.mendeley.com/datasets/3fmjm7ncc6/2",
           terms_summary="CC BY-NC 3.0: use with credit, not for commercial purposes."),
    Source("weed_growth_stage_nc", "Weed Growth Stage: 16 American field weeds, 1 to 11 weeks old (personal use)",
           "CC BY-NC-SA 4.0 (Zenodo 15808623)",
           "Weed Growth Stage Dataset (Southern Illinois University Horticulture Research Center, 2025), Zenodo "
           "15808623, CC BY-NC-SA 4.0, https://doi.org/10.5281/zenodo.15808623", "noncommercial", 2000, 20,
           prepare_weed_growth_stage_nc, "about 500 MB of pictures, read out of a 50 GB zip",
           terms="https://zenodo.org/records/15808623",
           terms_summary="CC BY-NC-SA 4.0: use with credit, not for commercial purposes, and anything made from it "
                         "shared under the same terms."),
    Source("cropandweed_nc", "CropAndWeed: crops and weeds outlined in field photos, Austria (personal use)",
           "AIT's own non-commercial terms, no redistribution (" + CNW_TERMS + ")",
           "CropAndWeed dataset (Daniel Steininger, Andreas Trondl, Gerardus Croonen, Julia Simon and Verena Widhalm, "
           "AIT Austrian Institute of Technology, WACV 2023), https://github.com/cropandweed/cropandweed-dataset",
           "noncommercial", 1500, 20, prepare_cropandweed_nc, "reads up to 12 GB from the web (nothing kept but "
                                                              "the pictures used)",
           terms=CNW_TERMS,
           terms_summary="Free for non-commercial purposes such as research, teaching or personal experimentation; "
                         "you must not distribute the dataset or changed copies, nor use it or anything made from it "
                         "for commercial gain. Personal, non-commercial use only."),
    # ---- research (needs the owner's own copy)
    Source("agriculture_vision", "Agriculture-Vision: field problems in aerial photos of US farmland (personal use; "
                                 "your own copy)",
           "Agriculture-Vision Workshop Terms and Conditions (IntelinAir): internal, non-commercial academic use only, "
           "for the workshop's challenge; no redistribution (" + AGVISION_TERMS + ")",
           "Agriculture-Vision dataset (Mang Tik Chiu et al., 'Agriculture-Vision: A Large Aerial Image Database for "
           "Agricultural Pattern Analysis', CVPR 2020), IntelinAir and the Agriculture-Vision Workshop, "
           + AGVISION_PAGE, "research", 1500, 20, prepare_agriculture_vision,
           "reads your 21 GB archive once (keeps about 300 MB of tiles)",
           terms=AGVISION_TERMS,
           terms_summary="IntelinAir's workshop terms: a limited licence for internal, non-commercial academic use "
                         "for the Agriculture-Vision challenge; you must not sell, share or redistribute the dataset, "
                         "must not use it for any commercial product or service, may not make derivative works other "
                         "than a challenge submission, and are asked to delete it 90 days after the challenge ends. "
                         "Read them before agreeing: they may not allow training your own model. Personal, "
                         "non-commercial use only."),
]

# The collections a picture-making model may learn from: plants, fields and drone tiles without people. Not the
# Commons entry (its photos may show farm and factory workers, and children in markets).
LAND_PICTURE_MAKING_OK = {"plant_seedlings_sa", "soybean_weeds_nc", "weed_growth_stage_nc", "cropandweed_nc",
                          "agriculture_vision"}


def main(argv=None):
    """Prepare one collection into an empty folder with a small cap and print a few rows (a quick check)."""
    import argparse
    import json
    import tempfile
    parser = argparse.ArgumentParser(description="Try one land and industry collection.")
    parser.add_argument("key", choices=[s.key for s in LAND_SOURCES])
    parser.add_argument("--data", default="")
    parser.add_argument("--cap", type=int, default=8)
    args = parser.parse_args(argv)
    source = next(s for s in LAND_SOURCES if s.key == args.key)
    source.test = 0
    data = args.data or tempfile.mkdtemp(prefix="land-")
    rows = source.prepare(source, data, os.path.join(data, "work"), args.cap)
    for row in rows[:6]:
        print(json.dumps(row, ensure_ascii=False))
    print(f"{len(rows)} rows, {len({r['picture'] for r in rows})} pictures, "
          f"{sum(1 for r in rows if r.get('child'))} rows marked child, in {data}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
