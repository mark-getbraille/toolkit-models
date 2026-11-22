"""Parenting and family resources for the reference library, in the group "Reference, parenting and family" (the
owner's request of 2026-11-22). Keys: parenting (every book), parent:<name>.

What this module builds, in plain words, each IN FULL (every page of the guide, read from the publisher's own site):
  - CDC's parenting pages, kept whole with their text unchanged as CDC's terms ask: Positive Parenting Tips by age,
    the Essentials for Parenting toddlers and teens, CDC's parent information by age (infants, children, teens)
    and the child development pages; the childhood vaccine pages for parents with the child and teen immunization
    schedules (the easy-to-read one for parents and the official one with its notes); children's mental health
    and adverse childhood experiences; and the injury pages for children (car seats and child passenger safety,
    drowning, teen drivers, child abuse and neglect prevention).
  (The family health books already in family_health.py, CDC's Learn the Signs. Act Early., Safe to Sleep and the
  crisis lines, are not repeated here.)

Licences: works of the US government (17 U.S.C. 105); CDC's "Use of Agency Materials" page is checked at every
build for its public-domain line, and its conditions (credit CDC, no endorsement, no change to the substance, say
it is free on CDC's site) are met in the notice; the pages are kept whole.

Run from the repository's folder:
  python3 textbooks/parenting.py parent:cdc_parenting --out build/textbooks --limit 5
  python3 textbooks/parenting.py --list parenting
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402

GROUP = "parenting"
GROUPS = {GROUP: "Reference, parenting and family"}

# CDC's terms (the same as family_health.py): checked at every build, kept whole, credit and no-endorsement notice.
CDC_TERMS = "https://www.cdc.gov/other/agencymaterials.html"
CDC_TEXT = r"Most of the information on the CDC and ATSDR websites is not subject to copyright, is in the public domain"
CDC_NOTICE = ("Source: CDC (Centers for Disease Control and Prevention). Materials developed by CDC; this material is "
              "available free of charge on www.cdc.gov. Reference to specific commercial products, manufacturers, "
              "companies, or trademarks does not constitute its endorsement or recommendation by the U.S. Government, "
              "Department of Health and Human Services, or Centers for Disease Control and Prevention, and this copy "
              "does not imply their endorsement of GetBraille.com or the toolkit. Kept whole with its text unchanged.")
NOT_MEDICAL = "Health information, not medical advice: talk with your child's doctor or nurse."
CDC_PUBLISHER = "Centers for Disease Control and Prevention (CDC)"


def cdc_sites(sites, extra=""):
    """The page pattern of one or more CDC sites (the folder names, such as "parents"): every .html page under them
    except the Spanish copies, the media files and the site index itself; extra: more addresses (a pattern) to
    keep."""
    alt = "|".join(sites)
    own = rf"https://www\.cdc\.gov/({alt})/(?!es/|media/|site\.html)[a-z0-9-]+(/[a-z0-9-]+)*\.html"
    return rf"^({own}{'|' + extra if extra else ''})$"


def cdc_book(name, title, subject, sites, description, units, urls=(), extra="", limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html", which lists every
    page of the site), kept whole under CDC's terms."""
    entry = K.guide(GROUP, name, title, subject, CDC_PUBLISHER,
                    [f"https://www.cdc.gov/{s}/site.html" for s in sites], cdc_sites(sites, extra), description,
                    CDC_NOTICE + " " + NOT_MEDICAL, depth=1, units=units, limit=limit)
    entry["urls"] = list(urls)
    return dict(entry, licence_page=CDC_TERMS, licence_text=CDC_TEXT, unchanged=True)


IMZ = "https://www.cdc.gov/vaccines/hcp/imz-schedules/"
GUIDES = [
    cdc_book("cdc_parenting", "Positive parenting and Essentials for Parenting (CDC)", "Parenting",
             ["child-development", "parents", "parenting-toddlers", "parenting-teens"],
             "CDC's pages for parents, every page: Positive Parenting Tips for each age (infants, toddlers 1 to 2 "
             "and 2 to 3, preschoolers, middle childhood and teens), the Essentials for Parenting toddlers and "
             "preschoolers (communicating, structure and rules, noticing and naming feelings, responding to "
             "behaviour, time-outs) and teens, CDC's parent information by age (infants, children and teens: "
             "health, safety, milestones and conditions), and the child development pages (developmental "
             "disabilities, safety for children with disabilities).",
             units=[(r"/positive-parenting-tips/", "Positive Parenting Tips"),
                    (r"/parenting-toddlers/", "Essentials for Parenting Toddlers and Preschoolers"),
                    (r"/parenting-teens/", "Essentials for Parenting Teens"), (r"/parents/", "Parent information"),
                    (r".", "Child development")],
             urls=["https://www.cdc.gov/child-development/positive-parenting-tips/index.html"]),
    cdc_book("cdc_child_vaccines", "Vaccines for your children and the immunization schedules (CDC)",
             "Childhood vaccines", ["vaccines-children"],
             "CDC's childhood vaccine pages for parents, every page (why vaccines matter, the diseases they "
             "prevent, before, during and after shots, keeping records, travel and when your child is sick), with "
             "the easy-to-read immunization schedule for parents and the official child and adolescent "
             "immunization schedule (by age, catch-up, by medical condition, its notes, appendix and addendum).",
             units=[(r"/imz-schedules/", "Immunization schedules"), (r".", "Vaccines for your children")],
             urls=["https://www.cdc.gov/vaccines/imz-schedules/child-easyread.html"] +
                  [IMZ + p for p in ("child-adolescent-age.html", "child-adolescent-catch-up.html",
                                     "child-adolescent-medical-indication.html", "child-adolescent-notes.html",
                                     "child-adolescent-appendix.html", "child-adolescent-addendum.html")],
             extra=r"https://www\.cdc\.gov/vaccines/(hcp/)?imz-schedules/child-[a-z-]+\.html"),
    cdc_book("cdc_children_mental_health", "Children's mental health and adverse childhood experiences (CDC)",
             "Children's mental health", ["children-mental-health", "aces"],
             "CDC's children's mental health pages, every page (anxiety and depression, behaviour and conduct "
             "problems, obsessive-compulsive disorder, post-traumatic stress disorder, treatment and getting help, "
             "data), and the pages on adverse childhood experiences (ACEs) and how to prevent them.",
             units=[(r"/aces/", "Adverse childhood experiences"), (r".", "Children's mental health")]),
    cdc_book("cdc_child_safety", "Keeping children safe: car seats, drowning, teen drivers and abuse prevention (CDC)",
             "Child injury prevention", ["child-passenger-safety", "drowning", "teen-drivers", "child-abuse-neglect"],
             "CDC's injury prevention pages for children and teens, every page: child passenger safety (car "
             "seats, booster seats and seat belts by age), drowning prevention (water safety, swimming skills, "
             "pools and bathtubs), teen drivers (risk factors, graduated licensing, parents' role) and child abuse "
             "and neglect prevention (risk and protective factors, what parents and communities can do).",
             units=[(r"/child-passenger-safety/", "Child passenger safety"), (r"/drowning/", "Drowning prevention"),
                    (r"/teen-drivers/", "Teen drivers"), (r".", "Child abuse and neglect prevention")]),
]

COLLECTION = K.Collection("parent", GROUP, guides=GUIDES,
                          words={"parenting": lambda: [f"parent:{g['name']}" for g in GUIDES]})

LICENCE_LINES = {
    "parenting_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                     "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on "
                     "CDC's site), met in each CDC book's notice; the pages are kept whole. www.cdc.gov's robots.txt "
                     "allows the pages; no AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = []


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
