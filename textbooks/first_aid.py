"""Emergency first aid, and wilderness and disaster first aid, for the reference library, in the group "Reference,
home health care and first aid" (the owner's requests of 2026-11-22). Keys: first-aid (every book), firstaid:<name>.
This module also holds the small helpers the other home health modules use (cdc_book, nhs_book, the notes).

What this module builds, in plain words, each IN FULL from the publisher's own site:
  - CDC's pages on heat illness and on cold weather (hypothermia and frostbite), kept whole with their text unchanged
    as CDC's terms ask;
  - CDC's stroke and heart disease pages (the signs of a stroke, BE FAST, and of a heart attack, what to do);
  - CDC's epilepsy pages (seizure first aid) and its traumatic brain injury and HEADS UP pages (concussion signs);
  - CDC's overdose prevention pages (naloxone, recognising an overdose, what to do);
  - CDC's rabies, tick and Lyme disease pages (animal bites, removing a tick safely);
  - the NHS's first aid and emergency condition pages (anaphylaxis, burns, cuts, broken bones, sprains, dislocations,
    head injury and concussion, heatstroke, hypothermia, frostbite, poisoning, nosebleeds, bites and stings, snake
    bites, stroke, heart attack, epilepsy, low blood sugar, asthma, knocked-out teeth, eye injuries ...), with the
    non-US note;
  - CDC Yellow Book, Health Information for International Travel (travel health: altitude, heat and cold, injuries,
    bites, water and food, travel first-aid kits; for when no doctor is near), kept whole;
  - "Emergency Childbirth: A Reference Guide for Students of the Medical Self-Help Training Course" (US Public
    Health Service and Office of Civil Defense), whole from the Internet Archive's copy of Project Gutenberg's text.
  (The US Army's First Aid, FM 4-25.11, is already a field manual of the library (pdf:army_fm_4_25_11_first_aid), and
  MedlinePlus's summaries are mlp:health_topics: not repeated.)

Every book starts with the emergency note: call 911 (or your local emergency number) in an emergency; Poison Help is
1-800-222-1222 in the US; general information, not medical training or a diagnosis.

Not built (NOT_INCLUDED, link-only for the owner's personal assistant): the Red Cross and the American Heart
Association (copyright), Ready.gov and FEMA's "Until Help Arrives" (refuse programs), WikEM and WHO (their robots.txt
shut out AI readers), Wikibooks First Aid (already in the toolkit's Kiwix library), Hesperian's books (non-commercial:
their PDFs are not offered for programs), the Merck Manual and Mayo Clinic (copyright), StatPearls (no derivatives;
the NCBI Bookshelf answers programs with a reCAPTCHA page), poison control centres' pages (copyright).

Licences: works of the US government (17 U.S.C. 105, the line checked on govinfo.gov's policies page at every build);
CDC's "Use of Agency Materials" is checked for its public-domain line and its conditions are met in the notice; the
NHS's terms release its content under the Open Government Licence v3.0 (checked at every build).

Run from the repository's folder:
  python3 textbooks/first_aid.py firstaid:cdc_heat_cold --out build/textbooks --limit 5
  python3 textbooks/first_aid.py --list first-aid
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_kit as K  # noqa: E402
import parenting as P  # noqa: E402 - CDC's terms and the page pattern of a whole CDC site
import early_childhood as E  # noqa: E402 - the NHS's terms

GROUP = "homehealth"
GROUPS = {GROUP: "Reference, home health care and first aid"}
EMERGENCY = ("In an emergency, call 911 (or your local emergency number); for a poisoning, call Poison Help at "
             "1-800-222-1222 (US). This is general information, not medical training or a diagnosis: ask a doctor, "
             "nurse or pharmacist.")
NHS_NOTICE = ("Information from the NHS website is licensed under the Open Government Licence v3.0; contains public "
              "sector information licensed under the Open Government Licence v3.0. A UK source: the NHS services, "
              "phone numbers (999 and 111) and medicine names it gives are those of the UK; in the US, call 911 in an "
              "emergency and ask your own doctor or pharmacist.")


def cdc_book(group, name, title, subject, sites, description, units, note=EMERGENCY, urls=(), limit=200):
    """A CDC web guide made of whole CDC sites, each read from its own site index ("site.html"), kept whole under
    CDC's terms with CDC's notice and the given note (the same shape as parenting.cdc_book, in another group)."""
    entry = K.guide(group, name, title, subject, P.CDC_PUBLISHER,
                    [f"https://www.cdc.gov/{s}/site.html" for s in sites], P.cdc_sites(sites), description,
                    note + " " + P.CDC_NOTICE, depth=1, units=units, limit=limit)
    entry["urls"] = list(urls)
    return dict(entry, licence_page=P.CDC_TERMS, licence_text=P.CDC_TEXT, unchanged=True)


def nhs_book(group, name, title, subject, slugs, description, note=EMERGENCY, units=None):
    """An NHS guide made of a fixed list of nhs.uk pages ("conditions/anaphylaxis" and the like, each read whole),
    under the Open Government Licence v3.0 with the non-US note."""
    urls = [f"https://www.nhs.uk/{s.strip('/')}/" for s in slugs]
    names = "|".join(sorted({s.strip("/") for s in slugs}, key=len, reverse=True))
    entry = K.guide(group, name, title, subject, "NHS England (nhs.uk)", urls[0],
                    rf"^https://www\.nhs\.uk/({names})/$", description, note + " " + NHS_NOTICE, depth=0,
                    units=units or [(r".", subject)], limit=len(urls) + 5, country="United Kingdom")
    entry["urls"] = urls
    return dict(entry, licence="OGL-UK-3.0", licence_url=E.OGL_URL, licence_page=E.NHS_TERMS,
                licence_text=E.NHS_TEXT)


GUIDES = [
    cdc_book(GROUP, "cdc_heat_cold", "Heat illness, hypothermia and frostbite (CDC)", "First aid: heat and cold",
             ["heat-health", "winter-weather"],
             "CDC's pages on heat and on winter weather, every page: heat exhaustion and heat stroke (the signs and "
             "what to do), heat and medicines, keeping cool, people at higher risk; hypothermia and frostbite (the "
             "warning signs and first aid), staying safe in cold weather, carbon monoxide, and preparing a home and "
             "car for winter.", units=[(r"/heat-health/", "Heat"), (r".", "Cold weather")]),
    cdc_book(GROUP, "cdc_stroke_heart", "Stroke and heart attack signs (CDC)", "First aid: stroke and heart attack",
             ["stroke", "heart-disease"],
             "CDC's stroke and heart disease pages, every page: the signs of a stroke (BE FAST: balance, eyes, face, "
             "arms, speech, time to call 911) and of a heart attack, what to do while waiting for help, the risk "
             "factors and how to prevent them.", units=[(r"/stroke/", "Stroke"), (r".", "Heart disease")]),
    cdc_book(GROUP, "cdc_seizures_concussion", "Seizure first aid and concussion (CDC)", "First aid: seizures and "
             "head injuries", ["epilepsy", "traumatic-brain-injury", "heads-up"],
             "CDC's epilepsy pages (seizure first aid: what to do and what not to do, when to call 911, kinds of "
             "seizures) and its traumatic brain injury and HEADS UP pages (concussion signs and symptoms, danger "
             "signs in adults and children, recovery and returning to school, work and sport), every page.",
             units=[(r"/epilepsy/", "Seizures and epilepsy"), (r".", "Head injury and concussion")]),
    cdc_book(GROUP, "cdc_overdose", "Overdose and naloxone (CDC)", "First aid: overdose",
             ["overdose-prevention", "stop-overdose"],
             "CDC's overdose prevention pages, every page: the signs of an opioid overdose, how to give naloxone and "
             "what to do until help comes, fentanyl and other drugs, and getting treatment.",
             units=[(r".", "Overdose")]),
    cdc_book(GROUP, "cdc_bites_ticks", "Animal bites, rabies, ticks and Lyme disease (CDC)", "First aid: bites",
             ["rabies", "ticks", "lyme"],
             "CDC's rabies pages (what to do after an animal bite or scratch, which animals carry it, getting care), "
             "and its tick and Lyme disease pages (removing a tick safely, preventing bites, the signs of tickborne "
             "diseases), every page.", units=[(r"/rabies/", "Rabies and animal bites"), (r".", "Ticks and Lyme "
                                                                                                  "disease")]),
    cdc_book(GROUP, "cdc_yellow_book", "Health Information for International Travel: the Yellow Book (CDC)",
             "Travel health", ["yellow-book"],
             "CDC's Yellow Book, every chapter: preparing for travel, travel first-aid kits, food and water, insect "
             "bites, altitude illness, heat and cold, injuries and safety, travelling with children, during "
             "pregnancy and with health conditions, and getting care abroad; for when no doctor is near.",
             units=[(r".", "The Yellow Book")], limit=500),
    nhs_book(GROUP, "nhs_emergency_first_aid", "First aid for emergencies and injuries (NHS)", "First aid (UK)",
             ["conditions/anaphylaxis", "conditions/burns-and-scalds", "conditions/cuts-and-grazes",
              "conditions/broken-arm-or-wrist", "conditions/broken-leg", "conditions/sprains-and-strains",
              "conditions/dislocated-shoulder", "conditions/head-injury-and-concussion",
              "conditions/heat-exhaustion-heatstroke", "conditions/hypothermia", "conditions/frostbite",
              "conditions/poisoning", "conditions/nosebleed", "conditions/animal-and-human-bites",
              "conditions/insect-bites-and-stings", "conditions/snake-bites", "conditions/stroke",
              "conditions/heart-attack", "conditions/epilepsy", "conditions/low-blood-sugar-hypoglycaemia",
              "conditions/asthma", "conditions/knocked-out-tooth", "conditions/eye-injuries"],
             "The NHS's pages on emergencies and injuries, each whole: anaphylaxis (a severe allergic reaction and "
             "adrenaline auto-injectors), burns and scalds, cuts and grazes, broken arms, wrists and legs, sprains "
             "and strains, dislocated shoulders, head injuries and concussion, heat exhaustion and heatstroke, "
             "hypothermia, frostbite, poisoning, nosebleeds, animal and human bites, insect bites and stings, snake "
             "bites, stroke, heart attack, epilepsy (seizures), low blood sugar, asthma attacks, knocked-out "
             "teeth and eye injuries: the symptoms, what to do, and when to call 999 (911 in the US) or go to A&E."),
]

PDFS = [
    K.us_pdf(GROUP, name="emergency_childbirth_self_help", title="Emergency Childbirth: A Reference Guide for "
             "Students of the Medical Self-Help Training Course (US Public Health Service)",
             subject="Emergency childbirth", publisher="US Public Health Service and the Office of Civil Defense",
             archive="emergencychildbi26923gut", version="Project Gutenberg text 26923",
             description="The civil defence guide to helping a woman give birth when no doctor or midwife can come: "
                         "the signs and stages of labour, preparing, delivering the baby and the afterbirth, caring "
                         "for the mother and the newborn, and the warning signs. From the 1960s: call 911 first.",
             notice="Call 911 (or your local emergency number) first: a dispatcher will talk you through the birth "
                    "until help arrives. A US government guide from the 1960s: practice has changed since. This is "
                    "general information, not medical training."),
]

COLLECTION = K.Collection("firstaid", GROUP, guides=GUIDES, pdfs=PDFS,
                          words={"first-aid": lambda: [f"firstaid:{g['name']}" for g in GUIDES + PDFS]})

PRACTICE_SUBJECTS = [
    (r"^(first aid|home treatment|long-term conditions|dental care|eye care|after the birth) \(uk\)",
     "emergency numbers (999 and 111, not 911), health services and how to reach them (the NHS, not US insurance), "
     "medicine names and which are sold without a prescription"),
]
LICENCE_LINES = {
    "firstaid_cdc": "www.cdc.gov/other/agencymaterials.html (checked at every build): CDC's pages are in the public "
                    "domain on four conditions (credit CDC, no endorsement, no change to the substance, free on CDC's "
                    "site), met in each CDC book's notice; the pages are kept whole. robots.txt allows the pages; no "
                    "AI rules (checked 2026-11-22).",
    "firstaid_nhs": "nhs.uk/our-policies/terms-and-conditions (checked at every build): its content is \"released "
                    "free-of-charge under the current version of the Open Government Licence\"; the attribution is "
                    "in the notice. robots.txt allows /conditions/; no AI rules (checked 2026-11-22).",
    "firstaid_childbirth": "archive.org (its robots.txt allows the files): the Emergency Childbirth guide is a US "
                           "Public Health Service work (public domain), the Internet Archive's copy of Project "
                           "Gutenberg's text.",
}
NOT_INCLUDED = [
    ("American Red Cross first aid and CPR guides, and the American Heart Association's CPR and first aid materials",
     "\"© American Red Cross\" and \"© American Heart Association, Inc. All rights reserved\": copyright, not openly "
     "licensed (checked 2026-11-22). Link-only. Index: https://www.redcross.org/take-a-class/first-aid/"
     "performing-first-aid and https://cpr.heart.org/"),
    ("Ready.gov and FEMA's \"Until Help Arrives\"", "Public domain, but www.ready.gov and www.fema.gov refuse "
     "programs (the preparedness books already say so; checked 2026-11-22). Link-only. Index: "
     "https://www.ready.gov/until-help-arrives"),
    ("WikEM and the World Health Organization's first aid and emergency care publications", "Their robots.txt shuts "
     "out AI companies' readers (wikem.org, www.who.int, checked 2026-11-22), and WHO's publications are mostly CC "
     "BY-NC-SA. Not read. Link-only. Index: https://wikem.org/ and https://www.who.int/publications"),
    ("Wikibooks: First Aid (CC BY-SA)", "Already in the toolkit's Kiwix library (Wikibooks in full), which the "
     "toolkit reads; not repeated. Index: https://en.wikibooks.org/wiki/First_Aid"),
    ("US Army Special Forces Medical Handbook (ST 31-91B, 1982)", "The Internet Archive's copy "
     "(milmanual-st-31-91b--us-army-special-forces-medical-handbook) does not show Distribution Statement A in its "
     "front matter (the builder's check, 2026-11-22), so it is not copied. Link-only. Index: "
     "https://archive.org/details/milmanual-st-31-91b--us-army-special-forces-medical-handbook"),
    ("US Army TC 4-02.1, First Aid (2016)", "No copy with a text layer and its front matter was found at the "
     "Internet Archive (checked 2026-11-22); FM 4-25.11 (2002) is already built (pdf:army_fm_4_25_11_first_aid). "
     "Index: https://armypubs.army.mil/"),
    ("Hesperian Health Guides: Where There Is No Doctor, Where Women Have No Doctor, Where There Is No Dentist and A "
     "Book for Midwives", "Free for non-commercial use (personal use only), but hesperian.org no longer offers the "
     "PDFs at addresses a program can find (its book pages answered 404 on 2026-11-22). Link-only. Index: "
     "https://hesperian.org/"),
    ("Merck Manual Consumer Version, Mayo Clinic first aid and Poison Control (poison.org)", "Copyright of Merck & "
     "Co., the Mayo Foundation and National Capital Poison Center (checked 2026-11-22). Link-only. Index: "
     "https://www.merckmanuals.com/home , https://www.mayoclinic.org/first-aid and https://www.poison.org/"),
    ("StatPearls (NCBI Bookshelf)", "CC BY-NC-ND (no derivatives, non-commercial), and the NCBI Bookshelf answers "
     "programs with a reCAPTCHA page. Link-only. Index: https://www.ncbi.nlm.nih.gov/books/NBK430685/"),
    ("First aid for blind and low-vision people", "No open guide written for blind first-aiders was found (the "
     "RNIB's and AFB's pages are copyright, checked 2026-11-22); the books here are read aloud as they are. Index: "
     "https://www.rnib.org.uk/ and https://www.afb.org/"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
