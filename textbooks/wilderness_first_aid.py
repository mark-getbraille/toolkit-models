"""Wilderness and remote first aid for the reference library, in its own group "Reference, wilderness first aid" (the
owner's request of 2026-11-22: first aid when help is hours or days away). Keys: wilderness-first-aid (every book),
wild:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - the National Park Service's hiking and backcountry safety pages (Hike Smart, the ten essentials, trip and
    emergency plans, heat illness, lightning, purifying water, river and stream crossings, tick-borne disease,
    severe weather);
  - the US Forest Service's "Know before you go" safety pages (safety, hiking, if you get lost, hypothermia, heat,
    lightning, avalanches, ticks, sun, caves, floods);
  - NIOSH's outdoor hazards pages (venomous snakes, venomous spiders, insects and scorpions, poisonous plants,
    tick- and mosquito-borne diseases, sun exposure, wildfire smoke), kept whole as CDC's terms ask;
  - CDC's lightning safety pages, kept whole (its drowning pages are parent:cdc_child_safety's);
  - NOAA SARSAT's pages on 406 MHz distress beacons (personal locator beacons, EPIRBs, ELTs: how the satellites
    find you, registering a beacon, rescues);
  - three US Army medical bulletins, whole from the Internet Archive and judged by the release rule of
    military_release.py: TB MED 507 Heat Stress Control and Heat Casualty Management (2003), TB MED 508 Prevention
    and Management of Cold-Weather Injuries (2005) and TB MED 505 Altitude Acclimatization and Illness Management
    (2010: acute mountain sickness, HAPE and HACE).

Already in the library, and linked rather than repeated (they are the core of wilderness first aid): CDC's heat and
cold pages (firstaid:cdc_heat_cold), bites, rabies, ticks and Lyme disease (firstaid:cdc_bites_ticks), the CDC Yellow
Book with altitude illness and travel first-aid kits (firstaid:cdc_yellow_book), the NHS emergency pages
(firstaid:nhs_emergency_first_aid), the Army's First Aid FM 4-25.11 (pdf:army_fm_4_25_11_first_aid), the Special
Forces Medical Handbook ST 31-91B (firstaid:army_st_31_91b_special_forces_medical), Survival ATP 3-50.21 and FM 21-76,
the Basic Cold Weather Manual FM 31-70 and Military Mountaineering TC 3-97.61 (field manuals), Field Hygiene and
Sanitation TC 4-02.3 and the emergency water books (outcook:), the weather safety pages (prep:nws_safety), the
preparedness books (ready:) and the radio rules for beacons (radio:).

Every book's notice ends with the wilderness note: general information, not training, medical advice or a diagnosis;
in an emergency call 911, or use the SOS of a satellite messenger or a personal locator beacon where there is no
signal; take a wilderness first aid course before you go.

Not built (NOT_INCLUDED, link-only): the Wilderness Medical Society practice guidelines (no derivatives,
non-commercial), NOLS, WMA, SOLO and the Red Cross wilderness courses (copyright), the US Coast Guard's cold-water
pages (no page found), the Army's desert, jungle and mountain operations manuals (tactics), and Wikibooks (already in
the Kiwix library).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build); CDC's terms and the Park Service's disclaimer are checked at every build and their conditions met in the
notice; the Army bulletins follow military_release.py (the builder writes their release line).

Run from the repository's folder:
  python3 textbooks/wilderness_first_aid.py wild:usfs_backcountry_safety --out build/textbooks --limit 5
  python3 textbooks/wilderness_first_aid.py --list wilderness-first-aid
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared helpers (cdc_book, pages_book) of the new health modules
import outdoor_cooking as O  # noqa: E402 - the Park Service's terms and page marks

GROUP = "wildfirstaid"
GROUPS = {GROUP: "Reference, wilderness first aid"}
NOTE = ("General information, not training, medical advice or a diagnosis. In an emergency call 911, or use the SOS "
        "of a satellite messenger or a personal locator beacon (PLB) where there is no phone signal. Take a "
        "wilderness first aid course before you go.")

NPS = "https://www.nps.gov"
NPS_PAGES = [NPS + p for p in ("/articles/hiking-safety.htm", "/articles/10essentials.htm", "/articles/gtgtripplan.htm",
                               "/articles/gtgemergencyplan.htm", "/subjects/healthandsafety/trip-planning-guide.htm",
                               "/articles/heat-illness.htm", "/articles/lightning-safety.htm",
                               "/subjects/healthandsafety/severe-weather-safety.htm", "/articles/2wayspurifywater.htm",
                               "/articles/river-and-stream-safety.htm", "/articles/safe-river-crossings.htm",
                               "/articles/one-health-disease-ticks-borne.htm")]
FS = "https://www.fs.usda.gov/visit/know-before-you-go/"
FS_TOPICS = ("safety", "hiking", "if-you-get-lost", "hypothermia", "heat", "lightning", "avalanches", "ticks",
             "sun-safety", "cave-safety", "floods")
SARSAT = "https://www.sarsat.noaa.gov/"
SARSAT_PAGES = [SARSAT + p + "/" for p in ("emergency-406-beacons", "register-your-beacon",
                                           "search-and-rescue-satellites", "cospas-sarsat-system-overview",
                                           "sarsat-us-rescues")]

GUIDES = [
    dict(M.pages_book(GROUP, "nps_hiking_backcountry_safety", "Hiking and backcountry safety (National Park Service)",
                      "Backcountry safety", "National Park Service (US Department of the Interior)", NPS_PAGES,
                      r"^https://www\.nps\.gov/(articles|subjects/healthandsafety)/[a-z0-9-]+\.htm$",
                      "The National Park Service's safety pages for hikers, each whole: Hike Smart, the ten "
                      "essentials (including a first-aid kit, navigation, extra water and food, and a way to call for "
                      "help), planning a trip and leaving an emergency plan, heat illness, lightning safety, severe "
                      "weather, two ways to purify water, river and stream safety and safe crossings, and tick-borne "
                      "disease.",
                      f"From the National Park Service: \"material created by the National Park Service ... is "
                      f"generally considered in the public domain\"; source: National Park Service (nps.gov). {NOTE}",
                      content=(r'<div id="main" role="main" class="MainContent">',
                               r'<div id="related_content_position">|<footer\b'),
                      units=[(r"heat|lightning|weather", "Heat, lightning and weather"),
                             (r"water|river|crossing", "Water and rivers"), (r"tick", "Ticks"),
                             (r".", "Planning and the ten essentials")]),
         licence_page=O.NPS_TERMS, licence_text=O.NPS_TEXT),
    M.pages_book(GROUP, "usfs_backcountry_safety", "Know before you go: backcountry safety (US Forest Service)",
                 "Backcountry safety", "US Forest Service (US Department of Agriculture)", [FS + t for t in FS_TOPICS],
                 rf"^https://www\.fs\.usda\.gov/visit/know-before-you-go/({'|'.join(FS_TOPICS)})$",
                 "The Forest Service's safety pages for visitors, each whole: general safety, hiking, what to do if "
                 "you get lost, hypothermia, heat, lightning, avalanches, ticks, sun safety, caves and floods. (Its "
                 "camping, food, bear and water pages are the outdoor cooking books'.)",
                 f"From the US Forest Service: a US government work (public domain). {NOTE}",
                 units=[(r"hypothermia|heat|sun", "Heat and cold"), (r"lightning|avalanche|flood", "Weather and "
                        "avalanches"), (r"ticks", "Ticks"), (r".", "Safety and getting lost")]),
    M.cdc_book(GROUP, "cdc_niosh_outdoor_hazards", "Venomous snakes, spiders, insects, poisonous plants and other "
               "outdoor hazards (CDC NIOSH)", "Bites, stings and poisonous plants", ["niosh/outdoor-workers"],
               "NIOSH's outdoor hazards pages, every page: venomous snakes (which ones, preventing bites, first aid "
               "and what not to do), venomous spiders, insects and scorpions (stings and allergic reactions), "
               "poisonous plants (poison ivy, oak and sumac), tick-borne and mosquito-borne diseases, sun exposure "
               "and wildfire smoke.", units=[(r".", "Outdoor hazards")], note=NOTE),
    M.cdc_book(GROUP, "cdc_lightning", "Lightning safety (CDC)", "Lightning", ["lightning"],
               "CDC's lightning safety pages, every page: how lightning strikes people, staying safe outdoors (no "
               "place outside is safe in a thunderstorm; go indoors or into a hard-topped vehicle) and indoors, "
               "and first aid for someone struck by lightning (call 911; they carry no charge and can be touched). "
               "CDC's drowning prevention pages are already in the parenting books.",
               units=[(r".", "Lightning")], note=NOTE),
    M.pages_book(GROUP, "noaa_sarsat_beacons", "Distress beacons and search and rescue satellites (NOAA SARSAT)",
                 "Calling for help: beacons", "NOAA Search and Rescue Satellite Aided Tracking (SARSAT)",
                 SARSAT_PAGES, r"^https://www\.sarsat\.noaa\.gov/[a-z0-9-]+/$",
                 "NOAA SARSAT's pages, each whole: 406 MHz emergency distress beacons (personal locator beacons for "
                 "people on land, EPIRBs for boats, ELTs for aircraft) and how to use them, registering a beacon "
                 "(required by law for US-coded beacons, and renewed every two years), how the search and rescue "
                 "satellites find a beacon, the Cospas-Sarsat system, and US rescues.",
                 f"From NOAA (a US government work, public domain). Beacon registration questions: 1-888-212-SAVE "
                 f"(1-888-212-7283). {NOTE}",
                 content=(r'id="main-content">', r'<footer\b'),
                 units=[(r"register", "Registering a beacon"), (r".", "Beacons and satellites")]),
]


def tb_med(name, title, archive, published, subject, description):
    """One US Army technical bulletin (medical) read whole from its Internet Archive copy; the builder judges it by
    the release rule of military_release.py (military=True) and writes its release line."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher="Headquarters, Departments of the Army "
                    "and the Air Force", archive=archive, military=True, published=published,
                    version=f"{published} edition (Internet Archive item {archive})", description=description,
                    notice=f"A work of the US armed forces (public domain under 17 U.S.C. 105); the builder says what "
                           f"its own front pages print about distribution. Written for military medical staff and "
                           f"leaders; practice may have changed since. {NOTE}")


PDFS = [
    tb_med("army_tb_med_507_heat", "Heat Stress Control and Heat Casualty Management (TB MED 507, 2003)",
           "ost-military-medical-tbmed507", "2003", "Heat illness",
           "The Army and Air Force bulletin on heat: how the body handles heat, acclimatisation, water and work-rest "
           "tables, preventing heat illness, and recognising and treating heat cramps, heat exhaustion, exertional "
           "heat stroke and low blood sodium (drinking too much water)."),
    tb_med("army_tb_med_508_cold", "Prevention and Management of Cold-Weather Injuries (TB MED 508, 2005)",
           "prevention-and-management-of-cold-weather-injuries", "2005", "Cold injuries",
           "The Army bulletin on cold: how the body loses heat, clothing and shelter, and preventing, recognising "
           "and treating hypothermia, frostbite, non-freezing cold injuries (trench foot, chilblains), cold-water "
           "immersion and dehydration in the cold."),
    tb_med("army_tb_med_505_altitude", "Altitude Acclimatization and Illness Management (TB MED 505, 2010)",
           "ost-military-medical-tbmed505", "2010", "Altitude illness",
           "The Army bulletin on high altitude: acclimatisation and staged ascent, and preventing, recognising and "
           "treating acute mountain sickness, high-altitude pulmonary oedema (HAPE) and high-altitude cerebral "
           "oedema (HACE), with descent as the main treatment."),
]

COLLECTION = K.Collection("wild", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"wilderness-first-aid": lambda: [f"wild:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "wild_us_gov": "www.fs.usda.gov and www.sarsat.noaa.gov: works of the US government (17 U.S.C. 105, checked on "
                   "govinfo.gov's policies page at every build); robots.txt allows the pages; no AI rules (checked "
                   "2026-11-22).",
    "wild_nps_cdc": "The Park Service's disclaimer (as outcook_usfs_nps, 5 seconds between pages) and CDC's terms (as "
                    "mind_cdc), checked at every build; the CDC pages are kept whole.",
    "wild_tb_med": "TB MED 505, 507 and 508: works of the US armed forces, read from the Internet Archive and judged "
                   "by the release rule of military_release.py (the owner's decision of 22 November 2026).",
}
NOT_INCLUDED = [
    ("Wilderness Medical Society Clinical Practice Guidelines (Wilderness & Environmental Medicine): frostbite, "
     "hypothermia, altitude illness, heat illness, drowning, lightning, wound care, spine injury, anaphylaxis, "
     "snakebite and others", "Those that are open access are CC BY-NC-ND (non-commercial, no derivatives), and the "
     "journal's publisher (SAGE) does not offer the files to programs; not built. The owner may read them himself "
     "(personal use). Link-only. Index: https://wms.org/magazine/1316/practice-guidelines and "
     "https://journals.sagepub.com/home/wem"),
    ("NOLS, the Wilderness Medical Associates (WMA), SOLO, Desert Mountain Medicine and the American Red Cross "
     "wilderness and remote first aid courses and field guides", "Copyright, not openly licensed (checked "
     "2026-11-22). Link-only: take one of their courses before a remote trip. Index: https://www.nols.edu/en/"
     "wilderness-medicine/ , https://www.wildmed.com/ , https://www.soloschools.com/ and https://www.redcross.org/"
     "take-a-class/first-aid/wilderness-first-aid"),
    ("US Coast Guard and NOAA cold-water immersion guidance (1-10-1: cold shock, swimming failure, hypothermia)",
     "No US Coast Guard or NOAA page on cold-water immersion was found that the builder may read "
     "(weather.gov/safety/cold-water answered \"404\"; uscgboating.org's pages carry no such guide in a form a program "
     "can find, checked 2026-11-22). TB MED 508 covers cold-water immersion, and the weather safety pages are "
     "prep:nws_safety. Link-only. Index: https://www.uscgboating.org/"),
    ("US Army Desert Operations (FM 90-3), Jungle Operations (FM 90-5) and Mountain Operations (FM 3-97.6)",
     "Built whole elsewhere since the owner's rule of 22 November 2026 (military_whole.py, milw:), not repeated "
     "here; their medical parts repeat TB MED 505, 507 and 508 (built here). Index: "
     "https://archive.org/details/fm-90-3-desert-operations-1993"),
    ("TB MED 507 (2022 edition) and TB MED 508 newer editions", "No copy with a text layer was found at the "
     "Internet Archive or on an open government address in this pass (armypubs.army.mil refuses programs); the 2003 "
     "and 2005 editions are built and say their date. Index: https://armypubs.army.mil/"),
    ("Wikibooks: Wilderness First Aid and First Aid (CC BY-SA)", "Already in the toolkit's Kiwix library (Wikibooks in "
     "full); not repeated. Index: https://en.wikibooks.org/wiki/First_Aid"),
    ("Poisonous plants and mushrooms by sight", "The plant identification collection (another collection of this "
     "library) and NIOSH's poisonous plants page (wild:cdc_niosh_outdoor_hazards) cover them; never eat a wild "
     "mushroom or plant on a picture's say-so. Index: https://www.cdc.gov/niosh/outdoor-workers/about/"
     "poisonous-plants.html"),
    ("Satellite messenger and PLB makers' guides (Garmin inReach, SPOT, ZOLEO, ACR, Ocean Signal)", "The makers' "
     "copyright; listed as links in the manual collection wilderness_first_aid. Index: https://www.acrartex.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
