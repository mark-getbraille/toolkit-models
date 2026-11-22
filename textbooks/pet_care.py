"""Pet care for the reference library, in its own group "Reference, pet care" (the owner's request of 2026-11-22):
dogs, cats, small pets, birds, fish and reptiles. Keys: pet-care (every book), pet:<name>.

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - CDC's Healthy Pets, Healthy People pages, every page: choosing and caring for dogs, cats, birds, fish, reptiles
    and amphibians, small mammals, ferrets, backyard poultry and horses; pet food safety; diseases people can catch
    from pets and how to prevent them; cleaning pet supplies; pets and travel; a pet preparedness kit and pets in
    evacuation centres. Kept whole with their text unchanged, as CDC's terms ask;
  - the FDA Center for Veterinary Medicine's animal health pages for pet owners, every page: pet food and treats
    (labels, raw food, recalls, how to report a problem), dangers to pets (chocolate, xylitol, lilies and cats,
    human medicines, vitamin D, snack bags, holidays, smoke), pet medicines (flea and tick products, heartworm,
    giving medicines safely) and other pet health topics, and who to call in a pet emergency;
  - seven old public-domain pet books (published before 1931) from the Internet Archive, each with a note on what is
    out of date: Your Dog and Your Cat (Spaulding, 1921), The Complete Dog Book (Bruette, 1921), The Care and
    Handling of Dogs (Leonard, 1928), The Cat (Huidekoper, 1895), Feeding and Care of the Domestic and Long-Haired Cat
    (1922), The Aquarium Book (Boulenger, 1927) and Foreign Birds for Cage and Aviary (Butler, 1908);
  - pet:index, a guide to pet care in the library, part by part (dogs, cats, small pets, birds, fish and reptiles,
    feeding, vaccines and the vet, spaying and neutering, first aid and poisons, travel, disasters, pet loss, guide
    and service dogs), with the books by key, the animal medicine labels, the breed picture pack, the pet supplies
    manuals and the copyright sources as links.

Already in the library and linked from the index, not repeated: USDA APHIS's pet travel, animals in emergencies and
animal welfare pages (home:aphis_pets), the animal medicine labels (med:animal), the old livestock books
(homestead), the breed picture pack (commons_breeds) and the pet and livestock supplies manuals.

Every book's notice ends with the pet note: information, not veterinary advice; ask a veterinarian, and if a pet may
have eaten something poisonous, call a veterinarian or an animal poison control centre at once.

Not built (NOT_INCLUDED, link-only): AVMA, ASPCA (and its poison control centre), the AKC, the Humane Society, and
university extension pet guides (copyright), NIH News in Health (no reuse statement found on its pages), and the
modern guide dog schools' handbooks (copyright).

Licences: CDC's terms and FDA's website policy are checked at every build and their conditions met in the notice;
the old books' Internet Archive records must show a date before 1931 (checked at every build).

Run from the repository's folder:
  python3 textbooks/pet_care.py pet:fda_pet_health --out build/textbooks --limit 5
  python3 textbooks/pet_care.py --list pet-care
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import mental_health as M  # noqa: E402 - the shared CDC book helper
import practical_index as X  # noqa: E402 - the index maker
from old_ia_books import old_book  # noqa: E402

GROUP = "petcare"
GROUPS = {GROUP: "Reference, pet care"}
NOTE = ("Information, not veterinary advice: ask a veterinarian. If a pet may have eaten something poisonous, call "
        "your veterinarian or an animal poison control centre at once.")
OLD_NOTE = ("Published in {year}: an old book whose medicines, vaccines, foods and some training methods are out of "
            "date (it was written before modern vaccines and flea, tick and worm treatments). Ask a veterinarian, and "
            "use the CDC and FDA books for current advice.")

FDA = "https://www.fda.gov"
FDA_POLICY = FDA + "/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished"
FDA_LIT = FDA + "/animal-veterinary/animal-health-literacy"
FDA_HUBS = [FDA + "/animal-veterinary/resources-you/animal-health-literacy"] + [
    f"{FDA_LIT}/{p}" for p in ("pet-food-and-treats", "dangers-pets", "pet-meds", "other-pet-health-topics")]

GUIDES = [
    M.cdc_book(GROUP, "cdc_healthy_pets", "Healthy Pets, Healthy People: caring for pets and staying healthy (CDC)",
               "Pet care and health", ["healthy-pets"],
               "CDC's Healthy Pets pages, every page: dogs, cats, birds, fish, reptiles and amphibians, small mammals "
               "(hamsters, guinea pigs, rabbits, mice and rats), ferrets, backyard poultry and horses (choosing a pet, "
               "keeping it healthy, and the germs it can carry); pet food safety; diseases from pets and how to "
               "prevent them; cleaning and disinfecting pet supplies; travelling with pets; a pet preparedness kit "
               "and pets in evacuation centres; staying healthy at animal exhibits.",
               units=[(r"/about/", "Pets, one kind at a time"), (r"/emergency-preparedness/", "Pets in emergencies"),
                      (r"/rodent-control/", "Keeping rodents out"), (r".", "Pets and your health")], note=NOTE),
    dict(K.guide(GROUP, "fda_pet_health", "Pet food, poisons and pet medicines (FDA Center for Veterinary Medicine)",
                 "Pet food, poisons and medicines", "Center for Veterinary Medicine, US Food and Drug Administration "
                 "(FDA)", FDA_HUBS,
                 rf"^{FDA_LIT.replace('.', chr(92) + '.')}/(?!cvm-kids-page$|food-producing-animals)[a-z0-9-]+$",
                 "The FDA's animal health pages for pet owners, every page: pet food and treats (reading the label, "
                 "raw pet food, grain-free diets, recalls, how to report a problem with a pet food), dangers to pets "
                 "(chocolate, xylitol, lilies and cats, people's medicines and creams, vitamin D, snack bags, "
                 "holiday hazards, second-hand smoke, disasters and hurricanes), pet medicines (flea and tick "
                 "products, heartworm, giving medicines safely, buying them online) and who to call in a pet "
                 "emergency.",
                 f"From the US Food and Drug Administration: FDA's web pages \"are in the public domain and may be "
                 f"republished\"; credit to the FDA, with no endorsement implied. {NOTE}", depth=1, limit=80,
                 units=[(r"food|treat|diet|raw", "Pet food and treats"),
                        (r"medic|meds|flea|tick|heartworm|drug", "Pet medicines"),
                        (r".", "Dangers to pets and other health topics")]),
         licence_page=FDA_POLICY, licence_text=FDA_TEXT),
]


def _old(name, title, subject, publisher, archive, year, description, note=OLD_NOTE, country="United States"):
    """One old public-domain pet book (published before 1931) with the out-of-date note and the pet note."""
    return old_book(GROUP, name, title, subject, publisher, archive, year, description, note=note, notice=NOTE,
                    country=country)


PDFS = [
    _old("spaulding_your_dog_and_your_cat_1921", "Your Dog and Your Cat: How to Care for Them (Spaulding, 1921)",
         "Dog and cat care", "Roy Henry Spaulding (D. Appleton and Company)", "yourdogyourcatho00spau", 1921,
         "A veterinarian's book on caring for dogs and cats in health and sickness: choosing a pet, feeding, "
         "housing, grooming, exercise, training and common illnesses, and when to call the veterinarian."),
    _old("bruette_complete_dog_book_1921", "The Complete Dog Book (Bruette, 1921)", "Dog care",
         "William A. Bruette (Stewart Kidd Company)", "completedogbook00brue", 1921,
         "A whole book of dog keeping: the breeds of the day, choosing a puppy, feeding, kennels, grooming, "
         "training and the dog's diseases."),
    _old("leonard_care_and_handling_of_dogs_1928", "The Care and Handling of Dogs (Leonard, 1928)", "Dog care",
         "John Lynn Leonard (Doubleday, Doran and Company)", "carehandlingofdo00leon", 1928,
         "A veterinarian's practical guide to raising and keeping dogs: puppies, feeding, housing, grooming, "
         "house training and obedience, and first aid and nursing at home."),
    _old("huidekoper_the_cat_1895", "The Cat: A Guide to the Classification and Varieties of Cats (Huidekoper, "
         "1895)", "Cat care", "Rush Shippen Huidekoper (D. Appleton and Company)", "catguidetoclassi00huidrich", 1895,
         "A veterinarian's book on cats: the kinds and varieties of cats of the time, and a short treatise on "
         "their care and diseases."),
    _old("feeding_care_domestic_long_haired_cat_1922", "Feeding and Care of the Domestic and Long-Haired Cat (1922)",
         "Cat care", "Ellen V. Celty and Anna Ray (F. B. Harrison Printing Company)", "feedingcareofdom00celt", 1922,
         "A short booklet on feeding cats and kittens, grooming long-haired cats, and keeping a cat healthy."),
    _old("boulenger_aquarium_book_1927", "The Aquarium Book (Boulenger, 1927)", "Fish keeping",
         "E. G. Boulenger (Duckworth, London)", "aquariumbook00boul", 1927,
         "Keeping fish and other water animals at home, by the curator of the London Zoo's aquarium: setting up "
         "tanks for fresh and salt water, plants, feeding, and the fish suited to them.",
         note=OLD_NOTE + " Its heating and filtering equipment is that of 1927.", country="United Kingdom"),
    _old("butler_foreign_birds_cage_aviary_1908", "Foreign Birds for Cage and Aviary (Butler, 1908)", "Cage birds",
         "Arthur G. Butler", "foreignbirdsforc0000arth", 1908,
         "Keeping finches, parakeets and other birds from abroad in cages and aviaries: housing, feeding and care. "
         "Many birds it names were wild-caught then; buying a wild-caught bird may now be against the law.",
         country="United Kingdom"),
]

# ====================================================================== the index

SECTIONS = [
    ("Dogs", "Feeding, housing, grooming, training and health.", [
        ("key", "pet:cdc_healthy_pets", "Dogs and your health (CDC Healthy Pets: the dogs page)"),
        ("key", "pet:spaulding_your_dog_and_your_cat_1921", "Your Dog and Your Cat (1921)"),
        ("key", "pet:bruette_complete_dog_book_1921", "The Complete Dog Book (1921)"),
        ("key", "pet:leonard_care_and_handling_of_dogs_1928", "The Care and Handling of Dogs (1928): training and "
                                                               "first aid"),
        ("pack", "commons_breeds", "Dog, cat and horse breeds, for the picture describer")]),
    ("Cats", "Feeding, litter, grooming and health.", [
        ("key", "pet:cdc_healthy_pets", "Cats and your health (CDC Healthy Pets: the cats page)"),
        ("key", "pet:huidekoper_the_cat_1895", "The Cat (1895)"),
        ("key", "pet:feeding_care_domestic_long_haired_cat_1922", "Feeding and Care of the Domestic and Long-Haired "
                                                                  "Cat (1922)"),
        ("key", "pet:fda_pet_health", "Lilies are deadly to cats (FDA)")]),
    ("Small pets, birds, fish and reptiles", "Hamsters, guinea pigs, rabbits, ferrets, birds, fish, reptiles and "
     "amphibians, and backyard poultry.", [
         ("key", "pet:cdc_healthy_pets", "CDC Healthy Pets: small mammals, ferrets, birds, fish, reptiles and "
                                         "amphibians, backyard poultry"),
         ("key", "pet:boulenger_aquarium_book_1927", "The Aquarium Book (1927)"),
         ("key", "pet:butler_foreign_birds_cage_aviary_1908", "Foreign Birds for Cage and Aviary (1908)"),
         ("key", "homestead:practical_rabbit_keeping_1919", "Practical Rabbit Keeping (1919)"),
         ("word", "homestead", "Chickens, ducks, goats and other small livestock (request word)")]),
    ("Feeding and pet food", "Pet food labels, raw food, treats, recalls and storing food safely.", [
        ("key", "pet:fda_pet_health", "Pet food and treats (FDA Center for Veterinary Medicine)"),
        ("key", "pet:cdc_healthy_pets", "Pet food safety (CDC)"),
        ("word", "recalls", "FDA recalls, pet food included (request word)")]),
    ("Vaccines, the vet, spaying and neutering, medicines", "Vaccines, worms, fleas and ticks, giving medicines and "
     "the official labels of pet medicines. Ask your veterinarian about vaccines and about spaying or neutering.", [
         ("key", "pet:fda_pet_health", "Pet medicines: flea and tick products, heartworm (FDA)"),
         ("word", "med:animal", "Pet and horse medicines: the official US animal drug labels"),
         ("link", "AVMA: pet owners' pages (vaccinations, spaying and neutering, choosing a veterinarian)",
          "https://www.avma.org/resources-tools/pet-owners", "the American Veterinary Medical Association's "
          "copyright; open it in a browser")]),
    ("First aid and poisons", "Foods, plants, medicines and products that are dangerous to pets, and what to do.", [
        ("key", "pet:fda_pet_health", "Dangers to pets and who to call in a pet emergency (FDA)"),
        ("key", "pet:leonard_care_and_handling_of_dogs_1928", "First aid and nursing (1928; old methods)"),
        ("link", "ASPCA Animal Poison Control Center", "https://www.aspca.org/pet-care/animal-poison-control",
         "the ASPCA's copyright; open it in a browser (it lists its own phone number and fee)"),
        ("link", "AVMA: pet first aid", "https://www.avma.org/resources-tools/pet-owners/emergencycare",
         "copyright; open it in a browser")]),
    ("Travelling with pets and disasters", "Taking a pet to another country or state, on a plane, and in an "
     "emergency.", [
         ("key", "home:aphis_pets", "Pet travel, animals in emergencies and animal welfare (USDA APHIS)"),
         ("key", "pet:cdc_healthy_pets", "Travelling with pets, a pet preparedness kit and pets in evacuation "
                                         "centres (CDC)")]),
    ("Pet loss", "Saying goodbye to a pet, and grief.", [
        ("link", "AVMA: euthanasia and pet loss", "https://www.avma.org/resources-tools/pet-owners/petcare/"
         "euthanasia-final-goodbye", "copyright; open it in a browser"),
        ("word", "mental-health", "Grief and loss in the mental health books (request word)")]),
    ("Guide dogs and service dogs", "Caring for a guide or service dog, and the rights of people who use one.", [
        ("key", "vision:index", "Blind and low-vision living: orientation and mobility, guide dogs"),
        ("word", "vision-living", "The vision section's books (request word)"),
        ("link", "ADA: service animals (US Department of Justice)", "https://www.ada.gov/topics/service-animals/",
         "a US government page; open it in a browser"),
        ("link", "Guide dog schools (Guide Dogs for the Blind, The Seeing Eye and others)",
         "https://www.guidedogs.com/", "the schools' copyright; open them in a browser")]),
    ("Pet supplies and breeds", "The makers' instructions for crates, aquariums, feeders, clippers and more.", [
        ("manuals", "pet_livestock_supplies", "Pet and livestock supplies: makers' manuals, as links"),
        ("pack", "commons_breeds", "Breeds of dogs, cats, horses and other animals")]),
    ("More pet care sites (links only)", "Copyright: open them in a browser or fetch them with Program Downloader.", [
        ("link", "ASPCA: general pet care", "https://www.aspca.org/pet-care", "copyright"),
        ("link", "American Kennel Club: dog care and training", "https://www.akc.org/expert-advice/",
         "copyright"),
        ("link", "The Humane Society of the United States: pet care", "https://www.humaneworld.org/en/pets",
         "copyright")]),
]
INDEX = X.index_maker("pet", GROUP, "Pet care: a guide to the library", "Pet care",
                      "A guide to pet care in the library: dogs, cats, small pets, birds, fish and reptiles, feeding, "
                      "the vet and medicines, first aid and poisons, travel and disasters, pet loss, guide and service "
                      "dogs, supplies and breeds.", SECTIONS)
MAKERS = {"index": INDEX}

COLLECTION = K.Collection("pet", GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS,
                          words={"pet-care": lambda: ["pet:index"] + [f"pet:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "pet_cdc_fda": "CDC's terms (www.cdc.gov/other/agencymaterials.html, as mind_cdc; the pages kept whole) and FDA's "
                   "website policy (\"in the public domain and may be republished\"), both checked at every build; "
                   "robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "pet_old_books": "Internet Archive items: each item's metadata \"date\" before 1931 (checked at every build); "
                     "The Aquarium Book and Foreign Birds are British books, public domain in the US as published "
                     "before 1931.",
    "pet_index": "The index (pet:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("AVMA, ASPCA (with the Animal Poison Control Center), American Kennel Club and Humane Society pet care pages",
     "Copyright of each organisation (\"All rights reserved\"); link-only from the index (pet:index). Index: "
     "https://www.aspca.org/pet-care and https://www.akc.org/expert-advice/"),
    ("University extension pet care guides", "Each university's copyright, or non-commercial licences; none was "
     "confirmed open one by one, so they are link-only. Index: https://extension.org/"),
    ("NIH News in Health articles on pets (\"The Power of Pets\")", "A US government work, but no reuse statement was "
     "found on its pages and the library's periodicals collection found it refusing programs before; link-only. "
     "Index: https://newsinhealth.nih.gov/2018/02/power-pets"),
    ("Guide dog schools' handbooks (Guide Dogs for the Blind, The Seeing Eye, Guiding Eyes, Leader Dogs)",
     "Copyright of each school; link-only, from the index's guide dog part. Index: https://www.guidedogs.com/"),
    ("USDA APHIS pet travel and animal welfare pages", "Already built in full (home:aphis_pets); linked, not "
     "repeated. Index: https://www.aphis.usda.gov/pet-travel"),
    ("Pet supplies manuals", "Already a manual collection (pet_livestock_supplies: crates, aquariums, feeders, "
     "fountains, clippers, pet doors, collars); not repeated. Index: https://www.petsafe.com/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
