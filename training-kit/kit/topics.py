"""Topic add-ons: one small add-on (a LoRA adapter) per subject, which the person chooses to load in the Digital
Accessibility Toolkit when they want more expertise. Qwen stays the general describer; a topic add-on only adds
knowledge of one subject on top of it.

This file is the list of topics (TOPICS) and the small, pure helpers that train.py and the wizard use for them. It
downloads nothing and needs no graphics card, so the tests and the wizard can use it anywhere.

Each Topic says:
  id               its short name, used on the command line (train.py --topic food) and in the label
  title            its name for people ("Food and packaged goods")
  description      one or two plain sentences, shown in the wizard's Topic add-ons window
  keys             the collections (sources.py keys, most of them ready-made packs) that feed it. Open ones are used
                   always; share-alike ones only with Wikipedia ticked (--with-wikipedia); non-commercial and
                   research-only ones only with their personal-use boxes (and then the add-on is personal use only).
  needs            the content choices this topic needs and turns on by itself: "nudity" for nudes in art,
                   "nudity" and "sexual" for sexual content (see sources.allowed_contents)
  sensitive        True for the topics a person may not want loaded by chance (nudity, sexual content)
  personal_only    True when the topic's add-on is always for personal use only (sexual content)
  review_contents  the content tags of checked review pictures (Describe pictures, Review collections) that fit
                   this topic; the other review pictures are left out of a topic add-on

How a topic add-on is trained (train.py --topic ID --topic-replay SHARE): the topic's collections are gathered, a
"replay" share of pictures from a broad everyday mix (EVERYDAY_KEYS: photos described in detail, photos taken by
blind people, everyday photos and their questions) is mixed in, so the add-on does not forget how to describe
ordinary pictures (mix: 15 percent of the training pictures by default, 0 to 40 allowed), and the add-on is trained
with the kit's usual training code. The topic's own test pictures are kept back (never trained on), with up to
EVERYDAY_TEST everyday test pictures, and the report says in plain words how the add-on did on each (score_lines).

Every add-on gets a small label, addon-label.json (make_label; its format is in "TOPIC ADD-ON LABEL FORMAT.txt" in
the kit folder, because the Digital Accessibility Toolkit reads it). Its licence is "personal use only" when any
personal-use collection, review picture or adult sexual content was learned from (licence_class), and "open"
otherwise. A topic add-on is a describer add-on: it is never used for picture-making.
"""

import datetime
import json
import random

# The kit's version as written in each label: the date of the kit's last change to how topic add-ons are made.
KIT_VERSION = "2026.11.20"
LABEL_FORMAT = 1
LABEL_FILE = "addon-label.json"
LICENCE_OPEN = "open"
LICENCE_PERSONAL = "personal use only"

# The everyday share ("replay") of the training pictures: 15 percent at first, 0 to 40 percent allowed.
REPLAY_DEFAULT = 0.15
REPLAY_MIN = 0.0
REPLAY_MAX = 0.40
# The most everyday test pictures kept back, to see whether ordinary description got worse.
EVERYDAY_TEST = 100

# The broad everyday mix the replay share comes from: open collections of ordinary photos described by people.
EVERYDAY_KEYS = ("docci", "vizwiz_captions", "vizwiz_vqa", "localized_narratives", "coco", "crossmodal",
                 "coco_questions", "imageinwords", "commons", "textcaps")

# Content tags that make an add-on sensitive whatever its topic (it learned from such pictures).
SENSITIVE_CONTENTS = ("nudity", "intimate", "sexual", "graphic")


class Topic:
    """One topic add-on (see the module docstring for the fields)."""

    def __init__(self, topic_id, title, description, keys, needs=(), sensitive=False, personal_only=False,
                 review_contents=()):
        """Store the fields."""
        self.id, self.title, self.description = topic_id, title, description
        self.keys = tuple(keys)
        self.needs = tuple(needs)
        self.sensitive, self.personal_only = bool(sensitive), bool(personal_only)
        self.review_contents = tuple(review_contents)


TOPICS = [
    Topic("medicines", "Medicines and medical supplies",
          "Pills, capsules and their imprints, blister packs, medicine boxes and labels, and medical supplies at "
          "home: bandages, syringes, insulin pens, inhalers, instruments, and animal medicines.",
          ("taiwan_pills", "pharmassist", "mediseg", "medpack_id", "scoa_blister", "med_commons_supplies",
           "med_commons_instruments", "med_commons_medicines", "vet_commons_medicine", "dental_instruments",
           "open_images_medical", "cdc_phil_supplies", "commons_medication_labels", "lfa_covid_tests", "commons_home_health_tests",
           # dental X-rays with the teeth they show (home health care; SCIN is medical: no topic)
           "denpar_dental_xrays",
           # share-alike (with Wikipedia ticked)
           "med_vet_commons_sa", "openfacts_supplements",
           # research-only (personal use)
           "dailymed_human_labels", "dailymed_vet_labels", "c3pi_pills")),
    Topic("drugs", "Drugs and paraphernalia",
          "Street drugs and counterfeit pills, drug seizures, and paraphernalia such as pipes, bongs, vapes, rolling "
          "papers and grinders, named plainly.",
          ("commons_drugs", "commons_drug_paraphernalia", "commons_cbp_seizures", "cdc_phil_drugs",
           "drug_firearm_commons_sa")),
    Topic("firearms", "Firearms and accessories",
          "Guns by kind, maker and model, cartridges and their headstamps, and gun accessories such as holsters, "
          "scopes, sights, lights and slings.",
          ("commons_firearm_accessories", "commons_firearm_kinds", "wikidata_firearms", "commons_firearms",
           "commons_cartridges", "drug_firearm_commons_sa", "commons_firearms_sa", "commons_weapons_sa")),
    Topic("food", "Food and packaged goods",
          "Food on the plate and in the shop: fresh or spoiled meat, fish, eggs and fruit, groceries on shelves, "
          "packaged goods with their names and use-by dates, and the text on food packs.",
          ("nutrition5k", "fresh_rotten", "avocado_ripeness", "banana_ripeness", "fruitnet_quality",
           "open_images_food", "open_images_food_more", "grocery_store", "fish_eyes", "commons_food",
           "meatscan", "eggs", "beef", "abo_packaged_goods", "abo_pet_supplies", "open_images_packaged_goods", "commons_packaging",
           "locbeef", "fish_freshness", "horse_mackerel", "fish_eyes_stages", "chicken_breast", "food_packaging",
           "packeat", "cerrado_fruits", "commons_date_codes",
           "commons_barbecue_food",
           # share-alike
           "openfoodfacts", "openfoodfacts_labels", "commons_food_sa", "openfacts_us", "openfacts_ca",
           # research-only (personal use)
           "fda_recall_photos", "freiburg_groceries", "food101", "uecfoodpix", "gothenburg_price_tags")),
    Topic("drinks", "Drinks (no alcohol)",
          "Soft drinks, energy drinks, juices, sports drinks, water, iced tea and coffee drinks, plant milks and drink "
          "mixes, in the can or bottle and in the glass.",
          ("commons_soft_drinks", "open_images_soft_drinks",
           # share-alike
           "drinks_soft_commons_sa")),
    Topic("alcohol", "Alcoholic drinks, brewing and distilling",
          "Wine, beer, spirits, cider and cocktails, bottles and labels, glassware and bar tools, and brewing, "
          "winemaking and distilling, with the legal and safety notes.",
          ("commons_alcoholic_drinks", "commons_bar_glassware", "commons_brewing_winemaking", "commons_distilling",
           "open_images_bar_drinks", "europeana_drinks_history",
           # share-alike
           "drinks_alcohol_commons_sa")),
    Topic("machines", "Vehicles, machines and devices",
          "Vehicles and their parts and dashboard symbols, machine parts, tools, plugs, clocks and displays, "
          "electronic devices, electronic parts and repair, assistive devices, radios and antennas, and "
          "building-site safety.",
          ("wikidata_vehicle_models", "commons_vehicle_kinds", "commons_us_cars", "commons_ca_cars",
           "commons_airplanes", "commons_car_parts", "commons_cycle_parts", "commons_machine_parts",
           "commons_engine_bays", "iso_machine_symbols", "corolla_engine_bay", "tyre_condition",
           "spark_plug_condition", "planetary_gearbox", "commons_connectors", "commons_tools", "clock_times",
           "seven_segment", "abo_products", "commons_things", "open_images_tech", "commons_us_controls",
           "wikidata_devices", "commons_devices", "nmah_devices", "farm_commons_equipment", "mech_commons_building",
           "open_images_objects", "core50", "gso_objects",
           # electronics repair, assistive devices and building-site safety (electronics_sources.py, building_sources.py)
           "commons_electronic_parts", "commons_cables_connectors", "commons_electronics_repair",
           "commons_assistive_devices", "commons_circuit_diagrams", "open_images_electronics",
           "commons_construction_safety", "electronics_commons_sa",
           # car care: wipers, tyres, jacks, roadside help, EV connectors, dashboard lights
           "commons_car_care", "commons_ev_charging", "commons_dashboard_lights", "open_images_car_care",
           # radios, antennas and mesh radio devices (radio_sources.py; also in the radio topic)
           "commons_radios", "commons_antennas_station", "commons_mesh_data_radio", "open_images_radio",
           # generators, dynamos and wind and water turbines (power_sources.py; also in the power topic)
           "commons_generators_power", "commons_wind_water_power",
           # share-alike
           "car_care_commons_sa", "radio_commons_sa",
           "commons_mechanical_sa", "dashboard_symbols_sa", "device_models_sa", "farm_mech_commons_sa",
           "commons_airplanes_sa",
           # non-commercial and research-only (personal use)
           "autovi", "dashboard_warning_icons", "car_parts_damage", "car_parts_dsmlr", "car_damage_views",
           "mechanical_parts_2022", "co3d_devices", "stanford_cars", "fgvc_aircraft", "museums_victoria",
           "stanford_products")),
    # Home and household (the owner's decision of 22 November 2026): everything about running and keeping a home in
    # one add-on. The household collections moved here from "machines"; the craft collections are also in "art" and
    # the household pests also in "nature", so those add-ons keep them.
    Topic("home", "Home and household",
          "Appliances and their controls, kitchens, laundry and care labels, cleaning products and hazards, home "
          "repair, locks, heating and lighting, building work and ramps, pests, baby products, sewing and crafts, "
          "first aid, dental and eye care, and emergency kits, shelters and disasters.",
          ("commons_appliances", "commons_appliance_controls", "open_images_appliance_controls", "commons_kitchen",
           "laundry_symbols", "laundry_care_labels", "commons_household_chemicals", "commons_finishes_in_use",
           "commons_household_hazards", "open_images_household_hazards",
           "commons_baby_products", "open_images_baby_products", "abo_baby_products",
           # home repair, locks, small engines and bicycles, pests (home_crafts_sources.py)
           "commons_home_repair", "commons_locks_engines_bikes", "open_images_home_upkeep", "commons_pest_control",
           # heating, firewood and emergency lighting
           "commons_home_heating", "commons_firewood", "open_images_home_heating", "commons_emergency_lighting",
           "open_images_emergency_lighting",
           # light construction and home access (building_sources.py)
           "commons_light_construction", "commons_home_access_building", "open_images_building",
           # sewing, mending and the textile crafts
           "commons_sewing_mending", "commons_upholstery_leather_shoes", "commons_knit_crochet_lace",
           "commons_quilt_embroidery_weaving", "commons_fabrics_fibres", "open_images_textile_crafts",
           "nmah_textiles_sewing",
           # other crafts (crafts_sources.py)
           "commons_pottery_ceramics", "commons_jewellery_beading", "commons_paper_crafts", "commons_candle_soap",
           "commons_glass_carving", "commons_art_supplies", "commons_models_resin", "open_images_crafts",
           # home health care: first aid supplies and skills, dental and eye care things
           "commons_first_aid_supplies", "commons_first_aid_skills", "commons_dental_care", "commons_eye_care",
           "open_images_home_health",
           # emergency cooking, camp stoves, grills and smokers (outdoor_cooking_sources.py)
           "commons_camp_cooking", "commons_emergency_cooking", "commons_grills_smokers",
           "open_images_outdoor_cooking",
           # share-alike
           "home_health_commons_sa", "outdoor_cooking_commons_sa",
           "commons_home_sa", "home_safety_commons_sa", "chemical_commons_sa", "appliance_commons_sa",
           "home_upkeep_commons_sa", "home_heating_commons_sa", "emergency_lighting_commons_sa", "building_commons_sa",
           "textile_crafts_commons_sa", "pottery_commons_sa", "jewellery_commons_sa", "crafts_commons_sa",
           # emergency preparedness and disasters (preparedness_sources.py)
           "commons_emergency_kits_power", "commons_warnings_shelters", "commons_emergency_signs_maps",
           "commons_disaster_types", "open_images_disasters", "preparedness_commons_sa",
           # generators, solar panels and batteries (power_sources.py; also in the power topic)
           "commons_generators_power", "commons_solar_batteries", "open_images_power", "power_commons_sa",
           # non-commercial and research-only (personal use)
           "cpsc_recalls")),
    # Power and electrical (the owner's decision of 22 November 2026): backup generators, solar, batteries, small wind
    # and water power, and the kit's electrical collections (wiring, outlets, panels, plugs, cables, circuits), in one
    # add-on of its own; those collections also stay in "home" and "machines" (power_sources.POWER_TOPIC_EXISTING).
    Topic("power", "Power and electrical",
          "Generators and their safety labels, solar panels, charge controllers and connectors, battery banks, wind "
          "turbines, water wheels and turbines, fuel, power lines, and home wiring, outlets, breakers, plugs, cables "
          "and circuits.",
          ("commons_generators_power", "commons_solar_batteries", "commons_wind_water_power", "open_images_power",
           # the kit's electrical and backup power collections (also in home or machines)
           "commons_home_repair", "open_images_home_upkeep", "commons_plumbing_electrical", "commons_connectors",
           "commons_electronic_parts", "commons_cables_connectors", "commons_circuit_diagrams",
           "open_images_electronics", "commons_emergency_lighting", "commons_emergency_kits_power",
           # share-alike
           "power_commons_sa", "home_upkeep_commons_sa")),
    # Radio communications (the owner's decision of 22 November 2026): ham and other two-way radio, antennas and
    # station gear, QSL cards and charts, and off-grid mesh and data radio, in one add-on of its own (the radios,
    # antennas and mesh devices are also in "machines", the cards and charts also in "documents").
    Topic("radio", "Radio communications",
          "Ham, GMRS, FRS, CB, marine and scanner radios, weather radios, antennas, towers, connectors and meters, "
          "Morse keys, ham stations, QSL cards and frequency charts, and off-grid mesh and data radio such as "
          "Meshtastic, LoRa and APRS.",
          ("commons_radios", "commons_antennas_station", "commons_radio_cards_charts", "commons_mesh_data_radio",
           "open_images_radio",
           # share-alike
           "radio_commons_sa")),
    # Privacy, security and digital safety (the owner's request of 22 November 2026): security keys and devices,
    # security screens and tools, and computer-made scam and safe message examples (privacy_sources.py).
    Topic("privacy", "Privacy, security and digital safety",
          "Security keys, code tokens, routers, home cameras and webcam covers, sign-in and padlock screens, password "
          "and authenticator apps, and made-up scam texts, phishing emails and fake pop-ups with their warning signs.",
          ("commons_privacy_security", "commons_privacy_screens", "synthetic_scam_examples",
           # share-alike
           "privacy_commons_sa")),
    Topic("art", "Art and museum objects",
          "Paintings, sculpture and museum objects, described the way museums write for blind visitors, musical "
          "instruments of every culture, and crafts: quilts, knitting, crochet, lace, weaving, fabrics, pottery, "
          "jewellery, paper, glass and carving.",
          ("cooper_hewitt", "art_institute", "met", "met_collection", "aic_collection", "cleveland_collection",
           "europeana_fashion_archaeology", "europeana", "canterbury", "auckland",
           "wellcome", "smithsonian", "tepapa", "japan_search", "ksamsok", "rijksmuseum", "getty_museum", "smk",
           "nypl", "europeana_fi", "europeana_cs", "europeana_hu", "europeana_el", "europeana_no", "europeana_pl",
           "met_instruments", "wikidata_instruments",
           "commons_knit_crochet_lace", "commons_quilt_embroidery_weaving", "commons_fabrics_fibres",
           "open_images_textile_crafts", "nmah_textiles_sewing",
           # instrument care: parts, tuning and repair
           "commons_string_instrument_parts", "commons_wind_percussion_parts", "commons_piano_parts",
           "commons_instrument_care", "open_images_instrument_care",
           # share-alike
           "instrument_care_commons_sa",
           "textile_crafts_commons_sa",
           # arts and crafts: pottery, jewellery, paper, glass, carving, art supplies, models (crafts_sources.py)
           "commons_pottery_ceramics", "museum_ceramics", "commons_jewellery_beading", "museum_jewellery",
           "commons_paper_crafts", "commons_candle_soap", "commons_glass_carving", "commons_art_supplies",
           "commons_models_resin", "museum_glass_crafts", "open_images_crafts",
           "pottery_commons_sa", "jewellery_commons_sa", "crafts_commons_sa",
           # non-commercial and research-only (personal use)
           "vam", "mimo_instruments", "princeton_general_personal", "turkish_instruments")),
    Topic("documents", "Documents, maps and signs",
          "Reading text and making sense of pages: letters, forms, receipts, tables and charts, maps, sheet "
          "music, road, safety and indoor signs (toilets, room numbers, exits), and phone screens.",
          ("textvqa", "textocr", "coco_text", "cord", "doclaynet", "plotqa", "loc_letters", "owid_charts",
           "pubtabnet_tables", "us_federal_forms", "open_images_cards_documents", "loc_maps", "safety_signs", "commons_hazard_symbols", "us_road_signs",
           "ca_road_signs",
           "deepscores_sheet_music", "field_manual_figures", "bentham_pages", "commons_handwriting",
           "openstax_figures", "commons_charts", "wpc_surface_maps", "nhc_forecast_cones",
           "commons_indoor_wayfinding", "open_images_indoor",
           "commons_emergency_signs_maps", "commons_radio_cards_charts",
           "synthetic_bills",
           # share-alike
           "hiertext", "mapqa", "indoor_commons_sa",
           # non-commercial and research-only (personal use)
           "sroie", "wildreceipt", "dvqa", "funsd", "xfund", "chartqa", "scienceqa", "ai2d", "streetsignset",
           "fintabnet_tables", "cra_forms", "screenqa_rico", "rico_screens", "rico_widgets", "tqa_diagrams",
           "commons_mail_parcels", "commons_screens")),
    Topic("nature", "Plants, animals and nature",
          "Plants, mushrooms, insects, birds and other animals by name, household pests and pest control, pet and "
          "farm breeds, crops and their diseases, weeds, clouds and weather, and landscapes seen from the ground and from space.",
          ("inaturalist", "lila_camera_traps", "gbif_species", "commons_breeds", "cattle_health",
           "agml_plant_health", "agml_weeds", "agml_harvest", "agrob_tomato", "gwhd_wheat", "inat_crops", "ccsn_clouds",
           "weather_images", "eurosat", "inaturalist_us", "inaturalist_ca", "earth_observatory", "usgs",
           "npgallery", "na_wild_mammals", "na_birds", "na_herps_fish", "na_insects", "na_invertebrates",
           "na_animal_signs", "noaa_fisheries_species", "na_domestic_animals", "commons_sky_weather",
           "commons_rocks_fossils", "commons_nara_aerial", "cdc_phil_algae",
           "commons_pest_control", "open_images_home_upkeep",
           "commons_disaster_types", "open_images_disasters",
           # gardening and lawn care
           "commons_garden_growing", "commons_garden_care", "commons_lawn_care", "commons_plant_problems",
           "open_images_garden",
           # share-alike
           "garden_commons_sa",
           "oxford_pets", "plantvillage", "plantnet_sa", "commons_breeds_sa", "inaturalist_us_sa",
           "inaturalist_ca_sa", "plant_seedlings_sa", "gaps_rocks_commons_sa", "home_upkeep_commons_sa",
           # non-commercial and research-only (personal use)
           "inaturalist_us_nc", "inaturalist_ca_nc", "plantnet_nc", "cub200", "plantdoc", "stanford_dogs",
           "soybean_weeds_nc", "weed_growth_stage_nc", "cropandweed_nc")),
    # Blind and low-vision living (the owner's request of 22 November 2026): the things of blind and low-vision life
    # in one add-on, gathered from vision_sources.py and the packs other files already had (vision_sources.
    # VISION_TOPIC_KEYS_ELSEWHERE). Kept before the sensitive topics, which stay last.
    Topic("vision", "Blind and low-vision living",
          "Braille, braille writers such as the Perkins Brailler, slates, white canes, guide dogs, tactile paving and "
          "graphics, braille signs, reading machines, magnifiers, eye charts, sighted guiding, deafblind "
          "communication, and money by touch.",
          ("commons_braille_writing", "commons_tactile_access", "commons_mobility_deafblind",
           "aph_museum_objects",
           # gathered from other files
           "commons_disability", "tapad_tactile_paving", "commons_access_features", "commons_assistive_devices",
           "commons_eye_care", "commons_crosswalks_signals", "commons_indoor_wayfinding", "commons_money_sides",
           # share-alike
           "vision_commons_sa", "commons_disability_sa",
           # research-only (personal use): photos and scans of braille pages
           "angelina_braille", "dsbi_braille")),
    Topic("nudity", "Nudity in art and photography",
          "Sensitive. Nude people in paintings, drawings, sculpture and non-sexual photographic studies of adults, "
          "described plainly and without anything sexual. No children.",
          ("art_nudes", "museum_art_nudes", "nude_photo_studies",
           # research-only (personal use)
           "princeton_art_personal"),
          needs=("nudity",), sensitive=True, review_contents=("nudity",)),
    Topic("sexual", "Sexual content",
          "Sensitive, and for personal use only. Erotic art showing adults, and checked pictures of the adult "
          "review collections, described plainly. Never publish, share or sell this add-on.",
          ("erotic_art",),
          needs=("nudity", "sexual"), sensitive=True, personal_only=True, review_contents=("sexual",)),
]


def find(topic_id):
    """The Topic with this id (any letter case), or None."""
    wanted = str(topic_id or "").strip().lower()
    return next((t for t in TOPICS if t.id == wanted), None)


def topic_list_text():
    """Every topic in plain lines ("food: Food and packaged goods"), for train.py --topic list and error messages."""
    return "\n".join(f"{t.id}: {t.title}" + (" (sensitive)" if t.sensitive else "") for t in TOPICS)


def check_replay(share):
    """The everyday share as a fraction from 0 to 0.40. A number above 1 is read as a percent (15 means 0.15).
    Raises ValueError in plain words when it is outside 0 to 40 percent."""
    try:
        value = float(share)
    except (TypeError, ValueError):
        raise ValueError(f"The everyday share must be a number from 0 to 40 percent, not {share!r}.") from None
    if value > 1:
        value /= 100.0
    if not REPLAY_MIN <= value <= REPLAY_MAX + 1e-9:
        raise ValueError(f"The everyday share must be from 0 to 40 percent; {value * 100:g} percent was asked for.")
    return round(value, 4)


def content_choices(topic, choices=None):
    """The content choices for training this topic: the person's choices (a dict with with_nudity, with_medical,
    with_sexual, with_graphic, with_noncommercial, with_research) with the topic's own needs turned on."""
    out = {"with_nudity": False, "with_medical": False, "with_sexual": False, "with_graphic": False,
           "with_noncommercial": False, "with_research": False}
    out.update({k: bool(v) for k, v in (choices or {}).items() if k in out})
    for tag in topic.needs:
        out[f"with_{tag}"] = True
    return out


def topic_sources(topic, sources, with_wikipedia=False, choices=None):
    """(collections to use, collections left out by the choices, keys this kit does not have) for a topic.
    sources is the kit's sources.py; choices as for content_choices. A collection is left out when its group's box
    is not ticked (share-alike: Wikipedia; non-commercial; research-only); a key may be missing when an optional
    collections file is not in this kit."""
    allowed = {s.key for s in sources.chosen(with_wikipedia, **content_choices(topic, choices))}
    known = {s.key: s for s in sources.SOURCES}
    used = [known[k] for k in topic.keys if k in allowed]
    left_out = [known[k] for k in topic.keys if k in known and k not in allowed]
    missing = [k for k in topic.keys if k not in known]
    return used, left_out, missing


def everyday_keys(topic, sources, with_wikipedia=False, choices=None):
    """The everyday collections the replay share comes from (EVERYDAY_KEYS that the choices allow and that are not
    the topic's own)."""
    allowed = {s.key for s in sources.chosen(with_wikipedia, **content_choices(topic, choices))}
    return [k for k in EVERYDAY_KEYS if k in allowed and k not in topic.keys]


def replay_count(topic_pictures, share):
    """How many everyday pictures make share (a fraction) of the whole training mix with topic_pictures topic
    pictures: 15 percent of the mix with 850 topic pictures is 150 everyday ones."""
    if share <= 0 or topic_pictures <= 0:
        return 0
    return int(round(topic_pictures * share / (1.0 - share)))


def mix(topic_rows, everyday_rows, share, seed=11):
    """(the training rows, how many everyday rows were added): the topic's rows with everyday rows making share of
    the whole (fewer when there are not enough), shuffled the same way each time. Everyday rows are marked
    "replay": True."""
    everyday = list(everyday_rows)
    random.Random(seed).shuffle(everyday)
    added = [dict(r, replay=True) for r in everyday[:replay_count(len(topic_rows), share)]]
    rows = list(topic_rows) + added
    random.Random(seed + 1).shuffle(rows)
    return rows, len(added)


def mark(rows, part):
    """The rows marked with the part of the test they belong to ("topic" or "everyday")."""
    return [dict(r, topic_part=part) for r in rows]


def everyday_test(rows, most=EVERYDAY_TEST, seed=12):
    """Up to most everyday test rows, picked the same way each time from all the everyday collections."""
    rows = list(rows)
    random.Random(seed).shuffle(rows)
    return rows[:most]


def review_fit(rows, topic):
    """The checked review rows that fit the topic: those with one of its review_contents (none for most topics)."""
    wanted = set(topic.review_contents)
    return [r for r in rows if wanted & set(r.get("contents") or ())] if wanted else []


def licence_class(topic, collections, sources, sexual_used=False, personal_choice=False, review_used=False,
                  own_used=False):
    """"personal use only" or "open", by the kit's rules: a topic that is always personal (sexual content), adult
    sexual content learned from, a personal-use choice made (non-commercial or research-only collections), any
    personal-use collection among collections (keys), checked review pictures, or the person's own pictures make
    it personal use only."""
    personal = (topic.personal_only or sexual_used or personal_choice or review_used or own_used or
                any(sources.is_personal(s) for s in sources.SOURCES if s.key in set(collections)))
    return LICENCE_PERSONAL if personal else LICENCE_OPEN


def is_sensitive(topic, contents_used=()):
    """True for a sensitive topic, or when the add-on learned from nudity, intimate, sexual or graphic pictures."""
    return bool(topic.sensitive or set(contents_used) & set(SENSITIVE_CONTENTS))


def make_label(topic, base_model, base_model_version, licence, sensitive, trained=None):
    """The label saved beside each topic add-on (addon-label.json; see "TOPIC ADD-ON LABEL FORMAT.txt")."""
    if licence not in (LICENCE_OPEN, LICENCE_PERSONAL):
        raise ValueError(f"unknown licence class {licence!r}")
    day = trained or datetime.date.today()
    return {"format": LABEL_FORMAT, "topic_id": topic.id, "title": topic.title, "description": topic.description,
            "base_model": base_model, "base_model_version": base_model_version, "licence_class": licence,
            "sensitive": bool(sensitive), "picture_making": False, "kit_version": KIT_VERSION,
            "trained": day.isoformat()}


def label_text(label):
    """The label as the text written to addon-label.json."""
    return json.dumps(label, indent=1, ensure_ascii=False) + "\n"


def write_label(path, label):
    """Write the label to path (addon-label.json)."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(label_text(label))


def _mean(rows):
    """The mean score of rows, or None when there are none."""
    return sum(r.get("score", 0.0) for r in rows) / len(rows) if rows else None


def score_summary(before_rows, after_rows):
    """{"topic": (before, after, pictures), "everyday": (...)} from the test results (rows marked by mark()); a part
    without test pictures is left out."""
    out = {}
    for part in ("topic", "everyday"):
        before = [r for r in before_rows if r.get("topic_part", "topic") == part]
        after = [r for r in after_rows if r.get("topic_part", "topic") == part]
        if before and after:
            out[part] = (_mean(before), _mean(after), len(before))
    return out


def score_lines(topic, summary):
    """The report's short, plain-language score of a topic add-on (summary from score_summary)."""
    lines = [f"Topic add-on: {topic.title}"]
    if "topic" in summary:
        before, after, count = summary["topic"]
        gain = after - before
        if gain >= 0.01:
            words = "it got better at this topic"
        elif gain <= -0.01:
            words = "it got worse at this topic; try training again with Full in How much to train"
        else:
            words = "no clear change at this topic"
        lines.append(f"  On this topic ({count} test pictures kept back): before {before:.3f}, after {after:.3f}: "
                     f"{words}.")
    else:
        lines.append("  This topic had no test pictures, so it could not be scored.")
    if "everyday" in summary:
        before, after, count = summary["everyday"]
        gain = after - before
        if gain < -0.03:
            words = "everyday description got worse; next time raise the everyday share"
        elif gain > 0.01:
            words = "everyday description got better too"
        else:
            words = "everyday description stayed about the same"
        lines.append(f"  On everyday pictures ({count} test pictures): before {before:.3f}, after {after:.3f}: "
                     f"{words}.")
    lines.append("  (Scores go from 0 to 1: how close the answers are to people's own descriptions.)")
    return lines
