"""Pets, and home and garden safety, for the reference library (the owner's requests of 2026-11-22). Keys: pets-home
(every book), home:<name>.

What this module builds, in plain words, each IN FULL:
  - USDA APHIS's pet pages: pet travel (taking a pet to another country, bringing a dog or cat into the US, moving
    between states, pets on planes, accredited veterinarians), animals in emergencies and disasters, and the animal
    welfare resources for owners;
  - the EPA's home guides on mould, radon, lead (in paint, dust, soil and water; renovating safely) and indoor air
    quality, marked "personal use only": the EPA's copyright statement says its documents "may be freely
    distributed and used for non-commercial, scientific and educational purposes" and that commercial use "may be
    protected", so these books are for the owner's own reading, not to be sold.

Not built (NOT_INCLUDED): AVMA's pet care pages ("© American Veterinary Medical Association, All rights reserved")
and university extension garden guides (the services checked say "All rights reserved", or shut out AI readers);
link-only for the personal assistant.

Licences: APHIS pages are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies
page at every build); the EPA's copyright statement is checked on its disclaimer page at every build. robots.txt of
aphis.usda.gov and epa.gov allows the pages; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/pets_home.py home:aphis_pets --out build/textbooks --limit 5
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "health"
EPA_TERMS = "EPA website copyright statement"
ALLOWED = {EPA_TERMS: "non-commercial"}
EPA_DISCLAIMER = "https://www.epa.gov/web-policies-and-procedures/epa-disclaimers"
EPA_TEXT = r"These documents may be freely distributed and used for non-commercial, scientific and educational purposes"
EPA_NOTICE = ("From the US Environmental Protection Agency. Personal use only: EPA says its documents \"may be freely "
              "distributed and used for non-commercial, scientific and educational purposes\". For testing or "
              "repairs, use a certified professional where EPA says to.")
EPA_TOPICS = "mold|radon|lead|indoor-air-quality-iaq"

GUIDES = [
    K.guide(GROUP, "aphis_pets", "Pets: travel, emergencies and welfare (USDA APHIS)", "Pets and pet travel",
            "Animal and Plant Health Inspection Service (APHIS), US Department of Agriculture",
            ["https://www.aphis.usda.gov/pet-travel", "https://www.aphis.usda.gov/animal-emergencies",
             "https://www.aphis.usda.gov/animal-care/animal-welfare-resources"],
            r"^https://www\.aphis\.usda\.gov/(pet-travel|animal-emergencies|animal-care/animal-welfare-resources)"
            r"(/[a-z0-9-]+)*$",
            "USDA APHIS's pages for pet owners: pet travel from the US to another country (country by country "
            "requirements), bringing a dog, cat or other pet into the US, travelling between states, pets on planes "
            "and accredited veterinarians; caring for animals in emergencies and disasters; and the animal welfare "
            "resources.",
            "A work of the US Department of Agriculture (public domain). Pet travel rules change: check APHIS's "
            "pet travel site and your veterinarian before you travel.", depth=2,
            follow=r"^https://www\.aphis\.usda\.gov/pet-travel/[a-z0-9-]+$",
            units=[(r"/pet-travel", "Pet travel"), (r"/animal-emergencies", "Animals in emergencies"),
                   (r".", "Animal welfare")], limit=300),
    dict(K.guide(GROUP, "epa_home_health", "Mould, radon, lead and indoor air at home (EPA)",
                 "Home health (mould, radon, lead, indoor air)", "US Environmental Protection Agency (EPA)",
                 [f"https://www.epa.gov/{t}" for t in EPA_TOPICS.split("|")],
                 rf"^https://www\.epa\.gov/({EPA_TOPICS})(/[a-z0-9-]+)*$",
                 "The EPA's guides for homes: mould (cleaning up, moisture control, after floods), radon (what it is, "
                 "testing, fixing, the citizen's guide and buying or selling a home), lead (in paint, dust and soil, "
                 "drinking water, renovating safely, protecting children) and indoor air quality (pollutants and "
                 "sources, ventilation, air cleaners, and indoor air in homes, schools and offices).", EPA_NOTICE,
                 depth=2, follow=rf"^https://www\.epa\.gov/({EPA_TOPICS})/[a-z0-9-]+$",
                 units=[(r"/mold", "Mould"), (r"/radon", "Radon"), (r"/lead", "Lead"), (r".", "Indoor air quality")],
                 limit=300),
         licence=EPA_TERMS, licence_url=EPA_DISCLAIMER, licence_page=EPA_DISCLAIMER, licence_text=EPA_TEXT,
         personal_use=True),
]

COLLECTION = K.Collection("home", GROUP, guides=GUIDES,
                          words={"pets-home": lambda: [f"home:{g['name']}" for g in GUIDES]})

GROUPS = {}
LICENCE_LINES = {
    "aphis_pets": "aphis.usda.gov: works of the US government (17 U.S.C. 105, checked on govinfo.gov's policies page "
                  "at every build); robots.txt allows the pages; no AI rules (checked 2026-11-22).",
    "epa_home_health": "epa.gov/web-policies-and-procedures/epa-disclaimers (checked at every build): \"These "
                       "documents may be freely distributed and used for non-commercial, scientific and educational "
                       "purposes. Commercial use of the documents available from the EPA websites may be protected\". "
                       "So the EPA books are marked personal use only (not for commercial use).",
}
NOT_INCLUDED = [
    ("AVMA pet care pages (American Veterinary Medical Association)", "\"© American Veterinary Medical Association. "
     "All rights reserved\" (checked 2026-11-22). Link-only for the personal assistant. Index: "
     "https://www.avma.org/resources-tools/pet-owners"),
    ("University extension garden guides (Minnesota, Virginia Tech, Georgia, UC IPM, Oregon State, Florida EDIS)",
     "Minnesota, Virginia Tech, Georgia and UC IPM say \"All rights reserved\" or copyright the Regents; Oregon State's "
     "catalogue shuts out AI readers; Florida's EDIS now forwards to its question site (checked 2026-11-22). No "
     "openly licensed extension garden collection was found. Link-only. Index: https://extension.umn.edu/"
     "garden-and-home/yard-and-garden and https://www.pubs.ext.vt.edu/"),
    ("APHIS animal care regulations and inspection pages", "Left out: they are about licensing dealers, breeders and "
     "research facilities, not pet care; the Animal Welfare Act rules are 9 CFR parts 1 to 3. Index: "
     "https://www.aphis.usda.gov/animal-care"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
