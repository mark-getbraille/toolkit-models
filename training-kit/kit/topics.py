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
          "Pills, capsules and their imprints, blister packs, medicine boxes and labels, medical supplies and "
          "instruments at home such as bandages, syringes, insulin pens and inhalers, home health tests, and animal "
          "medicines.",
          ("taiwan_pills", "pharmassist", "mediseg", "medpack_id", "scoa_blister", "med_commons_supplies",
           "med_commons_instruments", "med_commons_medicines", "vet_commons_medicine", "dental_instruments",
           "open_images_medical", "cdc_phil_supplies", "commons_medication_labels",
           # home health tests: also in "health" (real_questions.py tests them with both add-ons)
           "lfa_covid_tests", "commons_home_health_tests",
           # share-alike (with Wikipedia ticked)
           "med_vet_commons_sa", "openfacts_supplements",
           # research-only (personal use)
           "dailymed_human_labels", "dailymed_vet_labels", "c3pi_pills")),
    # Health and medical pictures (the owner's decision of 22 November 2026): home health care in one add-on of its
    # own, gathered from "home" (first aid, dental and eye care, daily-living, wellbeing and rescue things), "machines"
    # (mobility aids), "documents" (hearing and communication access) and "medicines" (dental X-rays), with the
    # skin-condition, birth and feeding and contraception and period product packs that had no topic before. The only
    # topic that may hold medical-content collections ("medical"): those are used only when the person ticks "Include
    # medical and anatomy pictures". Nothing with nudity or sexual content; not sensitive. Never used for
    # picture-making, like every add-on.
    Topic("health", "Health and medical pictures",
          "First aid supplies and skills, dental and eye care, home health tests, dental X-rays, skin conditions, "
          "mobility, daily-living and wellbeing aids, wilderness rescue, hearing and sign language, pregnancy and "
          "feeding, and contraception and period products.",
          ("commons_first_aid_supplies", "commons_first_aid_skills", "commons_dental_care", "commons_eye_care",
           "open_images_home_health", "lfa_covid_tests", "commons_home_health_tests", "denpar_dental_xrays",
           "open_images_medical",
           # mobility, daily-living, wellbeing and rescue (people_sources.py, aging_care_sources.py,
           # mental_health_sources.py, wilderness_first_aid_sources.py)
           "commons_mobility_aids", "open_images_disability", "commons_daily_living_aids", "commons_wellbeing_aids",
           "commons_wilderness_rescue", "cdc_phil_health_behaviour",
           # hearing and communication access, sign language
           "commons_hearing_communication", "commons_sign_language",
           # contraception and period products (sexual_health_sources.py: products only, no content mark)
           "commons_contraception_menstrual",
           # medical content: used only with medical pictures ticked (birth_and_feeding is marked "medical", not
           # "nudity"; it keeps only respectful care scenes)
           "scin_skin_conditions", "birth_and_feeding",
           # share-alike
           "home_health_commons_sa", "people_commons_sa",
           # non-commercial and research-only (personal use); scin, ham10000 and isic_nc are medical content
           "scin", "ham10000", "isic_nc", "wheelchair_types", "mobility_aids", "visible_disability",
           "wheelchair_detection")),
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
           "commons_barbecue_food", "commons_food_guides",
           # restaurant menus (menus_sources.py)
           "nypl_menus", "synthetic_menus",
           # home food preserving: jars, pickles, ferments, jams, dried and salted food (foraging_preserving_sources.py)
           "commons_home_preserving",
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
    # Machines, tools and devices: the vehicles, car parts, boats and aircraft moved to "transport", the mobility aids
    # to "health" and the seven-segment displays to "screens" (22 November 2026).
    Topic("machines", "Machines, tools and devices",
          "Machine parts and symbols, tools, plugs and connectors, clocks, household and electronic devices by make "
          "and model, electronic parts and repair, assistive devices, radios and antennas, generators, farm "
          "equipment, building-site safety, and computer and phone parts.",
          ("commons_cycle_parts", "commons_machine_parts", "iso_machine_symbols", "planetary_gearbox",
           "commons_connectors", "commons_tools", "clock_times", "abo_products", "commons_things", "open_images_tech",
           "commons_us_controls", "wikidata_devices", "commons_devices", "nmah_devices", "farm_commons_equipment",
           "mech_commons_building", "open_images_objects", "core50", "gso_objects",
           # electronics repair, assistive devices and building-site safety (electronics_sources.py, building_sources.py)
           "commons_electronic_parts", "commons_cables_connectors", "commons_electronics_repair",
           "commons_assistive_devices", "commons_circuit_diagrams", "open_images_electronics",
           "commons_construction_safety", "electronics_commons_sa",
           # radios, antennas and mesh radio devices (radio_sources.py; also in the radio topic)
           "commons_radios", "commons_antennas_station", "commons_mesh_data_radio", "open_images_radio",
           # generators, dynamos and wind and water turbines (power_sources.py; also in the power topic)
           "commons_generators_power", "commons_wind_water_power",
           # computer and phone basics (practical_sources.py; also in the screens topic)
           "commons_computer_basics", "open_images_computer_basics",
           # home manufacturing and making: 3D printers, cutters and lasers, CNC, lathes and mills, moulding and
           # casting, circuit board fabrication (making_sources.py; also in the home topic)
           "commons_3d_printing", "commons_cutting_lasers", "commons_cnc_machining", "commons_moulding_casting",
           "commons_pcb_fabrication", "open_images_making",
           # share-alike
           "radio_commons_sa", "making_commons_sa", "commons_mechanical_sa", "device_models_sa",
           "farm_mech_commons_sa",
           # non-commercial and research-only (personal use)
           "mechanical_parts_2022", "co3d_devices", "museums_victoria", "stanford_products")),
    # Transport and travel (the owner's decision of 22 November 2026): vehicles of every kind and getting around, in
    # one add-on, gathered from "machines" (vehicles, car parts and care, boats, aircraft and rockets, driving) and
    # "documents" (travel documents; the road, travel and water signs also stay in "documents" for reading), with the
    # transit and road-scene packs that had no topic before.
    Topic("transport", "Transport and travel",
          "Cars, trucks, motorcycles, RVs, trailers, boats, aircraft and rockets, car parts, tyres, dashboard lights, "
          "EV charging, driving and road scenes, transit and airports, road and travel signs, passports and boarding "
          "passes, buoys and trail markers.",
          ("wikidata_vehicle_models", "commons_vehicle_kinds", "commons_us_cars", "commons_ca_cars",
           "commons_airplanes", "commons_car_parts", "commons_cycle_parts", "commons_engine_bays",
           "iso_machine_symbols", "corolla_engine_bay", "tyre_condition", "spark_plug_condition",
           # car care: wipers, tyres, jacks, roadside help, EV connectors, dashboard lights (car_care_sources.py)
           "commons_car_care", "commons_ev_charging", "commons_dashboard_lights", "open_images_car_care",
           # driving, motorcycles, RVs and trailers (practical_sources.py)
           "commons_driving", "open_images_driving", "commons_trailers_rvs", "commons_motorcycle_gear",
           "open_images_motorcycles_rvs",
           # boats and paddling, small boats, buoys and trail markers (outdoors_sources.py, small_boats_sources.py)
           "commons_boating_paddling", "commons_small_boats", "commons_water_trail_markers",
           # aircraft and rockets (photo_library_sources.py and the Smithsonian air and space pack)
           "nasa_aircraft", "nasa_rockets_launch", "nasm_aircraft",
           # transit, roads and travel (travel_sources.py and the street and getting-around packs)
           "commons_us_getting_around", "commons_ca_getting_around", "commons_state_roads",
           "commons_streets_roads_na", "us_dot_street_photos", "caltrans_cctv", "tripcheck_cameras",
           "us_road_signs", "ca_road_signs", "commons_travel_signs", "synthetic_travel_documents",
           # share-alike
           "car_care_commons_sa", "commons_mechanical_sa", "dashboard_symbols_sa", "commons_airplanes_sa",
           "streetsurfacevis", "arc_d_asphalt",
           # non-commercial and research-only (personal use)
           "autovi", "dashboard_warning_icons", "car_parts_damage", "car_parts_dsmlr", "car_damage_views",
           "stanford_cars", "fgvc_aircraft", "streetsignset", "lisa_traffic_signs", "mapillary_signs", "bdd100k",
           "bosch_traffic_lights", "lisa_traffic_lights")),
    # Home and household (the owner's decision of 22 November 2026): everything about running and keeping a home in
    # one add-on. The household collections moved here from "machines"; the craft collections are also in "art" and
    # the household pests also in "nature", so those add-ons keep them. The home health collections moved on to
    # "health" (22 November 2026).
    Topic("home", "Home and household",
          "Appliances, kitchens, laundry, cleaning and hazards, home repair, heating, lighting, building, pests, "
          "baby things, sewing, crafts, emergency kits, pools, knots, camp, homestead and outdoor gear, fishing, "
          "fitness equipment, games, toys, personal care products, clothes, 3D printing, lasers and CNC.",
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
           # emergency cooking, camp stoves, grills and smokers (outdoor_cooking_sources.py)
           "commons_camp_cooking", "commons_emergency_cooking", "commons_grills_smokers",
           "open_images_outdoor_cooking",
           # homestead equipment, outdoor gear and tackle, games, clothing (the leisure collections)
           "commons_homestead_poultry_bees", "commons_homestead_farmstead", "commons_fishing_tackle",
           "commons_outdoor_gear", "open_images_outdoors", "commons_card_games", "commons_board_games_world",
           "commons_puzzles_hobbies", "open_images_games", "commons_clothing_more", "open_images_clothing",
           # share-alike
           "outdoor_cooking_commons_sa",
           "homestead_commons_sa", "outdoors_commons_sa", "games_commons_sa", "clothing_commons_sa",
           "commons_home_sa", "home_safety_commons_sa", "chemical_commons_sa", "appliance_commons_sa",
           "home_upkeep_commons_sa", "home_heating_commons_sa", "emergency_lighting_commons_sa", "building_commons_sa",
           "textile_crafts_commons_sa", "pottery_commons_sa", "jewellery_commons_sa", "crafts_commons_sa",
           # emergency preparedness and disasters (preparedness_sources.py)
           "commons_emergency_kits_power", "commons_warnings_shelters", "commons_emergency_signs_maps",
           "commons_disaster_types", "open_images_disasters", "preparedness_commons_sa",
           # generators, solar panels and batteries (power_sources.py; also in the power topic)
           "commons_generators_power", "commons_solar_batteries", "open_images_power", "power_commons_sa",
           # cleaning tools, pool equipment, knots and outdoor tools (practical_sources.py)
           "commons_cleaning_tools", "open_images_cleaning", "commons_pool_equipment", "commons_knots",
           "commons_outdoor_skills", "open_images_knots_outdoor", "knots_commons_sa",
           # fitness equipment and adaptive sports (fitness_nutrition_sources.py)
           "commons_fitness_equipment", "commons_adaptive_sports",
           # home manufacturing and making (making_sources.py; also in the machines topic)
           "commons_3d_printing", "commons_cutting_lasers", "commons_cnc_machining", "commons_moulding_casting",
           "commons_pcb_fabrication", "open_images_making", "making_commons_sa",
           # personal care and beauty products, and toys and children's products (personal_care_sources.py,
           # toys_sources.py)
           "commons_personal_care_products", "commons_historic_cosmetics", "met_historic_cosmetics",
           "open_images_personal_care", "commons_toys_by_type", "commons_ride_ons_playgrounds",
           "commons_nursery_more", "commons_museum_toys", "met_toys", "open_images_toys",
           "personal_care_commons_sa", "toys_commons_sa",
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
           # circuit board fabrication (making_sources.py; also in machines and home)
           "commons_pcb_fabrication",
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
    # security screens and tools, and computer-made scam and safe message examples (privacy_sources.py; the screens
    # and scam examples are also in "screens").
    Topic("privacy", "Privacy, security and digital safety",
          "Security keys, code tokens, routers, home cameras and webcam covers, sign-in and padlock screens, password "
          "and authenticator apps, and made-up scam texts, phishing emails and fake pop-ups with their warning signs.",
          ("commons_privacy_security", "commons_privacy_screens", "synthetic_scam_examples",
           # share-alike
           "privacy_commons_sa")),
    # Screens and apps (the owner's decision of 22 November 2026): reading phone and computer screens, gathered from
    # "documents" (screens and app screenshots), "privacy" (security screens and scam examples, which stay there too)
    # and "machines" (computer basics, which stay there too; the seven-segment displays moved here).
    Topic("screens", "Screens and apps",
          "Phone and computer screens and screenshots: apps and their buttons, error messages, dialog boxes, sign-in "
          "and lock screens, made-up scam messages, computer and phone basics, and the numbers on LED and LCD "
          "displays.",
          ("commons_screens", "commons_privacy_screens", "synthetic_scam_examples", "commons_computer_basics",
           "open_images_computer_basics", "seven_segment",
           # computer-made screens read in order (screens_sources.py)
           "synthetic_screens",
           # research-only (personal use)
           "rico_screens", "screenqa_rico", "rico_widgets")),
    # Money and paperwork (the owner's decision of 22 November 2026): money, bills, receipts, forms and specimen papers,
    # gathered from "documents" and "vision" (money by its sides, which stays there too), with the currency packs that
    # had no topic before.
    Topic("money", "Money and paperwork",
          "US, Canadian, foreign and old banknotes and coins, bills and statements, pay stubs and W-2s, receipts, price tags, "
          "blank and filled-in government and tax forms, ballots and jury summonses, and specimen papers such as "
          "visas and Social Security cards.",
          ("commons_us_money", "commons_ca_money", "commons_money_sides", "banknotes", "ghana_money", "bd_taka",
           # bills, pay, civics and government forms (daily_access_sources.py, money_work_sources.py,
           # civics_sources.py, gov_forms_sources.py, people_sources.py)
           "synthetic_bills", "synthetic_pay_documents", "synthetic_civic_documents", "synthetic_gov_forms",
           "us_federal_forms", "commons_immigration_documents", "cord",
           # foreign banknotes and coins: old coins and notes, museum coins, money in photos (world_money_sources.py)
           "commons_world_money", "met_world_coins", "open_images_money",
           # non-commercial and research-only (personal use)
           "sroie", "wildreceipt", "funsd", "xfund", "cra_forms", "gothenburg_price_tags")),
    # People and everyday activities (the owner's decision of 22 November 2026): what people are doing, gathered from
    # the people and activity packs that had no topic (people_activity_sources.py among them), with the clothing,
    # deafblind communication and adaptive sports packs, which stay in their own topics too. Nothing nude or sexual
    # (those stay only in the sensitive topics); the people packs stay never-for-picture-making.
    Topic("people", "People and everyday activities",
          "What people are doing: cooking, shopping, working, eating, reading, playing, holidays, ceremonies, events "
          "and crowds, facial expressions, gestures and sign language, hairstyles, and what people wear, from "
          "everyday photos and documentary archives.",
          ("open_images_activities", "commons_daily_life", "dollar_street_routines", "open_images_in_use",
           "commons_in_use", "vcoco_actions", "vg_people_actions", "oi_expressions", "commons_expressions",
           "bice_gestures", "vqa_expressions", "commons_sign_language", "fashionpedia", "commons_hairstyles",
           "open_images_clothing", "commons_uniformed", "commons_religious_life", "commons_us_holidays",
           "commons_ca_holidays", "commons_ca_daily_life", "nara_events", "open_images_outings",
           "commons_college_streams", "commons_state_community", "loc_fsa", "nara", "nasa_people_at_work",
           "commons_mobility_deafblind", "commons_adaptive_sports",
           # stills from public-domain films (film_stills_sources.py, also in "art")
           "pd_film_stills",
           # share-alike
           "commons_daily_life_sa", "coco_actions_sa", "commons_hairstyles_sa", "hagrid", "commons_uniformed_sa",
           # non-commercial and research-only (personal use)
           "coco_actions_nc", "stanford40_actions", "swig_situations", "har_actions", "epic_kitchens", "charades",
           "how2sign", "ravdess", "jaffe", "ifeed", "navarasa", "flickr30k")),
    # Places and buildings (the owner's decision of 22 November 2026): streets, buildings inside and out, landmarks and
    # facilities, gathered from "documents" (the indoor photos; the wayfinding signs and park facilities stay there
    # too) and the street, house, landmark and historic building packs that had no topic before.
    Topic("places", "Places and buildings",
          "Streets, pavements and crossings, neighbourhoods, houses and rooms, shops, restaurants and public places, "
          "stations, lobbies and corridors, workplaces, landmarks, places of worship, architecture, historic "
          "buildings and park facilities.",
          ("open_images_street", "outdoor_navigation", "seoul_sidewalks", "walkway_dhaka", "ptl_crossings",
           "uroac_crossings", "commons_indoor_wayfinding", "open_images_indoor", "commons_us_streets",
           "commons_ca_streets", "commons_neighbourhoods_na", "commons_streets_roads_na", "commons_us_homes",
           "commons_ca_homes", "loc_habs_houses", "loc_haer", "npgallery_historic_buildings", "npgallery_facilities",
           "commons_us_public_places", "commons_ca_public_places", "commons_ca_shops", "commons_us_eating_out",
           "commons_ca_eating_out", "commons_us_getting_around", "commons_ca_getting_around", "wikidata_landmarks",
           "wikidata_architecture", "gldv2_landmarks", "wikidata_worship", "commons_state_outdoors",
           "work_commons_workplaces", "loc_highsmith", "loc_world", "newberry_library", "dollar_street",
           # share-alike
           "indoor_commons_sa", "street_scene_commons_sa", "gldv2_sa", "commons_us_sa", "commons_ca_sa",
           "work_commons_sa", "hypersim",
           # non-commercial and research-only (personal use)
           "indoor_scenes", "rotterdam_accessibility", "mapillary_vistas", "accessparkcv")),
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
           # public-domain film stills and Golden Age comics (film_stills_sources.py, comics_sources.py)
           "pd_film_stills", "commons_golden_age_comics",
           # non-commercial and research-only (personal use)
           "vam", "mimo_instruments", "princeton_general_personal", "turkish_instruments")),
    # Documents, maps and signs: reading text and making sense of pages. The receipts, forms, bills, pay and civic
    # papers moved to "money", the screens to "screens", the travel documents to "transport", the indoor photos to
    # "places" and the hearing access pictures to "health" (22 November 2026); the road, travel and water signs and
    # the wayfinding signs stay here for reading too.
    Topic("documents", "Documents, maps and signs",
          "Reading text and making sense of pages: letters, handwriting, document pages, tables, charts, diagrams, "
          "maps, weather maps, sheet music, cards, mail, and road, safety, travel, emergency and indoor signs, buoys "
          "and trail markers.",
          ("textvqa", "textocr", "coco_text", "doclaynet", "plotqa", "loc_letters", "owid_charts",
           "pubtabnet_tables", "open_images_cards_documents", "loc_maps", "safety_signs", "commons_hazard_symbols",
           "us_road_signs", "ca_road_signs",
           "deepscores_sheet_music", "field_manual_figures", "bentham_pages", "commons_handwriting",
           "openstax_figures", "commons_charts", "wpc_surface_maps", "nhc_forecast_cones",
           "commons_indoor_wayfinding", "commons_water_trail_markers", "commons_travel_signs",
           "commons_emergency_signs_maps", "commons_radio_cards_charts",
           # national park visitor facilities and signs (photo_library_sources.py; also in "places")
           "npgallery_facilities",
           # restaurant menus (menus_sources.py, also in "food"), maths and science notation (math_notation_sources.py)
           "nypl_menus", "synthetic_menus", "synthetic_formulas", "chem_structures",
           # share-alike
           "hiertext", "mapqa", "indoor_commons_sa",
           # non-commercial and research-only (personal use)
           "dvqa", "chartqa", "scienceqa", "ai2d", "streetsignset", "fintabnet_tables", "tqa_diagrams",
           "commons_mail_parcels", "im2latex_formulas")),
    Topic("nature", "Plants, animals and nature",
          "Plants, mushrooms, insects, birds and other animals by name, household pests and pest control, pet and "
          "farm breeds and animals, crops and their diseases, weeds, poisonous plants, mushrooms and wild plants, "
          "clouds, weather and science instruments, and landscapes from the ground and from space.",
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
           # farm animals, science instruments and plant identification (the leisure collections)
           "open_images_homestead", "commons_science_instruments", "open_images_science", "commons_poisonous_plants",
           "commons_mushrooms_id", "commons_wild_plants_bark",
           # edible wild plants, wild mushrooms and their lookalikes (foraging_preserving_sources.py)
           "commons_wild_food_plants", "commons_wild_mushrooms", "inat_wild_edibles",
           # NASA Earth from space, planets and telescopes, more park wildlife and landscapes (photo_library_sources.py)
           "nasa_earth_from_space", "nasa_planets_telescopes", "npgallery_wildlife_more", "npgallery_landscapes_more",
           # share-alike
           "garden_commons_sa",
           "science_commons_sa", "plant_id_commons_sa",
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
           "npgallery_accessibility",
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
