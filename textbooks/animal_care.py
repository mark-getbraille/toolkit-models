"""Animal care and veterinary books for the reference library, in their own group "Reference, animal care and
veterinary" (the owner's request of 2026-11-23: practical offline knowledge on caring for farm animals and pets in
health and sickness). Keys: animal-care (every book), the themes vet-livestock, vet-pets and vet-classics, and
vet:<name>. A sibling of pet_care.py (pet:), which has the everyday pet books.

What this module builds, in plain words:
  - USDA APHIS's livestock and poultry disease pages, every page under poultry, cattle, swine, horses, and sheep and
    goats (bird flu, Newcastle disease, tuberculosis, brucellosis, swine fevers, equine infectious anaemia and the
    other diseases farmers must watch for and report), and the FDA Center for Veterinary Medicine's pages for keepers
    of food-producing animals (drug residues, records, talking to the veterinarian before treating);
  - CDC's pages on diseases people catch from animals (zoonoses) not already in the library: One Health, parrot fever
    (psittacosis), Q fever, bird flu in people, toxoplasmosis, ringworm, echinococcosis and toxocariasis (kept whole
    with their text unchanged, as CDC's terms ask);
  - the US Department of Agriculture's classic Special Reports on Diseases of the Horse (1923 edition) and Diseases
    of Cattle (1942 edition), and the two Yearbooks of Agriculture on animal health, Keeping Livestock Healthy (1942)
    and Animal Diseases (1956): works of the US government, each a whole veterinary handbook for farmers;
  - the US Army's horse and dog manuals: The Army Horse in Accident and Disease (1909), the Manual for Stable
    Sergeants (1917), the Manual for Army Horseshoers (1917) and TM 10-396 War Dogs (1943, read whole), judged at
    every build by the release rule for military publications (military_release.py);
  - old public-domain veterinary books (published before 1931), marked as history with the note "ask a
    veterinarian; old treatments may be harmful": James Law's five-volume Text-Book of Veterinary Medicine
    (1896-1903), Mayo's The Diseases of Animals (1913), Hayes's Veterinary Notes for Horse Owners (1915), Moussu's
    Diseases of Cattle, Sheep, Goats and Swine (1920), Craig's Diseases of Swine (1906), Salmon's The Diseases of
    Poultry (1899), Pearl, Surface and Curtis's Diseases of Poultry (1915), Randall's The Practical Shepherd (1864),
    Muller and Glass's Diseases of the Dog (1911), Hill's The Management and Diseases of the Dog (1888), Lemmon's
    Training the Dog (1914), and the British War Office's Animal Management (1923) and Veterinary Manual (War) (1915);
  - vet:index, a guide in plain words to every animal care book, manual and picture pack in the library, by animal
    (horses, cattle, sheep and goats, pigs, poultry, rabbits, dogs and cats), with diseases people catch from animals,
    medicines, first aid and the links-only sources.

Every book's notice carries VET_NOTE (not veterinary advice; diseases that spread from animals to people: wash hands,
gloves, see a doctor after a bite; reportable diseases go to the veterinarian or the state veterinarian).

Already in the library and linked from the index, not repeated: the pet care books (pet:, CDC Healthy Pets and FDA pet
pages), APHIS pet travel (home:aphis_pets), the animal medicine labels (med:animal), CDC's rabies, tick and wild game
pages (firstaid:cdc_bites_ticks, gamefish:), the old poultry, goat, rabbit, pig and bee books (homestead:), the Peace
Corps poultry, livestock and rabbit manuals (apt:), the USDA Farmers' Bulletins, livestock health among them
(pub:usda_farmers_bulletins), the Army pack animal manuals (kmil:), horseshoeing and butchering books (hfill:), the
Army veterinary food inspection courses (service-skills-veterinary), and the breed and veterinary picture packs. Guide
dogs are in the blind-living books (vision:).

Not built (NOT_INCLUDED, with the reason and an address): the Merck Veterinary Manual, AVMA and university extension
guides (copyright), Kirk's books on dogs and cats (no downloadable copy found), the 1942 Diseases of the Horse (a
lending-library scan), and others listed below.

Run from the repository's folder:
  python3 textbooks/animal_care.py vet:usda_yearbook_1942_keeping_livestock_healthy --out build/textbooks --limit 3
  python3 textbooks/animal_care.py --list animal-care
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared CDC book helper
import practical_index as X  # noqa: E402 - the index maker
from old_ia_books import old_book  # noqa: E402

PREFIX = "vet"
GROUP = "animalcare"
GROUPS = {GROUP: "Reference, animal care and veterinary"}

# The safety note every book here carries (the owner asked for notes on diseases people catch from animals and bites).
VET_NOTE = ("Information, not veterinary advice: ask a veterinarian. Many animal diseases spread to people "
            "(zoonoses): wash your hands after handling animals, their bedding or droppings, wear gloves for a sick or "
            "dead animal, and see a doctor after an animal bite or scratch. A sudden illness or death in a herd or "
            "flock may be a reportable disease: call your veterinarian or the state veterinarian.")
# The note on every old book (published before 1931) and every historical government handbook.
OLD_NOTE = ("Published in {year}: a historical book. Ask a veterinarian; old treatments may be harmful: many medicines "
            "it names (arsenic, mercury, strychnine, lead and other poisons) are now known to be dangerous or are "
            "banned, bleeding and firing are no longer used, and modern vaccines and medicines have replaced most of "
            "its remedies.")
HISTORY_NOTE = ("Published in {year}: its medicines and treatments are those of its day. Ask a veterinarian; old "
                "treatments may be harmful, and many medicines it names are no longer used or allowed.")
# The first words of a military manual's notice; the builder puts the truthful release line in front of it.
MIL_NOTICE = ("The release line before this says what its own front pages print about distribution. Written for "
              "army horse and dog handlers: its methods and medicines are those of its day. ")
USDA = "US Department of Agriculture (USDA)"
YEARBOOK_NOTICE = ("A work of the US Department of Agriculture (public domain), read from the National Agricultural "
                   "Library's scan on the Internet Archive: the machine-read text has the scanner's mistakes. ")


def _gov(name, title, subject, publisher, archive, year, description, notice=""):
    """One US government handbook read from its Internet Archive scan (a work of the US government), with the
    historical note and the vet note."""
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher=publisher, archive=archive,
                    published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                    description=f"{description} {HISTORY_NOTE.format(year=year)}",
                    notice=(notice or YEARBOOK_NOTICE) + VET_NOTE)


def _mil(name, title, subject, archive, year, description, old=True):
    """One US Army manual of the Internet Archive, judged by the release rule at every build (military=True); a
    manual published before 1931 is also checked for its date (old_public_domain)."""
    fields = dict(military=True, work="a work of the US Army")
    if old:
        fields["old_public_domain"] = True
    return K.us_pdf(GROUP, name=name, title=title, subject=subject, publisher="War Department (US Army)",
                    archive=archive, published=str(year), version=f"{year} edition (Internet Archive item {archive})",
                    description=f"{description} {HISTORY_NOTE.format(year=year)}", notice=MIL_NOTICE + VET_NOTE,
                    **fields)


def _old(name, title, subject, publisher, archive, year, description, country="United States", note=OLD_NOTE):
    """One old public-domain veterinary book (published before 1931), marked as history."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=VET_NOTE,
                    country=country)


# ====================================================================== web pages (US government)

APHIS = "https://www.aphis.usda.gov/livestock-poultry-disease"
APHIS_KINDS = ("avian", "cattle", "swine", "equine", "sheep-goat")
FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FDA_LIT = FDA + "/animal-veterinary/animal-health-literacy/"
FDA_FOOD_ANIMALS = [FDA_LIT + p for p in (
    "food-producing-animals-such-cattle-pigs-and-chickens",
    "talk-you-treat",
    "adequate-records-help-prevent-illegal-drug-residues-and-ensure-food-safety",
    "how-cows-eat-grass",
    "banamine-transdermal-nonsteroidal-anti-inflammatory-drug-approved-control-pain-cattle-foot-rot")]
# CDC sites on diseases from animals that no other book of the library reads (rabies, ticks, wild game, brucellosis,
# tularemia, leptospirosis, hantavirus, plague and Healthy Pets are elsewhere).
CDC_SITES = ["one-health", "psittacosis", "q-fever", "bird-flu", "toxoplasmosis", "ringworm", "echinococcosis",
             "toxocariasis"]

GUIDES = [
    K.guide(GROUP, "aphis_livestock_poultry_disease", "Livestock and poultry diseases: poultry, cattle, pigs, horses, "
            "sheep and goats (USDA APHIS)", "Livestock and poultry diseases",
            "Animal and Plant Health Inspection Service (APHIS), US Department of Agriculture",
            [f"{APHIS}/{k}" for k in APHIS_KINDS],
            rf"^{APHIS.replace('.', chr(92) + '.')}/({'|'.join(APHIS_KINDS)})(/[a-z0-9-]+)*$",
            "USDA APHIS's pages on the diseases of farm animals, every page under poultry, cattle, swine, horses, and "
            "sheep and goats: avian influenza (bird flu) and Defend the Flock biosecurity for backyard flocks, "
            "virulent Newcastle disease, bovine tuberculosis, brucellosis, cattle fever ticks, African and classical "
            "swine fever, equine infectious anaemia, equine herpes and piroplasmosis, scrapie, and the other "
            "diseases keepers must watch for and report.",
            "From the USDA Animal and Plant Health Inspection Service: a work of the US government (public domain). "
            "Reporting rules differ by state. " + VET_NOTE, depth=2, limit=150,
            follow=rf"^{APHIS.replace('.', chr(92) + '.')}/({'|'.join(APHIS_KINDS)})/[a-z0-9-]+$",
            units=[(r"/avian", "Poultry and birds"), (r"/cattle", "Cattle"), (r"/swine", "Pigs"),
                   (r"/equine", "Horses"), (r"/sheep-goat", "Sheep and goats")]),
    dict(X.page_list_book(GROUP, "fda_food_producing_animals", "Food-producing animals: medicines, records and residues "
                          "(FDA Center for Veterinary Medicine)", "Medicines for farm animals",
                          "Center for Veterinary Medicine, US Food and Drug Administration (FDA)", FDA_FOOD_ANIMALS,
                          rf"^{FDA_LIT.replace('.', chr(92) + '.')}[a-z0-9-]+$",
                          "The FDA's pages for people who keep cattle, pigs, chickens and other animals raised for "
                          "food: talking to your veterinarian before you treat, keeping treatment records so no drug "
                          "residues reach meat, milk or eggs, how cows digest grass, and a pain medicine approved for "
                          "foot rot in cattle.",
                          "From the US Food and Drug Administration: FDA's web pages \"are in the public domain and may "
                          "be republished\"; credit to the FDA, with no endorsement implied. Follow each medicine's "
                          "label and withdrawal time. " + VET_NOTE),
         licence_page=FDA_POLICY, licence_text=FDA_TEXT),
    M.cdc_book(GROUP, "cdc_zoonoses", "Diseases people catch from animals: One Health, parrot fever, Q fever, bird "
               "flu, toxoplasmosis, ringworm and worms (CDC)", "Zoonoses: diseases from animals", CDC_SITES,
               "CDC's pages on diseases that spread between animals and people, every page of each: One Health "
               "(people, animals and the environment together, and the zoonotic diseases), psittacosis (parrot "
               "fever, from pet birds and poultry), Q fever (from sheep, goats and cattle, especially at birthing), "
               "bird flu in people (avian influenza: protecting yourself around sick or dead birds and poultry), "
               "toxoplasmosis (cat litter, raw meat and pregnancy), ringworm (from pets and livestock), "
               "echinococcosis (tapeworms from dogs and livestock) and toxocariasis (roundworms from dogs and "
               "cats).", units=[(r"/one-health/", "One Health"), (r"/bird-flu/", "Bird flu in people"),
                                (r"/(psittacosis|q-fever)/", "Parrot fever and Q fever"),
                                (r"/(toxoplasmosis|toxocariasis|echinococcosis)/", "Parasites from animals"),
                                (r".", "Ringworm")], note=VET_NOTE, limit=250),
]

# ====================================================================== USDA and Army handbooks

PDFS = [
    _gov("usda_special_report_diseases_horse_1923", "Special Report on Diseases of the Horse (USDA Bureau of Animal "
         "Industry, 1923 edition)", "Horse diseases", "Bureau of Animal Industry, " + USDA,
         "specialreportond0000drsp_w6u7", 1923,
         "The US government's classic handbook for horse owners, revised by John R. Mohler: the anatomy of the "
         "horse, the examination of a sick horse and how to give medicines, then the diseases system by system "
         "(digestion, breathing, heart and blood, nervous system, urinary and breeding organs, skin, eyes, bones "
         "and joints, the feet and lameness, wounds), parasites, infectious diseases and shoeing."),
    _gov("usda_special_report_diseases_cattle_1942", "Special Report on Diseases of Cattle (USDA Bureau of Animal "
         "Industry, 1942 edition)", "Cattle diseases", "Bureau of Animal Industry, " + USDA, "CAT10502663", 1942,
         "The US government's classic handbook for cattle keepers, last revised in 1942: the examination of sick "
         "cattle, feeding and digestive troubles, bloat, diseases of the breathing and heart, the udder and milk, "
         "calving and the newborn calf, the skin, bones and feet, parasites, poisonous plants, and the infectious "
         "diseases (tuberculosis, brucellosis, anthrax, blackleg and others)."),
    _gov("usda_yearbook_1942_keeping_livestock_healthy", "Keeping Livestock Healthy: The Yearbook of Agriculture 1942",
         "Livestock health", USDA, "yoa1942", 1942,
         "The USDA's yearbook on animal health, written for farmers: disease prevention and sanitation, nutrition "
         "and deficiency diseases, poisonous plants, parasites, and chapters on the diseases of horses and mules, "
         "cattle, sheep and goats, swine, poultry, and dogs, cats and fur animals, with what each disease looks "
         "like and how it was prevented and treated."),
    _gov("usda_yearbook_1956_animal_diseases", "Animal Diseases: The Yearbook of Agriculture 1956",
         "Livestock health", USDA, "yoa1956", 1956,
         "The USDA's second yearbook on animal health: how diseases spread and are kept out, vaccines and "
         "medicines of the 1950s, and the diseases and parasites of cattle, swine, sheep and goats, horses, "
         "poultry, and dogs and cats, with a chapter on diseases people catch from animals."),
    _mil("army_horse_in_accident_and_disease_1909", "The Army Horse in Accident and Disease (US Army, 1909 edition)",
         "Horse first aid and diseases", "armyhorseinaccid00mounrich", 1909,
         "A manual for the students of the Mounted Service School: the horse's body, examining a sick or lame "
         "horse, first aid for wounds and accidents in the field, the common diseases of the army horse, and "
         "the care of the feet."),
    _mil("army_manual_for_stable_sergeants_1917", "Manual for Stable Sergeants (US Army, 1917)",
         "Horse care and stable management", "manualforstables00unit", 1917,
         "The Army's handbook for the soldier in charge of a stable: the horse's body and how it works, feeding "
         "and watering, grooming, stabling and bedding, the care of the feet and shoeing, conditioning, first aid "
         "and nursing of sick and injured horses, and the common diseases and how to prevent them."),
    _mil("army_manual_for_horseshoers_1917", "Manual for Army Horseshoers (US Army, 1917)",
         "Hoof care and horseshoeing", "manualforarmyhor00moun", 1917,
         "The Army's textbook for horseshoers at the Mounted Service School: the bones and structure of the horse's "
         "foot, the forge and tools, examining a horse for shoeing, preparing the hoof, making and fitting shoes, "
         "corrective shoeing, and the diseases of the foot. Horseshoeing is skilled work: a horse can kick; learn "
         "from a trained farrier."),
    _mil("army_tm_10_396_war_dogs_1943", "War Dogs (US Army, TM 10-396, 1943)", "Dog care and training",
         "tm-10-396-war-dogs-1943", 1943,
         "The Army's 1943 technical manual on its dogs, read whole: choosing dogs, kennels and feeding, grooming and "
         "health care, first aid for dogs, the principles of training and the commands of basic obedience, and the "
         "training of sentry, messenger, scout and sledge dogs of the Second World War, kept as history.",
         old=False),
]

# ====================================================================== old veterinary books (before 1931)

LAW_VOLUMES = [
    (1, "General pathology; diseases of the respiratory and circulatory organs, the blood vessels and the lymphatic "
        "system in all domestic animals", 1896),
    (2, "Diseases of the digestive organs, liver, pancreas and spleen", 1900),
    (3, "Diseases of the nervous system, the urinary and breeding organs, the eye and the skin, and constitutional "
        "diseases", 1901),
    (4, "Infectious diseases", 1902),
    (5, "Parasites and parasitic diseases", 1903),
]
PDFS += [
    _old(f"law_text_book_veterinary_medicine_v{n}", f"Text-Book of Veterinary Medicine, volume {n} (James Law, "
         f"{year})", "Veterinary medicine (old book)", "James Law, Cornell University (published by the author, "
         "Ithaca, New York)", f"b2812120x_000{n}", year,
         f"Volume {n} of the five-volume textbook by the first director of the New York State Veterinary College, "
         f"covering every domestic animal: {what[0].lower() + what[1:]}.")
    for n, what, year in LAW_VOLUMES
]
PDFS += [
    _old("mayo_diseases_of_animals_1913", "The Diseases of Animals: A Book of Brief and Popular Advice on the Care and "
         "the Common Ailments of Farm Animals (Nelson S. Mayo, 1913 edition)", "Farm animal diseases (old book)",
         "Nelson S. Mayo (Macmillan)", "diseasesofanimal00mayorich", 1913,
         "A plain guide for farmers to keeping horses, cattle, sheep, pigs, dogs and poultry healthy: housing and "
         "feeding, the signs of sickness, nursing, wounds and the common diseases of each animal."),
    _old("hayes_veterinary_notes_horse_owners_1915", "Veterinary Notes for Horse Owners (M. Horace Hayes, 8th edition, "
         "1915)", "Horse care and diseases (old book)", "M. Horace Hayes (Hurst and Blackett, London)",
         "cu31924003264151", 1915,
         "The famous British manual of horse medicine and surgery in plain words: examining a horse, lameness, "
         "wounds, colic and the other diseases, nursing, giving medicines and first aid.",
         country="United Kingdom"),
    _old("moussu_diseases_cattle_sheep_goats_swine_1920", "Diseases of Cattle, Sheep, Goats and Swine (G. Moussu, "
         "translated by John A. W. Dollar, 1920 edition)", "Livestock diseases (old book)",
         "Gustave Moussu, translated and edited by John A. W. Dollar (American Veterinary Publishing Company, "
         "Chicago)", "diseasesofcattle00mous", 1920,
         "A French veterinary professor's textbook in English: the diseases of the digestive, breathing, heart, "
         "urinary and nervous systems, the skin, bones and udder, and the infectious and parasitic diseases of "
         "cattle, sheep, goats and pigs."),
    _old("craig_diseases_of_swine_1906", "Diseases of Swine (Robert A. Craig, 1906)", "Pig diseases (old book)",
         "Robert A. Craig (Breeder's Gazette, Chicago)", "diseasesofswine00crai", 1906,
         "A short book for farmers on keeping pigs healthy: housing and feeding, hog cholera and swine plague, "
         "parasites, and the other common diseases of pigs."),
    _old("salmon_diseases_of_poultry_1899", "The Diseases of Poultry (D. E. Salmon, 1899)",
         "Poultry diseases (old book)", "Daniel Elmer Salmon (George E. Howard, Washington)",
         "diseasesofpoultr00salm", 1899,
         "By the first chief of the USDA Bureau of Animal Industry: the anatomy of the fowl, hygiene and feeding, "
         "and the diseases of chickens, turkeys and other poultry, with their causes, signs and prevention."),
    _old("pearl_diseases_of_poultry_1915", "Diseases of Poultry: Their Etiology, Diagnosis, Treatment and Prevention "
         "(Raymond Pearl, Frank M. Surface and Maynie R. Curtis, 1915)", "Poultry diseases (old book)",
         "Raymond Pearl, Frank M. Surface and Maynie R. Curtis (Macmillan)", "diseasesofpoultr01pear", 1915,
         "A practical book from the Maine Agricultural Experiment Station: the poultry keeper's examination of a "
         "sick bird, sanitation, and the diseases of the breathing, digestion, skin and egg-laying organs, the "
         "infectious diseases and parasites of poultry."),
    _old("randall_practical_shepherd_1864", "The Practical Shepherd: A Complete Treatise on the Breeding, Management "
         "and Diseases of Sheep (Henry S. Randall, 1864)", "Sheep keeping and diseases (old book)",
         "Henry S. Randall (D. D. T. Moore, Rochester, New York)", "cu31924003079450", 1864,
         "The classic American shepherd's book: breeds, breeding, lambing, feeding and shelter through the year, "
         "shearing and wool, and the diseases and parasites of sheep."),
    _old("muller_glass_diseases_of_the_dog_1911", "Diseases of the Dog and Their Treatment (Georg Muller, translated "
         "and edited by Alexander Glass, 1911 edition)", "Dog diseases (old book)",
         "Georg Muller and Alexander Glass (Alexander Eger, Chicago)", "diseasesofdogthe00ml", 1911,
         "A veterinary textbook of the dog's diseases: examining a dog, giving medicines, and the diseases of each "
         "body system, the skin, the eyes and ears, distemper and the other infectious diseases, and parasites."),
    _old("hill_management_and_diseases_of_dog_1888", "The Management and Diseases of the Dog (J. Woodroffe Hill, 1888 "
         "edition)", "Dog care and diseases (old book)", "J. Woodroffe Hill (W. R. Jenkins, New York)",
         "cu31924000940563", 1888,
         "A veterinary surgeon's book on keeping dogs: kennels, feeding and exercise, breeding and puppies, giving "
         "medicines, and the diseases and injuries of dogs."),
    _old("lemmon_training_the_dog_1914", "Training the Dog (Robert S. Lemmon, 1914)", "Dog training (old book)",
         "Robert S. Lemmon (Outing Publishing Company)", "trainingdog00lemm", 1914,
         "A short practical guide to training a dog: the trainer's attitude, house training, coming when called, "
         "heeling, lying down and staying, and curing bad habits.",
         note="Published in {year}: some training methods of its day are harsh; today's trainers use reward-based "
              "methods. Ask a veterinarian or a qualified trainer; old treatments may be harmful."),
    _old("war_office_animal_management_1923", "Animal Management (British War Office, 1923)",
         "Horse and mule care (old book)", "War Office (Great Britain), His Majesty's Stationery Office",
         "animal-management-1923", 1923,
         "The British Army's handbook of horse and mule management: the animal's body, conformation and age by the "
         "teeth, feeding and watering, stable management, grooming, saddlery and harness fitting, shoeing, care on "
         "the march, transport by rail and sea, and the prevention and first aid of disease and injury. Crown "
         "copyright has ended in the UK (50 years after publication), and it is public domain in the US as "
         "published before 1931.", country="United Kingdom"),
    _old("war_office_veterinary_manual_war_1915", "Veterinary Manual (War) (British War Office, 1915)",
         "Army veterinary service (old book)", "War Office (Great Britain), His Majesty's Stationery Office",
         "veterinarymanualwar1915", 1915,
         "The British Army's short veterinary manual for the First World War: caring for horses and mules in the "
         "field, sick lines, contagious diseases and how to keep them from spreading, and the duties of the "
         "veterinary service. Crown copyright has ended in the UK, and it is public domain in the US as published "
         "before 1931.", country="United Kingdom"),
]

# ====================================================================== the index

LIVESTOCK_PACKS = ("pack", "commons_breeds", "Breeds of horses, cattle, pigs, sheep, goats, chickens and other farm "
                                             "animals, for the picture describer")
SECTIONS = [
    ("How to use these books", "Start with the modern government books (APHIS, FDA, CDC and the Yearbooks of "
     "Agriculture), then use the old books for the way animals were kept. Every old book here is history: ask a "
     "veterinarian, because old treatments may be harmful. For a sick animal now, call your veterinarian; for a "
     "disease that may spread, call the state veterinarian.", [
         ("key", "vet:aphis_livestock_poultry_disease", "Livestock and poultry diseases (USDA APHIS)"),
         ("key", "vet:usda_yearbook_1956_animal_diseases", "Animal Diseases (USDA Yearbook 1956)"),
         ("key", "vet:usda_yearbook_1942_keeping_livestock_healthy", "Keeping Livestock Healthy (USDA Yearbook "
                                                                     "1942)"),
         ("word", "animal-care", "Every book of this section (request word)")]),
    ("Horses and mules", "Feeding, stabling, hoofs and shoeing, lameness, colic and the other diseases of horses.", [
        ("key", "vet:usda_special_report_diseases_horse_1923", "Special Report on Diseases of the Horse (USDA, "
                                                                "1923)"),
        ("key", "vet:army_manual_for_stable_sergeants_1917", "Manual for Stable Sergeants (Army, 1917)"),
        ("key", "vet:army_horse_in_accident_and_disease_1909", "The Army Horse in Accident and Disease (1909)"),
        ("key", "vet:army_manual_for_horseshoers_1917", "Manual for Army Horseshoers (1917)"),
        ("key", "vet:hayes_veterinary_notes_horse_owners_1915", "Veterinary Notes for Horse Owners (Hayes, 1915)"),
        ("key", "vet:war_office_animal_management_1923", "Animal Management (British War Office, 1923)"),
        ("key", "vet:war_office_veterinary_manual_war_1915", "Veterinary Manual (War) (1915)"),
        ("key", "hfill:lungwitz_complete_guide_blacksmithing_horseshoeing_1902", "Blacksmithing and horseshoeing "
                                                                                  "(1902)"),
        ("key", "kmil:army_fm_25_7_pack_transportation_1944", "Pack Transportation (FM 25-7, 1944): pack animals"),
        ("key", "kmil:army_manual_pack_transportation_1917", "Manual of Pack Transportation (1917)"),
        ("word", "med:animal", "Horse and pet medicines: the official US animal drug labels")]),
    ("Cattle", "Calving, milk and the udder, bloat, feet, parasites and the infectious diseases of cattle.", [
        ("key", "vet:usda_special_report_diseases_cattle_1942", "Special Report on Diseases of Cattle (USDA, 1942)"),
        ("key", "vet:moussu_diseases_cattle_sheep_goats_swine_1920", "Diseases of Cattle, Sheep, Goats and Swine "
                                                                      "(1920)"),
        ("key", "vet:fda_food_producing_animals", "Medicines for food animals: records and withdrawal times (FDA)"),
        ("key", "apt:pc_animal_traction_1982", "Animal traction: working oxen (Peace Corps)")]),
    ("Sheep and goats", "Lambing and kidding, feet, worms, and the diseases of sheep and goats.", [
        ("key", "vet:randall_practical_shepherd_1864", "The Practical Shepherd (1864)"),
        ("key", "vet:moussu_diseases_cattle_sheep_goats_swine_1920", "Diseases of Cattle, Sheep, Goats and Swine "
                                                                      "(1920)"),
        ("key", "homestead:pegler_book_of_the_goat_1917", "The Book of the Goat (1917)"),
        ("key", "homestead:richards_modern_milk_goats_1921", "Modern Milk Goats (1921)"),
        ("key", "vet:cdc_zoonoses", "Q fever: a disease people catch from sheep and goats at birthing (CDC)")]),
    ("Pigs", "Housing, feeding and the diseases of pigs.", [
        ("key", "vet:craig_diseases_of_swine_1906", "Diseases of Swine (1906)"),
        ("key", "homestead:dietrich_swine_1910", "Swine: Breeding, Feeding and Management (1910)"),
        ("key", "apt:pc_livestock_training_manual_1982", "Livestock: pigs, rabbits, poultry and goats (Peace "
                                                         "Corps)")]),
    ("Chickens and other poultry", "Biosecurity for backyard flocks, bird flu, and the diseases of poultry.", [
        ("key", "vet:aphis_livestock_poultry_disease", "Bird flu and Defend the Flock (APHIS)"),
        ("key", "vet:salmon_diseases_of_poultry_1899", "The Diseases of Poultry (Salmon, 1899)"),
        ("key", "vet:pearl_diseases_of_poultry_1915", "Diseases of Poultry (Pearl, 1915)"),
        ("key", "homestead:lippincott_poultry_production_1921", "Poultry Production (1921)"),
        ("key", "apt:pc_practical_poultry_raising_1981", "Practical Poultry Raising (Peace Corps)"),
        ("pack", "commons_homestead_poultry_bees", "Poultry and bees, for the picture describer")]),
    ("Rabbits", "Keeping rabbits healthy.", [
        ("key", "homestead:practical_rabbit_keeping_1919", "Practical Rabbit Keeping (1919)"),
        ("key", "apt:pc_livestock_training_manual_1982", "Rabbits in the Peace Corps livestock manual")]),
    ("Dogs and cats", "The diseases of dogs and cats, training, and the pet care books.", [
        ("key", "pet:index", "Pet care: a guide to the library"),
        ("key", "pet:fda_pet_health", "Pet food, poisons and pet medicines (FDA)"),
        ("key", "home:aphis_pets", "Pet travel and animals in emergencies (USDA APHIS)"),
        ("key", "vet:army_tm_10_396_war_dogs_1943", "War Dogs (TM 10-396, 1943): kennels, health and training"),
        ("key", "vet:muller_glass_diseases_of_the_dog_1911", "Diseases of the Dog (1911)"),
        ("key", "vet:hill_management_and_diseases_of_dog_1888", "The Management and Diseases of the Dog (1888)"),
        ("key", "vet:lemmon_training_the_dog_1914", "Training the Dog (1914)"),
        ("key", "vision:index", "Guide dogs: in the blind and low-vision living books")]),
    ("Diseases people catch from animals", "Wash your hands after touching animals; wear gloves for sick or dead "
     "animals; see a doctor after a bite or scratch.", [
         ("key", "vet:cdc_zoonoses", "One Health, parrot fever, Q fever, bird flu, toxoplasmosis, ringworm, worms "
                                     "(CDC)"),
         ("key", "pet:cdc_healthy_pets", "Healthy Pets, Healthy People (CDC)"),
         ("key", "firstaid:cdc_bites_ticks", "Animal bites, rabies and ticks (CDC)"),
         ("key", "gamefish:cdc_wild_game_diseases", "Diseases from wild game (CDC)"),
         ("key", "gamefish:aphis_chronic_wasting_disease", "Chronic wasting disease in deer (APHIS)")]),
    ("Old veterinary textbooks (history)", "The great veterinary books before 1931. Ask a veterinarian; old "
     "treatments may be harmful.", [
         *[("key", f"vet:law_text_book_veterinary_medicine_v{n}", f"Law's Text-Book of Veterinary Medicine, "
                                                                   f"volume {n} ({year})")
           for n, _what, year in LAW_VOLUMES],
         ("key", "vet:mayo_diseases_of_animals_1913", "The Diseases of Animals (Mayo, 1913)"),
         ("word", "vet-classics", "Every old veterinary book (request word)")]),
    ("Farm bulletins, medicines and supplies", "Short USDA bulletins, medicine labels and supplies.", [
        ("word", "pub:usda_farmers_bulletins", "USDA Farmers' Bulletins by decade: livestock health, parasites, "
                                               "poultry and more"),
        ("word", "med:animal", "Animal medicine labels"),
        ("word", "service-skills-veterinary", "Army veterinary food inspection courses"),
        ("manuals", "pet_livestock_supplies", "Pet and livestock supplies: makers' manuals"),
        LIVESTOCK_PACKS,
        ("pack", "na_domestic_animals", "Farm and domestic animals"),
        ("pack", "vet_commons_medicine", "Veterinary medicines, ear tags and vet clinics")]),
    ("More animal care sites (links only)", "Copyright: open them in a browser or fetch them with Program "
     "Downloader.", [
         ("link", "Merck Veterinary Manual (consumer and professional versions)", "https://www.merckvetmanual.com/",
          "copyright of Merck and Co."),
         ("link", "American Veterinary Medical Association: animal health and welfare",
          "https://www.avma.org/resources-tools/animal-health-and-welfare", "copyright"),
         ("link", "US state animal health officials (state veterinarians)",
          "https://www.usaha.org/saho", "copyright of the US Animal Health Association"),
         ("link", "Extension Foundation: livestock and poultry", "https://extension.org/",
          "each university's copyright or non-commercial licence"),
         ("link", "Open Textbook Library: agriculture and animal science",
          "https://open.umn.edu/opentextbooks/subjects/agriculture",
          "check each book's licence; non-commercial ones are for personal use")]),
]
INDEX = X.index_maker(PREFIX, GROUP, "Animal care and veterinary books: a guide to the library", "Animal care",
                      "A guide in plain words to caring for farm animals and pets in the library, by animal: horses, "
                      "cattle, sheep and goats, pigs, poultry, rabbits, dogs and cats, with diseases people catch "
                      "from animals, old veterinary textbooks, medicines, supplies and picture packs.", SECTIONS)
MAKERS = {"index": INDEX}


def _keys(names):
    """The index first, then the keys of the named books."""
    return [f"{PREFIX}:index"] + [f"{PREFIX}:{n}" for n in names]


ALL = [g["name"] for g in GUIDES] + [p["name"] for p in PDFS]
OLD = [p["name"] for p in PDFS if p.get("old_public_domain") and not p.get("military")]
PETS = ["cdc_zoonoses", "army_tm_10_396_war_dogs_1943", "muller_glass_diseases_of_the_dog_1911",
        "hill_management_and_diseases_of_dog_1888", "lemmon_training_the_dog_1914"]
LIVESTOCK = [n for n in ALL if n not in PETS or n == "cdc_zoonoses"]
WORDS = {"animal-care": lambda: _keys(ALL), "vet-livestock": lambda: _keys(LIVESTOCK),
         "vet-pets": lambda: _keys(PETS), "vet-classics": lambda: _keys(OLD)}

COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "vet_aphis_fda_cdc": "aphis.usda.gov (a work of the US government, 17 U.S.C. 105, checked on govinfo.gov's "
                         "policies page at every build), FDA's website policy (\"in the public domain and may be "
                         "republished\") and CDC's terms (www.cdc.gov/other/agencymaterials.html; the pages kept "
                         "whole), each checked at every build; robots.txt allows the pages, no AI rules; small "
                         "test builds read all three (2026-11-23).",
    "vet_usda_army": "Internet Archive copies of USDA Bureau of Animal Industry reports and Yearbooks of Agriculture "
                     "(the National Agricultural Library's scans) and US Army manuals: works of the US government "
                     "(17 U.S.C. 105); the Army manuals are judged at every build by the release rule "
                     "(military_release.py); archive.org's robots.txt allows the files (checked 2026-11-23).",
    "vet_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build); "
                     "Hayes and the two War Office manuals are British, public domain in the US as published before "
                     "1931 (and the War Office's Crown copyright has ended in the UK).",
    "vet_index": "The index (vet:index) is the toolkit's own facts and links, CC0.",
}

NOT_INCLUDED = [
    ("Merck Veterinary Manual, AVMA, ASPCA and university extension animal health guides", "Copyright of each "
     "publisher, or non-commercial licences not confirmed one by one; link-only from vet:index. Index: "
     "https://www.merckvetmanual.com/"),
    ("Special Report on Diseases of the Horse, 1942 edition", "The Internet Archive's copy is a lending-library scan "
     "that cannot be downloaded (bwb_S0-DFU-707); the 1923 edition is built (vet:usda_special_report_diseases_horse_"
     "1923). Index: https://archive.org/search?query=%22special+report+on+diseases+of+the+horse%22"),
    ("Special Report on Diseases of Cattle, other editions (1892 to 1923), and Diseases of the Horse before 1923",
     "The same book revised; the newest downloadable edition of each is built. Index: "
     "https://archive.org/search?query=%22special+report+on+diseases+of+cattle%22"),
    ("USDA Farmers' Bulletins on livestock diseases (Diseases of Swine, Parasites and Parasitic Diseases of Sheep, "
     "Diseases of Poultry and others)", "Already in the library by decade (pub:usda_farmers_bulletins, from the "
     "National Agricultural Library's collection usda-farmersbulletin); not built again. Index: "
     "https://archive.org/details/usda-farmersbulletin"),
    ("Hamilton Kirk's books on dogs and cats (Index of Diagnosis, Diseases of the Cat, 1925 and later)", "No "
     "downloadable Internet Archive copy was found (searched 2026-11-23); Surgical Diseases of the Dog and Cat (1924) "
     "is a lending-library scan, and editions after 1930 may still be in copyright. Index: "
     "https://archive.org/search?query=surgical+diseases+of+the+dog+and+cat"),
    ("Hayes's Veterinary Notes for Horse Owners, editions after 1930", "Later revisions (1924 lending copy, 1964 and "
     "later) are lending-library scans or still in copyright; the 1915 edition is built. Index: "
     "https://archive.org/search?query=%22veterinary+notes+for+horse+owners%22"),
    ("Army veterinary and animal care manuals after 1945 (FM 4-02.18 Veterinary Service, TB MED 283 working dog "
     "necropsy, the animal care specialist courses)", "Their downloadable copies found are about food inspection (built as "
     "service-skills-veterinary), veterinary administration or necropsy for pathologists, not animal care for "
     "keepers; not built. Index: https://archive.org/search?query=%22military+working+dog%22"),
    ("CDC and APHIS pages already in other books", "Rabies, ticks and Lyme disease (firstaid:cdc_bites_ticks), "
     "brucellosis, tularemia and chronic wasting disease (gamefish:), leptospirosis, hantavirus and plague "
     "(rmed:), Healthy Pets (pet:cdc_healthy_pets) and APHIS pet travel (home:aphis_pets); not read twice. Index: "
     "https://www.cdc.gov/one-health/"),
    ("Guide dog and service dog care", "Left to the blind and low-vision living books (vision:), as the owner "
     "asked. Index: https://www.ada.gov/topics/service-animals/"),
    ("Openly licensed veterinary and animal science textbooks (OER)", "None with a licence the toolkit may "
     "repackage (CC0, CC BY) was confirmed in this pass; non-commercial ones are for personal use: link-only from "
     "vet:index. Index: https://open.umn.edu/opentextbooks/subjects/agriculture"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
