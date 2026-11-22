"""Communication and relationships for the reference library, in its own group "Reference, communication and
relationships" (the owner's request of 2026-11-22). Keys: relationships (every book), relate:<name>.

What this module builds, in plain words, each IN FULL:
  - CDC's intimate partner violence pages: what healthy and unhealthy relationships look like, the warning signs and
    kinds of abuse (physical, sexual, emotional and psychological, stalking), teen dating violence, risk and
    protective factors, prevention, and CDC's Dating Matters programme for building healthy teen relationships;
  - youth.gov's teen dating violence and bullying pages (the federal Interagency Working Group on Youth Programs):
    what they are, the signs, electronic (online) abuse, consequences, prevention, the laws, and help for young
    people and the adults around them;
  - "Culture Matters: The Peace Corps Cross-Cultural Workbook" (Peace Corps, 1997, read whole from ERIC's copy on the
    Internet Archive): understanding your own culture and other people's, communication styles (direct and indirect),
    personal space, time, hierarchy, and getting along respectfully in another culture.
  Every book's notice gives the hotlines (HOTLINES: the National Domestic Violence Hotline and love is respect, both
  with text and relay options, and 911 in danger).

Already in the library and not repeated (link by name): open communication textbooks in LibreTexts' social sciences
library (interpersonal communication, relationship dynamics, conflict management, public speaking: the opencourses
keys, course:libretexts:socialsci-N) and the Open Textbook Library catalogue (cat:otl); OpenStax's College Success,
Psychology, Lifespan Development and Introduction to Sociology (osbooks: keys); the writing and business
communication guides (writing, wb:) and the money and work collection's job books for workplace communication;
parenting teenagers (parent:cdc_parenting with its teen pages, parent:nida_parents_teens, parent:cwig_family_topics);
the mental health collection's pages on loneliness, crisis lines and domestic violence hotlines (fam:crisis_lines and
the health and life collection); romance scams (the privacy collection's scam books); the State Department's
country information for cultural etiquette when travelling (the travel collection).

Not built (NOT_INCLUDED, link-only): the Surgeon General's advisory on loneliness and isolation (hhs.gov refuses
programs), the DOJ Community Relations Service's publications (its pages hold no guides a program can read), the
FTC's romance scam pages (refuses programs), FEMA's Effective Communication course (IS-242; no readable copy), and the
copyright guides of community mediation centres and hotlines.

Licences: CDC's terms (checked at every build: credit CDC, no endorsement, kept whole); youth.gov and the Peace Corps
workbook are works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every
build). robots.txt allows every page read; no AI rules (checked 2026-11-22).

Run from the repository's folder:
  python3 textbooks/relationships.py relate:cdc_partner_violence --out build/textbooks --limit 5
  python3 textbooks/relationships.py --list relationships
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
from disability_life import cdc_site_book  # noqa: E402 - the same CDC whole-site helper (CDC's terms met)

GROUP = "relationships"
GROUPS = {GROUP: "Reference, communication and relationships"}

# The help lines every book names (as the hotlines publish them, checked 2026-11-22).
HOTLINES = ("If you are in danger, call 911. National Domestic Violence Hotline: 1-800-799-7233, text START to 88788, "
            "or chat at thehotline.org. Young people: love is respect, 1-866-331-9474 or text LOVEIS to 22522. Deaf "
            "and hard of hearing callers can use their relay service.")

GUIDES = [
    cdc_site_book(GROUP, "cdc_partner_violence", "Healthy relationships, warning signs of abuse and teen dating "
                  "violence (CDC)", "Healthy relationships and abuse", ["intimate-partner-violence"],
                  "CDC's intimate partner violence pages, every page: what intimate partner violence is and the "
                  "kinds of abuse (physical violence, sexual violence, stalking, emotional and psychological "
                  "aggression, including controlling behaviour and abuse by phone or online), teen dating violence "
                  "and its warning signs, abuse during pregnancy, violence against men, risk and protective factors, "
                  "prevention and the skills of healthy relationships, and CDC's Dating Matters programme for "
                  "teens, their parents and schools.", HOTLINES,
                  units=[(r"/datingmatters/", "Dating Matters: healthy teen relationships"),
                         (r"/about/", "What it is and the warning signs"), (r".", "Prevention")]),
]

YOUTH = "https://youth.gov/youth-topics"
YOUTH_PAGES = [f"{YOUTH}/teen-dating-violence"] + [f"{YOUTH}/teen-dating-violence/{p}" for p in (
    "characteristics", "electronic", "risk-factors", "consequences", "prevention", "legal-responses",
    "sex-considerations", "resources", "additional-federal-resources")] + [f"{YOUTH}/bullying"]
GUIDES.append(K.guide(
    GROUP, "youth_gov_dating_bullying", "Teen dating violence and bullying (youth.gov)", "Teen relationships and "
    "bullying", "youth.gov (the Interagency Working Group on Youth Programs, US federal government)",
    [f"{YOUTH}/teen-dating-violence", f"{YOUTH}/bullying"],
    r"^https://youth\.gov/youth-topics/(teen-dating-violence|bullying)(/[a-z0-9-]+)*$",
    "youth.gov's pages for young people and the adults who help them, every page: what teen dating violence is and "
    "how it shows (including electronic abuse through phones and social media), risk factors, consequences, "
    "prevention and building healthy relationships, legal responses, and resources; and its bullying pages (what "
    "bullying and cyberbullying are, the signs, preventing it and responding to it).",
    f"From youth.gov, run by the federal government's Interagency Working Group on Youth Programs: a US government "
    f"work (public domain). {HOTLINES}", depth=1, units=[(r"/bullying", "Bullying"), (r".", "Teen dating violence")],
    urls=YOUTH_PAGES, limit=60))

PDFS = [
    K.us_pdf(GROUP, name="peace_corps_culture_matters", title="Culture Matters: The Peace Corps Cross-Cultural "
             "Workbook (Peace Corps, 1997)", subject="Cultural etiquette and communication",
             publisher="Peace Corps, Information Collection and Exchange (T0087)", archive="ERIC_ED429911",
             published="1997", version="1997 edition (ERIC ED429911, Internet Archive item ERIC_ED429911)",
             description="The Peace Corps' workbook for getting along in another culture, with exercises: what "
                         "culture is, how your own culture shapes you, styles of communication (direct and "
                         "indirect, high and low context), personal space, attitudes to time, individual and group, "
                         "rank and status, adjusting to a new culture and culture shock, and working with people "
                         "from other cultures.",
             notice=f"A work of the Peace Corps, a US government agency (public domain), read from ERIC's scan, whose "
                    f"machine-read text has the scanner's mistakes; its exercises are written for Peace Corps "
                    f"Volunteers but fit anyone meeting another culture. {HOTLINES}"),
]

COLLECTION = K.Collection("relate", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"relationships": lambda: [f"relate:{g['name']}" for g in GUIDES + PDFS]})

LICENCE_LINES = {
    "relationships_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the "
                         "public domain on four conditions (credit CDC, no endorsement, no change to the substance, "
                         "free on CDC's site), met in the book's notice; the pages are kept whole. robots.txt allows "
                         "the pages; no AI rules (checked 2026-11-22).",
    "relationships_youth_peace_corps": "youth.gov and the Peace Corps workbook (ERIC ED429911 on the Internet "
                                       "Archive): works of the US government (17 U.S.C. 105, the line checked on "
                                       "govinfo.gov's policies page at every build); robots.txt allows the pages; no "
                                       "AI rules (checked 2026-11-22).",
}
NOT_INCLUDED = [
    ("Our Epidemic of Loneliness and Isolation (the US Surgeon General's advisory, 2023)", "Public domain, but "
     "www.hhs.gov refuses programs (\"403\", robots.txt included, checked 2026-11-22) and no copy of the PDF was "
     "found on the Internet Archive. Link-only (the health and life collection may hold it). Index: "
     "https://www.hhs.gov/sites/default/files/surgeon-general-social-connection-advisory.pdf"),
    ("DOJ Community Relations Service (conflict resolution and mediation)", "Its pages answer programs but hold only "
     "an overview and FAQs, no guide a program can read as a book (checked 2026-11-22). Link-only. Index: "
     "https://www.justice.gov/crs"),
    ("FEMA Emergency Management Institute: Effective Communication (IS-242.c) and Leadership and Influence (IS-240)",
     "Public domain, but the course materials come only through FEMA's course player, and no copy was found on the "
     "Internet Archive (checked 2026-11-22). Link-only. Index: "
     "https://training.fema.gov/is/courseoverview.aspx?code=IS-242.c"),
    ("FTC: romance scams and online dating safety", "Public domain, but consumer.ftc.gov refuses programs (403); the "
     "privacy collection's scam books cover romance scams. Link-only. Index: "
     "https://consumer.ftc.gov/articles/what-know-about-romance-scams"),
    ("State Department country information and cultural etiquette pages", "www.state.gov refuses programs (403); "
     "travel advice is in the travel collection. Link-only. Index: https://travel.state.gov/"),
    ("National Association for Community Mediation, the National Domestic Violence Hotline's and love is respect's "
     "guides, Mental Health America and Gottman Institute articles", "Copyright of each organisation; link-only. "
     "Index: https://www.nafcm.org/ https://www.thehotline.org/ https://www.loveisrespect.org/"),
    ("Open communication textbooks (Communication in the Real World, Interpersonal Communication: A Mindful Approach "
     "to Relationships, Exploring Relationship Dynamics, Conflict Management)", "Already in the library through "
     "LibreTexts' social sciences library (opencourses) and the Open Textbook Library catalogue (cat:otl), with "
     "their own licences (CC BY or CC BY-NC-SA, the latter personal use only); not built twice. Index: "
     "https://socialsci.libretexts.org/Bookshelves/Communication"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
