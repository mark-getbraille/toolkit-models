"""Remote and long-term-care medicine for the reference library, in its own group "Reference, remote and long-term
care medicine" (the owner's request of 2026-11-23: medical guidance for when professional help is hours or days
away). Keys: rmed:<name>. Request words: remote-medicine (every book) and one word per theme: rmed-ship,
rmed-austere, rmed-pfa and rmed-nursing.

What this module builds, in plain words (every book's notice carries REMOTE_NOTE, "For when no professional help is
available; follow current medical guidance and get professional care as soon as possible", with the edition's date
and what in it may be out of date):
  - ship's medicine (rmed-ship): the US Public Health Service's The Ship's Medicine Chest, in four editions from the
    Internet Archive (the 1904 Handbook, the 1929 and 1940 editions "and First Aid at Sea", and the 2003 edition "and
    Medical Aid at Sea"); the UK Maritime and Coastguard Agency's notice on ships' medical stores (MSN 1905: the
    medicines and equipment a ship must carry) and its guidance notes on infectious disease at sea and on radio
    medical advice (MGN 652 and MGN 623), under the Open Government Licence v3.0;
  - remote and austere care (rmed-austere): the Joint Trauma System's clinical practice guidelines for prolonged
    and remote care, read from jts.health.mil (the newest version of each, found on the guidelines page at every
    build), Emergency War Surgery (third US revision, 2004, the DTIC copy), the Special Operations Forces Medical
    Handbook (2001), three US Army Research Institute of Environmental Medicine guides (cold, desert heat and
    altitude), the NOAA Diving Manual (1991), and CDC's pages on infectious diseases that break out after disasters
    and in remote places (cholera, typhoid, hepatitis A and E, measles, malaria, dengue, Ebola, plague and others);
  - psychological first aid (rmed-pfa): the Psychological First Aid Field Operations Guide (2nd edition, 2006),
    Psychological First Aid for Schools and Skills for Psychological Recovery (the National Child Traumatic Stress
    Network and the VA's National Center for PTSD: copyright, copied by their notice only whole, unchanged and free
    of charge, so PERSONAL USE ONLY), the National Center for PTSD's disaster pages (VA, public domain), and the
    Defense Health Agency's guideline on forward management of acute mental health conditions by non-specialists;
  - nursing and caregiving at home (rmed-nursing): three old public-domain home nursing books (the American Red
    Cross Text-Book on Home Hygiene and Care of the Sick, 1922; Harrison's Text Book of Home Nursing, 1918; Pope's
    Home Care of the Sick, 1907), each with a note on what is out of date, and the FDA's pages on using medicines
    safely (drug interactions, over-the-counter medicines, antibiotics, medicines and age);
  - rmed:index, a plain-words guide to all of it and to the library's other first aid, wilderness, home health,
    medicine and mental health books (the toolkit's own facts and links, CC0).

Military publications follow military_release.py: each is judged at every build by its own front pages (the builder
writes the truthful release line); they are read whole (military=True: no parts are cut, as none is about
explosives). The Joint Trauma System's guideline on unexploded ordnance is not chosen.

Already in the library and linked from the index, not repeated: first aid (firstaid:, with the CDC Yellow Book and the
Special Forces Medical Handbook ST 31-91B), wilderness first aid (wild:, with Army TB MED 505, 507 and 508), home
health (homecare:), mental health (mind:) and SAMHSA's disaster leaflets (gpo:), aging and caregiving (aging:, gpo:),
the Navy's Hospital Corpsman course (pdf:navy_hospital_corpsman), the Army's First Aid (pdf:army_fm_4_25_11_first_aid),
the Coast Guard's boat crew first aid handbook (boat:uscg_bch_first_aid), the medicine labels (word medicines) and the
Open RN nursing books, which are already in LibreTexts' medicine shelf (course:libretexts:med-0, med-1 and med-3).

Not built (NOT_INCLUDED, link-only or left out, with the reason): the WHO International Medical Guide for Ships and
WHO's psychological first aid guide (WHO copyright; WHO's robots.txt shuts out AI readers), the UK Ship Captain's
Medical Guide (TSO's copyright), the Borden Institute's Emergency War Surgery 5th edition and Medical Aspects of Harsh
Environments (they print "certain parts of this publication pertain to copyright restrictions"), the Alaska Community
Health Aide/Practitioner Manual (it prints a copyright claim), Open RN's Health Promotion book (its Pressbooks site
refuses programs), and others below.

Run from the repository's folder:
  python3 textbooks/remote_medicine.py rmed:ships_medicine_chest_2003 --out build/textbooks --limit 3
  python3 textbooks/remote_medicine.py --list remote-medicine
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import early_childhood as E  # noqa: E402 - the Open Government Licence address
import mental_health as M  # noqa: E402 - the shared CDC and page-list helpers of the health modules
import practical_index as X  # noqa: E402 - the index maker
import refs_kit as K  # noqa: E402
from old_ia_books import old_book  # noqa: E402

PREFIX = "rmed"
GROUP = "remotemed"
GROUPS = {GROUP: "Reference, remote and long-term care medicine"}

# The words every book's notice ends with (the owner's own words first).
REMOTE_NOTE = ("For when no professional help is available; follow current medical guidance and get professional "
               "care as soon as possible. In an emergency call 911 (or your local emergency number); at sea, call the "
               "Coast Guard on VHF channel 16 or ask for radio medical advice; where there is no phone signal, use a "
               "satellite messenger or a personal locator beacon. General information, not medical training or a "
               "diagnosis; medicine doses are only those the source itself states.")


# The edition words of a web guide (its pages are read anew at each build; the book's version says the day).
WEB_EDITION = ("Edition: the publisher's web pages as read on the day in this book's version; they change, so check "
               "the site for the current guidance.")


def dated(year, outdated):
    """The first words of a notice: the edition's date and what in it may be out of date."""
    return f"Edition of {year}: {outdated}"


# ====================================================================== ship's medicine (rmed-ship)

OLD_DRUGS = ("its medicines (such as mercury, opium, arsenic and strychnine preparations), doses and treatments are "
             "those of its day and many are now known to be harmful; never use its doses.")
SHIP_PDFS = [
    old_book(GROUP, "ships_medicine_chest_1904", "Handbook for the Ship's Medicine Chest (US Public Health and "
             "Marine-Hospital Service, 1904)", "Ship's medicine", "Public Health and Marine-Hospital Service (US); "
             "George W. Stoner (Government Printing Office)", "handbookforships00unitrich", 1904,
             "The government handbook for ship masters with no doctor on board, at the time of the Marine-Hospital "
             "Service: the ship's medicine chest and what each medicine was for, examining the sick, common "
             "diseases at sea, injuries, wounds and fractures, and keeping seamen healthy. A work of the US "
             "government, also public domain as published before 1931.",
             notice=dated(1904, OLD_DRUGS) + " " + REMOTE_NOTE),
    old_book(GROUP, "ships_medicine_chest_1929", "The Ship's Medicine Chest and First Aid at Sea (US Public Health "
             "Service, 1929)", "Ship's medicine", "United States Public Health Service (Government Printing Office)",
             "shipsmedicineche00unit", 1929,
             "The Public Health Service's guide for masters and mates of merchant ships without a doctor: the "
             "medicine chest and its use, first aid for injuries, burns, drowning and poisoning, diseases common at "
             "sea, communicable diseases and quarantine, and radio medical advice as it was in 1929. A work of the "
             "US government, also public domain as published before 1931.",
             notice=dated(1929, OLD_DRUGS) + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="ships_medicine_chest_1940", title="The Ship's Medicine Chest and First Aid at Sea (US Public "
             "Health Service, 1940)", subject="Ship's medicine", publisher="United States Public Health Service "
             "(Government Printing Office)", archive="100928449.nlm.nih.gov", published="1940",
             version="1940 edition (Internet Archive item 100928449.nlm.nih.gov, the National Library of Medicine's "
                     "copy)",
             description="The 1940 edition of the Public Health Service's guide for merchant ships without a "
                         "doctor: the medicine chest, examining a sick seaman, first aid, the diseases and injuries "
                         "of seamen, venereal disease, communicable diseases and quarantine, and getting medical "
                         "advice by radio.",
             notice=dated(1940, "before antibiotics were in common use: its medicines, doses and many of its "
                                "treatments are out of date; never use its doses.") + " A work of the US government "
                    "(public domain), read from the Internet Archive's copy of the National Library of Medicine's "
                    "scan. " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="ships_medicine_chest_2003", title="The Ship's Medicine Chest and Medical Aid at Sea (US "
             "Department of Health and Human Services, 2003 revision)", subject="Ship's medicine",
             publisher="US Department of Health and Human Services, Public Health Service",
             archive="gov.law.usphs.ships.2003", published="2003",
             version="2003 revision (Internet Archive item gov.law.usphs.ships.2003, Public.Resource.Org's copy)",
             description="The last edition of the US government's guide for ships without a doctor (first published "
                         "in 1881 as the Handbook for the Ship's Medicine Chest): examining a patient and taking vital "
                         "signs, first aid and emergency care (bleeding, shock, breathing, burns, fractures, "
                         "poisoning, hypothermia and drowning), diseases by body system, communicable diseases, "
                         "pregnancy and childbirth at sea, care of the sick and injured on board (nursing care), "
                         "dental emergencies, death at sea, getting medical advice by radio, and the ship's medicine "
                         "chest with each medicine's use, dose and cautions.",
             notice=dated(2003, "its medicine list, doses and some treatments (CPR, antibiotics, malaria medicines) "
                                "may be out of date; check doses with radio medical advice or a current label.")
                    + " A work of the US government (public domain), read from the Internet Archive's copy. "
                    + REMOTE_NOTE),
]

# The UK Maritime and Coastguard Agency's notices on gov.uk, under the Open Government Licence v3.0 (the licence
# line is on each publication page, checked at every build).
GOVUK = "https://www.gov.uk/government/publications/"
OGL = dict(country="United Kingdom", licence="OGL-UK-3.0", licence_url=E.OGL_URL,
           licence_text=r"Open Government Licence v3\.0")
OGL_CREDIT = ("Contains public sector information licensed under the Open Government Licence v3.0 (Maritime and "
              "Coastguard Agency). A UK source: its rules, radio services and medicine names are the UK's.")
MGN_PAGES = [GOVUK + "mgn-652-mf-infectious-disease-at-sea/mgn-652-mf-amendment-1-infectious-disease-at-sea",
             GOVUK + "mgn-623-mf-amendment-1-telemedical-advice-service-tmas-for-ships-at-sea/"
                     "mgn-623-mf-amendment-1-telemedical-advice-service-tmas-for-ships-at-sea"]
SHIP_PDFS.append(dict(
    OGL, group=GROUP, name="uk_mca_msn_1905_ships_medical_stores", title="Ships' Medical Stores (MSN 1905, Maritime "
    "and Coastguard Agency, UK)", subject="The ship's medicine chest", publisher="Maritime and Coastguard Agency "
    "(UK)", page=GOVUK + "msn-1905-mf-amendment-5-ships-medical-stores", pdf_pattern=r"MSN_1905[^/]*\.pdf$",
    level="reference", version="the newest amendment published on gov.uk",
    description="The UK merchant shipping notice on the medicines and medical equipment ships and fishing vessels "
                "must carry, by category of vessel (how far from land it goes), with its annexes: the lists of "
                "medicines and their quantities, medical equipment, antidotes for dangerous goods, and how to keep "
                "and replace stores. A good checklist of a remote medicine chest.",
    notice=dated("the newest amendment", "the lists change; check gov.uk for the current notice.") + " "
           + OGL_CREDIT + " " + REMOTE_NOTE))
SHIP_GUIDES = [dict(M.pages_book(
    GROUP, "uk_mca_medical_notices_at_sea", "Infectious disease at sea and radio medical advice (MGN 652 and MGN "
    "623, Maritime and Coastguard Agency, UK)", "Medical advice at sea", "Maritime and Coastguard Agency (UK)",
    MGN_PAGES, r"^https://www\.gov\.uk/government/publications/mgn-(652|623)-[a-z0-9-]+/mgn-(652|623)-[a-z0-9-]+$",
    "Two UK marine guidance notes, each whole: infectious disease at sea (recognising and isolating an infectious "
    "illness on board, reporting it before arrival, and protecting the crew) and the Telemedical Advice Service "
    "(TMAS: how a ship with no doctor gets medical advice by radio or satellite, and what to have ready when you "
    "call).", dated("the newest amendment", "check gov.uk for the current notes.") + " " + OGL_CREDIT + " "
    + REMOTE_NOTE, units=[(r"mgn-652", "Infectious disease at sea"), (r".", "Radio medical advice")]),
    **OGL, licence_page=MGN_PAGES[0])]

# ====================================================================== remote and austere care (rmed-austere)

JTS = "https://jts.health.mil"
JTS_PAGE = JTS + "/index.cfm/CPGs/cpgs"
JTS_NOTE = ("Edition: the newest version the Joint Trauma System lists, dated on its first page; the JTS updates its "
            "guidelines, so check jts.health.mil for a newer one. Written for military medical staff in remote "
            "and deployed places: its drugs, doses and procedures are for trained people and the equipment they "
            "carry.")


def jts(name, title, pattern, description):
    """One Joint Trauma System clinical practice guideline: the newest PDF on the guidelines page whose address
    matches pattern, judged by the release rule (military=True; read from the .mil site itself)."""
    return K.us_pdf(GROUP, name=name, title=title, subject="Prolonged and remote casualty care",
                    publisher="Joint Trauma System, Defense Health Agency (US Department of Defense)", page=JTS_PAGE,
                    pdf_pattern=pattern, military=True, work="a work of the US Department of Defense",
                    version="the newest version on jts.health.mil", description=description,
                    notice=f"{JTS_NOTE} {REMOTE_NOTE}")


CPG = r"/assets/docs/cpgs/"
JTS_PDFS = [
    jts("jts_prolonged_casualty_care", "Prolonged Casualty Care Guidelines (Joint Trauma System, CPG ID 91)",
        CPG + r"Prolonged_Casualty_Care_Guidelines_[^/]*\.pdf$",
        "The consolidated guide to caring for a casualty for hours or days in remote or austere places before "
        "evacuation: the PCC principles, triage of many casualties, massive bleeding, airway, breathing, "
        "circulation and resuscitation, communication and documentation, hypothermia and heat illness, head "
        "injury, pain management and sedation, wounds, burns, nursing care, infection and antibiotics, nutrition, "
        "and preparing a casualty for a long move."),
    jts("jts_nursing_interventions_pcc", "Nursing Interventions in Prolonged Casualty Care (Joint Trauma System, "
        "CPG ID 70)", CPG + r"Nursing_Interventions_PCC_[^/]*\.pdf$",
        "Nursing care for a casualty kept for a long time far from a hospital: hygiene and skin care, turning and "
        "preventing pressure sores, wound and dressing care, splints, eye and mouth care, lines and tubes, fluids "
        "in and out, bladder and bowel care, keeping the casualty warm and comfortable, and the nursing checklist."),
    jts("jts_analgesia_sedation_pfc", "Analgesia and Sedation Management during Prolonged Field Care (Joint "
        "Trauma System, CPG ID 61)", CPG + r"Analgesia_and_Sedation_Management_during_PFC_[^/]*\.pdf$",
        "Managing pain and sedation for a casualty held for a long time in the field: assessing pain, medicines "
        "and their dangers, monitoring, and what to do when supplies run low."),
    jts("jts_burn_management_pfc", "Burn Management in Prolonged Field Care (Joint Trauma System, CPG ID 57)",
        CPG + r"Burn_Management_PFC_[^/]*\.pdf$",
        "Caring for burns when evacuation is delayed: estimating the burn's size, fluids by mouth and by drip, "
        "wound care and dressings, pain, infection, and monitoring urine output."),
    jts("jts_burn_care", "Burn Care (Joint Trauma System, CPG ID 12)", CPG + r"Burn_Care_CPG_[^/]*\.pdf$",
        "The JTS's main burn guideline: first care, resuscitation with fluids, airway and inhalation injury, wound "
        "care, electrical and chemical burns, and burns in children."),
    jts("jts_crush_syndrome_pfc", "Crush Syndrome in Prolonged Field Care (Joint Trauma System, CPG ID 58)",
        CPG + r"Crush_Syndrome_PFC_[^/]*\.pdf$",
        "Recognising and treating crush injury and crush syndrome (after a limb has been trapped under a heavy "
        "weight, as in a building collapse) when help is far away: fluids, potassium danger to the heart, and "
        "kidney failure."),
    jts("jts_damage_control_resuscitation_pfc", "Damage Control Resuscitation in Prolonged Field Care (Joint Trauma "
        "System, CPG ID 73)", CPG + r"Damage_Control_Resuscitation_PFC_[^/]*\.pdf$",
        "Resuscitating a bleeding casualty over hours in the field: stopping bleeding, blood and fluids, "
        "preventing the deadly triad (cold, acid blood and poor clotting), and reassessing."),
    jts("jts_wound_management_pfc", "Wound Management in Prolonged Field Care (Joint Trauma System, CPG ID 62)",
        CPG + r"Wound_Management_PFC_[^/]*\.pdf$",
        "Caring for wounds when evacuation is delayed: cleaning and irrigation, when not to close a wound, "
        "dressings and their changes, infection signs, and antibiotics."),
    jts("jts_tbi_pfc", "Traumatic Brain Injury Management in Prolonged Field Care (Joint Trauma System, CPG ID 63)",
        CPG + r"Traumatic_Brain_Injury_PFC_[^/]*\.pdf$",
        "Caring for a head injury when evacuation is delayed: checking consciousness and pupils, keeping oxygen "
        "and blood pressure up, positioning, seizures, and the warning signs of rising pressure in the skull."),
    jts("jts_ocular_injuries_pfc", "Ocular Injuries and Vision-Threatening Conditions in Prolonged Field Care "
        "(Joint Trauma System, CPG ID 66)", CPG + r"Ocular_Injuries_Vision-Threatening_Conditions_PFC_[^/]*\.pdf$",
        "Eye injuries and sight-threatening eye problems far from an eye doctor: examining the eye, chemical "
        "burns, foreign bodies, penetrating injuries (shield, do not press), and infections."),
    jts("jts_eye_trauma_initial_care", "Eye Trauma: Initial Care (Joint Trauma System, CPG ID 3)",
        CPG + r"Eye_Trauma_Initial_Care_\d[^/]*\.pdf$",
        "The first care of eye injuries: what to check, rinsing chemical injuries, protecting an injured eye with "
        "a rigid shield, and what never to do."),
    jts("jts_frostbite_immersion_foot", "Frostbite and Immersion Foot Care (Joint Trauma System, CPG ID 59)",
        CPG + r"Frostbite_and_Immersion_Foot_Care_[^/]*\.pdf$",
        "Recognising and treating frostbite and non-freezing cold injury (trench or immersion foot): rewarming, "
        "when not to rewarm, blisters, pain, and protecting the tissue."),
    jts("jts_hypothermia", "Hypothermia Prevention, Monitoring and Management (Joint Trauma System, CPG ID 23)",
        CPG + r"Hypothermia_Prevention_Treatment_[^/]*\.pdf$",
        "Keeping injured people warm and treating hypothermia: how injured people lose heat, insulation and "
        "active warming, warmed fluids, and monitoring temperature."),
    jts("jts_drowning", "Drowning Management (Joint Trauma System, CPG ID 64)", CPG + r"Drowning_Management_[^/]*\.pdf$",
        "Rescue and care of a drowning person: rescue breaths first, CPR, oxygen, and the problems that can come "
        "hours later."),
    jts("jts_altitude_emergencies", "Altitude Emergencies in the Prehospital Environment (Joint Trauma System, CPG "
        "ID 95)", CPG + r"Altitude_Emergencies_Prehospital_Environment_[^/]*\.pdf$",
        "Acute mountain sickness, high-altitude pulmonary oedema (HAPE) and cerebral oedema (HACE): recognising "
        "them, descent as the main treatment, oxygen and medicines."),
    jts("jts_infection_prevention", "Infection Prevention in Combat-Related Injuries (Joint Trauma System, CPG ID "
        "24)", CPG + r"Infection_Prevention_in_Combat_Injuries_[^/]*\.pdf$",
        "Preventing infection in serious wounds: early antibiotics, wound cleaning, dressings, and when infection "
        "is suspected."),
    jts("jts_spine_injury", "Cervical and Thoracolumbar Spine Injury Evaluation, Transport and Surgery (Joint "
        "Trauma System, CPG ID 15)", CPG + r"Cervical_Thoracolumbar_Spine_Injury_[^/]*\.pdf$",
        "Checking for and protecting a spine injury, moving and transporting the casualty, and what the surgeon "
        "does later."),
    jts("jts_extremity_fractures", "Orthopaedic Trauma: Extremity Fractures (Joint Trauma System, CPG ID 56)",
        CPG + r"Orthopaedic_Trauma_Extremity_Fractures_[^/]*\.pdf$",
        "Broken arms and legs: checking the blood supply and nerves, splinting and traction, open fractures and "
        "antibiotics, and later surgical care."),
    jts("jts_nutrition", "Nutrition Using Enteral and Parenteral Methods (Joint Trauma System, CPG ID 33)",
        CPG + r"Nutrition_Using_Enteral_and_Parenteral_Methods_[^/]*\.pdf$",
        "Feeding a seriously injured or ill person who is kept for days: how much energy and protein, feeding by "
        "mouth and by tube, and the dangers of refeeding."),
    jts("jts_documentation_pfc", "Documentation in Prolonged Field Care (Joint Trauma System, CPG ID 72)",
        CPG + r"Documentation_Prolonged_Field_Care_[^/]*\.pdf$",
        "Writing down what happened and what was done for a casualty kept over hours or days: the flow sheet of "
        "vital signs, treatments and medicines, and handing over to the next carer."),
    jts("jts_telemedicine", "Telemedicine in the Deployed Setting (Joint Trauma System, CPG ID 94)",
        CPG + r"Telemedicine_Deployed_Setting_[^/]*\.pdf$",
        "Getting medical advice from a distant doctor by phone, radio or video: what to have ready, how to give a "
        "clear report, and the limits of advice from far away."),
]

ARMY_NOTE = ("Written for military medical staff; practice has changed since.")
AUSTERE_PDFS = JTS_PDFS + [
    K.us_pdf(GROUP, name="army_emergency_war_surgery_2004", title="Emergency War Surgery: Third United States "
             "Revision (2004)", subject="Emergency surgery in austere places", publisher="Borden Institute, Walter "
             "Reed Army Medical Center (US Army); the Defense Technical Information Center's copy",
             archive="DTIC_ADA428731", military=True, work="a work of the US Army", published="2004",
             version="Third United States Revision, 2004 (Internet Archive item DTIC_ADA428731)",
             description="The military surgeon's handbook for treating the injured with limited resources: triage of "
                         "many casualties, airway, shock and resuscitation, wound care, burns, cold and heat "
                         "injuries, injuries of each part of the body, care of the injured child, and the care of "
                         "casualties waiting for evacuation. A surgical handbook for trained surgeons and medics.",
             notice=dated(2004, "the 5th edition (2018) has replaced it; tourniquets, blood products and many "
                                "practices have changed since.") + " " + ARMY_NOTE + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="socom_sof_medical_handbook_2001", title="Special Operations Forces Medical Handbook (US "
             "Special Operations Command, 2001)", subject="Medicine far from a hospital",
             publisher="US Special Operations Command (printed by Teton NewMedia)", archive="SOFMH2001",
             military=True, work="a work of the US Special Operations Command", published="2001",
             version="first edition, 2001 (Internet Archive item SOFMH2001)",
             description="The single-volume medical reference for special operations medics working far from a "
                         "hospital: history and examination, symptoms and how to work them out, diseases by body "
                         "system, infectious and tropical diseases, environmental injuries (heat, cold, altitude, "
                         "diving, bites and stings), trauma, children and women's health, dental care, mental "
                         "health, veterinary care, and procedures. (The 1982 Special Forces Medical Handbook is "
                         "firstaid:army_st_31_91b_special_forces_medical.)",
             notice=dated(2001, "medicines, doses and practices have changed since (the American Heart "
                                "Association's resuscitation charts are left out of the book itself for copyright).")
                    + " " + ARMY_NOTE + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="usariem_cold_weather_1992", title="Sustaining Health and Performance in the Cold: "
             "Environmental Medicine Guidance for Cold-Weather Operations (USARIEM Technical Note 92-2)",
             subject="Cold injuries", publisher="US Army Research Institute of Environmental Medicine (USARIEM)",
             archive="DTIC_ADA254328", military=True, work="a work of the US Army", published="1992-07",
             version="Technical Note 92-2, July 1992 (Internet Archive item DTIC_ADA254328)",
             description="The Army's guide to staying healthy in the cold: how the body loses heat, clothing, food "
                         "and water, preventing and treating hypothermia, frostbite, trench foot and other cold "
                         "injuries, the wind chill chart, cold-weather training and a survival kit. (Army TB MED 508 "
                         "is wild:army_tb_med_508_cold.)",
             notice=dated(1992, "the wind chill chart was revised in 2001, and some first aid has changed.") + " "
                    + ARMY_NOTE + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="usariem_desert_heat_1990", title="Sustaining Health and Performance in the Desert: "
             "Environmental Medicine Guidance (USARIEM Technical Note 91-1)", subject="Heat illness",
             publisher="US Army Research Institute of Environmental Medicine (USARIEM)", archive="DTIC_ADA229643",
             military=True, work="a work of the US Army", published="1990-12",
             version="Technical Note 91-1, December 1990 (Internet Archive item DTIC_ADA229643)",
             description="The Army's guide to staying healthy in hot deserts, written for Operation Desert Shield: "
                         "acclimatisation, water and work-rest tables, preventing and treating heat illness, sun, "
                         "sand and dust, insects and other desert hazards. (Army TB MED 507 is "
                         "wild:army_tb_med_507_heat.)",
             notice=dated(1990, "today's water guidance warns more strongly against drinking too much water "
                                "(low blood sodium); see TB MED 507.") + " " + ARMY_NOTE + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="usariem_altitude_guide_2004", title="Altitude Acclimatization Guide (USARIEM Technical "
             "Note TN04-05)", subject="Altitude illness", publisher="US Army Research Institute of Environmental "
             "Medicine (USARIEM)", archive="DTIC_ADA423388", military=True, work="a work of the US Army",
             published="2004-03", version="Technical Note TN04-05, March 2004 (Internet Archive item DTIC_ADA423388)",
             description="A short guide to going high safely: how altitude affects the body, staged ascent and "
                         "acclimatisation, and recognising acute mountain sickness, HAPE and HACE. (Army TB MED 505 "
                         "is wild:army_tb_med_505_altitude.)",
             notice=dated(2004, "check current altitude medicine guidance for medicines and doses.") + " "
                    + ARMY_NOTE + " " + REMOTE_NOTE),
    K.us_pdf(GROUP, name="noaa_diving_manual_1991", title="NOAA Diving Manual: Diving for Science and Technology "
             "(3rd edition, 1991)", subject="Diving medicine", publisher="National Oceanic and Atmospheric "
             "Administration (NOAA), Office of Undersea Research", archive="noaadivingmanual00unit",
             published="1991", version="3rd edition, 1991 (Internet Archive item noaadivingmanual00unit)",
             description="NOAA's manual for scientific and working divers, with its chapters on diving physics and "
                         "physiology, the medical problems of diving (barotrauma, decompression sickness, gas "
                         "embolism, nitrogen narcosis, oxygen toxicity, hypothermia), diver first aid and "
                         "recompression, hazardous marine animals, and the decompression tables of its day.",
             notice=dated(1991, "its decompression tables and treatment tables are those of its day; never use "
                                "them to plan a dive. The Divers Alert Network (DAN) gives diving emergency advice "
                                "by phone.") + " A work of the US government (public domain); its photographs are "
                    "not reproduced (NOAA asks permission for them), only their captions. " + REMOTE_NOTE),
]

OUTBREAK_SITES = ["cholera", "typhoid-fever", "hepatitis-a", "hepatitis-e", "shigella", "giardia",
                  "cryptosporidium", "measles", "pertussis", "tetanus", "malaria", "dengue", "west-nile-virus",
                  "mosquitoes", "ebola", "plague", "hantavirus", "leptospirosis"]
AUSTERE_GUIDES = [M.cdc_book(
    GROUP, "cdc_outbreak_diseases", "Infectious diseases after disasters and in remote places (CDC)",
    "Outbreak diseases", OUTBREAK_SITES,
    "CDC's pages for the public on infectious diseases that break out when water, sanitation or shelter fail, or "
    "that travellers meet far from care, every page of each site: cholera, typhoid fever, hepatitis A and E, "
    "shigella, giardia and cryptosporidium (dirty water and food), measles, whooping cough and tetanus (and their "
    "vaccines), malaria, dengue, West Nile virus and mosquito bite prevention, Ebola, plague, hantavirus and "
    "leptospirosis (rodents and floodwater): the signs, how they spread, prevention and when to get care. (Flu, "
    "COVID-19 and stomach bugs are homecare:cdc_common_illnesses; rabies and ticks are firstaid:cdc_bites_ticks.)",
    units=[(r"/(cholera|typhoid-fever|hepatitis-[ae]|shigella|giardia|cryptosporidium)/", "Water and food"),
           (r"/(measles|pertussis|tetanus)/", "Vaccine-preventable diseases"),
           (r"/(malaria|dengue|west-nile-virus|mosquitoes)/", "Mosquitoes"), (r".", "Other outbreaks")],
    note=WEB_EDITION + " " + REMOTE_NOTE, limit=400)]

# ====================================================================== psychological first aid (rmed-pfa)

# The National Child Traumatic Stress Network's and the National Center for PTSD's notice, printed in each guide:
# "You are welcome to copy or redistribute this material in print or electronically provided the text is not
# modified, the authors ... are cited in any use, and no fee is charged for copies of this publication." So the guides
# are kept WHOLE with their text unchanged (only their format converted: sources.WHOLE_AND_UNCHANGED), credited, and
# PERSONAL USE ONLY (no fee may be charged; commercial use needs written permission).
NCTSN_LICENCE = "NCTSN and NCPTSD permission (copy whole and unchanged, credited, free of charge)"
NO_CHANGES = {NCTSN_LICENCE: "non-commercial-no-changes"}
NCTSN_TEXT = r"You are welcome to copy or redistribute this material"
NCTSN_URL = "https://www.nctsn.org/resources/psychological-first-aid-pfa-field-operations-guide-2nd-edition"
NCTSN_NOTICE = ("Copyright of its authors (National Child Traumatic Stress Network and National Center for PTSD); "
                "copied as its own notice allows: whole, with the text not modified, the authors and both centres "
                "credited, and free of charge. PERSONAL USE ONLY: no fee may be charged and commercial use needs "
                "the NCTSN's written permission.")


def nctsn(name, title, archive, year, description, outdated):
    """One NCTSN / National Center for PTSD field guide, whole and unchanged, personal use only (see above)."""
    return dict(group=GROUP, name=name, title=title, subject="Psychological first aid", publisher="National Child "
                "Traumatic Stress Network and the National Center for PTSD (US Department of Veterans Affairs), "
                "funded by SAMHSA", archive=archive, country="United States", licence=NCTSN_LICENCE,
                licence_url=NCTSN_URL, licence_page="", licence_text="", pdf_licence_text=NCTSN_TEXT,
                personal_use=True, unchanged=True, level="reference", published=str(year),
                version=f"{year} edition (Internet Archive item {archive})", description=description,
                notice=f"{dated(year, outdated)} {NCTSN_NOTICE} {REMOTE_NOTE}")


PFA_PDFS = [
    nctsn("nctsn_pfa_field_operations_guide_2006", "Psychological First Aid: Field Operations Guide (2nd edition, "
          "2006)", "psychological-first-aid-field-operations-guide", 2006,
          "The standard guide to helping people in the hours and days after a disaster or terrorism, for anyone "
          "helping, not only counsellors: preparing to help, then the eight core actions (contact and engagement, "
          "safety and comfort, stabilisation, gathering information on needs, practical help, connection with "
          "social supports, information on coping, and linking with services), with what to say to adults, "
          "children and older people, caring for the helper, worksheets and handouts.",
          "the help lines and services it names have changed; in the US the Disaster Distress Helpline is 1-800-985-"
          "5990 and the crisis line is 988."),
    nctsn("nctsn_pfa_for_schools_2012", "Psychological First Aid for Schools: Field Operations Guide (2nd edition)",
          "1-pfa-for-schools-final", 2012,
          "Psychological first aid adapted for schools after an emergency: the same core actions for teachers, "
          "school staff and families, with what to say to students of different ages, and handouts.",
          "the help lines and services it names have changed; in the US the crisis line is 988."),
    nctsn("ncptsd_skills_psychological_recovery_2010", "Skills for Psychological Recovery: Field Operations Guide "
          "(2010)", "skills-for-psychological-recovery-field-operations-guide", 2010,
          "What comes after psychological first aid, in the weeks and months after a disaster: gathering "
          "information and setting priorities, building problem-solving skills, promoting positive activities, "
          "managing reactions, promoting helpful thinking and rebuilding healthy social connections, with "
          "worksheets.",
          "the help lines and services it names have changed; in the US the crisis line is 988."),
    jts("jts_forward_mental_health", "Forward Management of Acute Mental Health Conditions by Non-Specialty Medical "
        "Personnel (Psychological Health Center of Excellence, Joint Trauma System list)",
        CPG + r"Mental_Health_[^/]*\.pdf$",
        "The Defense Health Agency's guideline for medics and other non-specialists caring for someone in mental "
        "crisis far from a specialist: combat and operational stress reactions, acute stress, panic, suicidal "
        "thoughts and safety, agitation and psychosis, sleep, substance problems, and when and how to evacuate."),
]
PFA_PDFS[-1]["subject"] = "Mental health crises far from help"

VA_PTSD = "https://www.ptsd.va.gov/PTSD/disaster_events/"
PFA_GUIDES = [K.guide(
    GROUP, "va_ptsd_disaster_events", "Disaster events: reactions, self-care and helping others (VA National Center "
    "for PTSD)", "Coping after disasters", "US Department of Veterans Affairs, National Center for PTSD",
    [VA_PTSD + s + "/index.asp" for s in ("for_everyone", "for_providers", "for_employers")],
    r"^https://www\.ptsd\.va\.gov/PTSD/disaster_events/(for_everyone|for_providers|for_employers)/[a-z_]+\.asp$",
    "The National Center for PTSD's disaster pages, every page: what to expect after a disaster, effects and risk "
    "factors, self-care, helpful thinking, helping others and families, the media after a traumatic event; for "
    "helpers and responders, psychological first aid, skills for psychological recovery and stress first aid, the "
    "phases of disaster reactions, managing grief and stress, older adults, rescue workers and moral injury; and "
    "for employers and community leaders, helping and supporting staff after a large-scale event.",
    f"A work of the US Department of Veterans Affairs (public domain). {WEB_EDITION} {REMOTE_NOTE}", depth=1,
    units=[(r"/for_everyone/", "For everyone"), (r"/for_providers/", "For helpers and responders"),
           (r".", "For employers and community leaders")], limit=80)]

# ====================================================================== nursing and caregiving at home (rmed-nursing)

OLD_NURSING = ("Published in {year}: an old book. Its nursing of the sick at home is that of its day: its medicines, "
               "doses, home remedies, infant feeding, disinfectants and infection ideas are out of date, and some "
               "are now known to be harmful. Use it for the practical ways of caring for a sick person in bed, and "
               "follow current guidance for everything else.")
NURSING_PDFS = [
    old_book(GROUP, "arc_home_hygiene_care_sick_1922", "American Red Cross Text-Book on Home Hygiene and Care of the "
             "Sick (1922)", "Home nursing", "American National Red Cross; Jane A. Delano and Isabel McIsaac (P. "
             "Blakiston's Son and Co.)", "ARCTextBook1922", 1922,
             "The Red Cross course book for caring for the sick at home: the sickroom, the bed and changing it "
             "with the patient in it, bathing and feeding the patient, taking temperature, pulse and breathing, "
             "giving medicines, preventing bedsores, caring for a person with an infectious disease, mothers and "
             "babies, emergencies and simple first aid.", note=OLD_NURSING, notice=REMOTE_NOTE),
    old_book(GROUP, "harrison_text_book_home_nursing_1918", "A Text Book of Home Nursing (Eveleen Harrison, 1918)",
             "Home nursing", "Eveleen Harrison (Macmillan)", "cu31924031241734", 1918,
             "A home nursing textbook \"for the care of the sick\": the patient's room, beds and bed-making, "
             "the patient's bath and comfort, observing and recording symptoms, feeding the sick, infections, "
             "convalescence, the care of children and the old, and emergencies.", note=OLD_NURSING,
             notice=REMOTE_NOTE),
    old_book(GROUP, "pope_home_care_of_sick_1907", "Home Care of the Sick (Amy Elizabeth Pope, 1907)",
             "Home nursing", "Amy Elizabeth Pope (American School of Home Economics)", "homecareofsick00poperich",
             1907,
             "A home study course in nursing at home: the sickroom, the bed, bathing and moving a patient, "
             "watching for symptoms, foods for the sick, giving medicines, infectious diseases, and accidents and "
             "emergencies.", note=OLD_NURSING, notice=REMOTE_NOTE),
]

FDA = "https://www.fda.gov"
FDA_PAGES = [FDA + p for p in (
    "/drugs/resources-drugs/drug-interactions-what-you-should-know",
    "/consumers/consumer-updates/grapefruit-juice-and-some-drugs-dont-mix",
    "/drugs/information-consumers-and-patients-drugs/think-it-through-managing-benefits-and-risks-medicines",
    "/drugs/buying-using-medicine-safely/understanding-over-counter-medicines",
    "/drugs/understanding-over-counter-medicines/safe-use-over-counter-otc-medicines-children",
    "/drugs/buying-using-medicine-safely/antibiotics-and-antibiotic-resistance",
    "/drugs/information-consumers-and-patients-drugs/you-age-you-and-your-medicines",
    "/drugs/information-consumers-and-patients-drugs/stop-learn-go-tips-talking-your-pharmacist-learn-how-use-"
    "medicines-safely",
    "/drugs/find-information-about-drug/finding-and-learning-about-side-effects-adverse-reactions")]
FDA_POLICY = "https://www.fda.gov/about-fda/about-website/website-policies"
FDA_TEXT = r"They are in the public domain and may be republished, reprinted and otherwise used freely"
NURSING_GUIDES = [dict(M.pages_book(
    GROUP, "fda_using_medicines_safely", "Using medicines safely: drug interactions, over-the-counter medicines and "
    "antibiotics (FDA)", "Medicines and interactions", "US Food and Drug Administration (FDA)", FDA_PAGES,
    "^(" + "|".join(re.escape(u) for u in FDA_PAGES) + ")$",      # only these pages (other modules read others)
    "The FDA's pages for the public on using medicines safely, each whole: drug interactions (with other "
    "medicines, food and drink, and health conditions), grapefruit juice and some drugs, managing the benefits "
    "and risks of medicines, understanding and reading over-the-counter medicine labels, giving over-the-counter "
    "medicines to children, antibiotics and antibiotic resistance, medicines as you age, talking with your "
    "pharmacist, and side effects. (Each medicine's own label, with its interactions, is in the medicine books: "
    "request word medicines.)",
    "From the FDA (a US government work, public domain). Read each medicine's own label, and ask a pharmacist or "
    "radio medical advice before combining medicines. " + WEB_EDITION + " " + REMOTE_NOTE,
    units=[(r"interaction|grapefruit", "Drug interactions"), (r".", "Using medicines safely")]),
    licence_page=FDA_POLICY, licence_text=FDA_TEXT)]

# ====================================================================== the index

SECTIONS = [
    ("Start here", "These books are for when a doctor, nurse or ambulance is hours or days away: at sea, in the "
     "backcountry, after a disaster, or caring for someone at home. They are no replacement for training or for "
     "real care: call for help first (911, VHF channel 16 at sea, or a satellite messenger or beacon where there "
     "is no phone signal), and get professional care as soon as you can. Old editions are kept as history; each "
     "book says what in it is out of date.", [
         ("key", "firstaid:nhs_emergency_first_aid", "First aid for emergencies and injuries (NHS)"),
         ("key", "pdf:army_fm_4_25_11_first_aid", "First Aid for everyone (Army FM 4-25.11)"),
         ("word", "first-aid", "The first aid books (request word)"),
         ("word", "wilderness-first-aid", "Wilderness first aid and backcountry safety (request word)"),
         ("word", "remote-medicine", "Every book of this remote medicine collection (request word)")]),
    ("Medicine at sea", "Guides for ships with no doctor on board, and the medicine chest a ship carries.", [
        ("key", "rmed:ships_medicine_chest_2003", "The Ship's Medicine Chest and Medical Aid at Sea (2003)"),
        ("key", "rmed:ships_medicine_chest_1940", "The Ship's Medicine Chest and First Aid at Sea (1940, history)"),
        ("key", "rmed:ships_medicine_chest_1929", "The Ship's Medicine Chest and First Aid at Sea (1929, history)"),
        ("key", "rmed:ships_medicine_chest_1904", "Handbook for the Ship's Medicine Chest (1904, history)"),
        ("key", "rmed:uk_mca_msn_1905_ships_medical_stores", "Ships' medical stores: what a ship must carry (UK)"),
        ("key", "rmed:uk_mca_medical_notices_at_sea", "Infectious disease at sea and radio medical advice (UK)"),
        ("key", "boat:uscg_bch_first_aid", "The Coast Guard's boat crew first aid handbook"),
        ("word", "rmed-ship", "The ship's medicine books (request word)"),
        ("link", "World Health Organization: International Medical Guide for Ships (3rd edition)",
         "https://www.who.int/publications/i/item/9789241547208", "WHO's copyright; open it in a browser"),
        ("link", "UK Ship Captain's Medical Guide (24th edition)",
         "https://www.gov.uk/government/publications/min-718-mf-the-ship-captains-medical-guide-24th-edition",
         "sold by TSO; not free to copy, as the MCA's notice says")]),
    ("Remote and prolonged care", "Caring for a sick or injured person for hours or days before help comes.", [
        ("key", "rmed:jts_prolonged_casualty_care", "Prolonged Casualty Care Guidelines (Joint Trauma System)"),
        ("key", "rmed:jts_nursing_interventions_pcc", "Nursing care in prolonged casualty care"),
        ("key", "rmed:jts_telemedicine", "Getting advice from a distant doctor (telemedicine)"),
        ("key", "rmed:socom_sof_medical_handbook_2001", "Special Operations Forces Medical Handbook (2001)"),
        ("key", "firstaid:army_st_31_91b_special_forces_medical", "Special Forces Medical Handbook (ST 31-91B, 1982)"),
        ("key", "rmed:army_emergency_war_surgery_2004", "Emergency War Surgery (2004), for trained surgeons"),
        ("key", "pdf:navy_hospital_corpsman", "Hospital Corpsman (US Navy course, 2000)"),
        ("word", "rmed-austere", "The remote and austere care books (request word)"),
        ("word", "military-whole", "Whole military manuals: survival, desert, jungle and mountain (request word)"),
        ("word", "service-skills-medical", "The Army Medical Department's self-study courses: vital signs, wounds, "
                                           "nursing care, pharmacy and preventive medicine (request word)")]),
    ("Heat, cold, altitude, water and diving", "The environment's injuries, and how to prevent them.", [
        ("key", "wild:army_tb_med_507_heat", "Heat illness (Army TB MED 507)"),
        ("key", "rmed:usariem_desert_heat_1990", "Staying healthy in the desert (USARIEM, 1990)"),
        ("key", "wild:army_tb_med_508_cold", "Cold injuries (Army TB MED 508)"),
        ("key", "rmed:usariem_cold_weather_1992", "Staying healthy in the cold (USARIEM, 1992)"),
        ("key", "rmed:jts_hypothermia", "Hypothermia (Joint Trauma System)"),
        ("key", "rmed:jts_frostbite_immersion_foot", "Frostbite and immersion foot (Joint Trauma System)"),
        ("key", "wild:army_tb_med_505_altitude", "Altitude illness (Army TB MED 505)"),
        ("key", "rmed:usariem_altitude_guide_2004", "Altitude acclimatization guide (USARIEM, 2004)"),
        ("key", "rmed:jts_drowning", "Drowning (Joint Trauma System)"),
        ("key", "rmed:noaa_diving_manual_1991", "Diving medicine (NOAA Diving Manual, 1991)"),
        ("key", "firstaid:cdc_yellow_book", "Travel health: the CDC Yellow Book")]),
    ("Infections and outbreaks", "Diseases that spread when clean water, sanitation or shelter fail.", [
        ("key", "rmed:cdc_outbreak_diseases", "Infectious diseases after disasters and in remote places (CDC)"),
        ("key", "homecare:cdc_common_illnesses", "Colds, flu, COVID-19 and stomach bugs (CDC)"),
        ("key", "firstaid:cdc_bites_ticks", "Animal bites, rabies and ticks (CDC)"),
        ("key", "outcook:cdc_emergency_water", "Making water safe in an emergency (CDC)"),
        ("key", "rmed:jts_infection_prevention", "Preventing infection in serious wounds (Joint Trauma System)")]),
    ("Psychological first aid", "Helping people in shock, fear or grief after a disaster, and caring for "
     "yourself as a helper.", [
         ("key", "rmed:nctsn_pfa_field_operations_guide_2006", "Psychological First Aid: Field Operations Guide "
                                                               "(personal use only)"),
         ("key", "rmed:ncptsd_skills_psychological_recovery_2010", "Skills for Psychological Recovery (personal "
                                                                   "use only)"),
         ("key", "rmed:nctsn_pfa_for_schools_2012", "Psychological First Aid for Schools (personal use only)"),
         ("key", "rmed:va_ptsd_disaster_events", "Disaster reactions and self-care (VA National Center for PTSD)"),
         ("key", "rmed:jts_forward_mental_health", "Mental health crises far from a specialist (DHA)"),
         ("key", "gpo:samhsa_trouble_coping_after_disaster_2007", "Having trouble coping after a disaster? (SAMHSA)"),
         ("key", "gpo:samhsa_traumatic_event_stress_2007", "Managing stress after a traumatic event (SAMHSA)"),
         ("key", "gpo:samhsa_coping_with_grief_2017", "Coping with grief after a disaster (SAMHSA)"),
         ("key", "gpo:samhsa_talking_to_children_trauma_2007", "Talking to children after trauma (SAMHSA)"),
         ("key", "mind:help_lines", "Help lines (988 and others)"),
         ("word", "rmed-pfa", "The psychological first aid books (request word)"),
         ("link", "World Health Organization: Psychological first aid: Guide for field workers (2011)",
          "https://www.who.int/publications/i/item/9789241548205", "WHO's copyright; open it in a browser")]),
    ("Nursing and caregiving at home", "Looking after someone who is ill, injured or frail at home, for days or "
     "for the long term.", [
         ("key", "rmed:arc_home_hygiene_care_sick_1922", "Home Hygiene and Care of the Sick (Red Cross, 1922)"),
         ("key", "rmed:harrison_text_book_home_nursing_1918", "A Text Book of Home Nursing (1918)"),
         ("key", "rmed:pope_home_care_of_sick_1907", "Home Care of the Sick (1907)"),
         ("key", "homecare:cdc_caregiving_older_adults", "Caregiving and falls prevention (CDC)"),
         ("key", "homecare:va_caregiver_support", "VA Caregiver Support Program"),
         ("key", "homecare:nhs_common_illnesses", "Common illnesses and what to do at home (NHS)"),
         ("key", "gpo:nia_caring_alzheimers_2019", "Caring for a person with Alzheimer's disease (NIA)"),
         ("key", "gpo:cms_medicare_home_health_care", "Medicare and home health care (CMS)"),
         ("key", "aging:acl_long_term_care", "Long-term care (ACL)"),
         ("word", "home-health", "The home health books (request word)"),
         ("word", "rmed-nursing", "The home nursing books of this collection (request word)"),
         ("word", "course:libretexts:med-1", "Open RN nursing textbooks (CC BY: Nursing Fundamentals, "
                                             "Pharmacology, Mental Health and Community Concepts, Management) "
                                             "among LibreTexts' medicine books"),
         ("word", "course:libretexts:med-0", "Open RN Nursing Skills among LibreTexts' medicine books"),
         ("word", "course:libretexts:med-3", "Open RN Nursing Advanced Skills and Nursing Assistant among "
                                             "LibreTexts' medicine books")]),
    ("Medicines", "What a medicine is for, its dose and its dangers, in its own label's words.", [
        ("key", "rmed:fda_using_medicines_safely", "Using medicines safely and drug interactions (FDA)"),
        ("key", "rmed:uk_mca_msn_1905_ships_medical_stores", "A ship's medicine list (UK)"),
        ("key", "rmed:jts_analgesia_sedation_pfc", "Pain relief far from help (Joint Trauma System)"),
        ("word", "medicines", "The medicine label books (DailyMed)"),
        ("key", "mlp:health_topics", "MedlinePlus health topics")]),
    ("Teeth, eyes and childbirth", "When a toothache, an eye injury or a birth cannot wait.", [
        ("word", "dental-care", "Dental care books (request word)"),
        ("word", "eye-care", "Eye care books (request word)"),
        ("key", "rmed:jts_ocular_injuries_pfc", "Eye injuries far from an eye doctor (Joint Trauma System)"),
        ("key", "firstaid:emergency_childbirth_self_help", "Emergency Childbirth (US Public Health Service)"),
        ("word", "midwifery", "Pregnancy, birth and after-birth care (request word)")]),
    ("Courses and books to buy or borrow (links only)", "Training is the best preparation: take a course.", [
        ("link", "Wilderness Medical Society practice guidelines", "https://wms.org/magazine/1316/practice-guidelines",
         "non-commercial, no derivatives; open them in a browser"),
        ("link", "Hesperian: Where There Is No Doctor", "https://hesperian.org/",
         "free for non-commercial use; fetch it yourself"),
        ("link", "Borden Institute: Emergency War Surgery (5th edition, 2018)",
         "https://medcoe.army.mil/borden", "parts are copyright; open it in a browser"),
        ("link", "American Red Cross: First Aid, CPR and wilderness courses", "https://www.redcross.org/take-a-class",
         "copyright; take a class")]),
]
INDEX = X.index_maker(PREFIX, GROUP, "Remote and long-term care medicine: a guide to the library",
                      "Remote and long-term care medicine",
                      "A plain-words guide to medical help for when professional care is hours or days away: medicine "
                      "at sea, remote and prolonged care, the environment's injuries, outbreaks, psychological first "
                      "aid, nursing and caregiving at home, and medicines.", SECTIONS)
MAKERS = {"index": INDEX}

THEMES = {"rmed-ship": SHIP_GUIDES + SHIP_PDFS, "rmed-austere": AUSTERE_GUIDES + AUSTERE_PDFS,
          "rmed-pfa": PFA_GUIDES + PFA_PDFS, "rmed-nursing": NURSING_GUIDES + NURSING_PDFS}
GUIDES = SHIP_GUIDES + AUSTERE_GUIDES + PFA_GUIDES + NURSING_GUIDES
PDFS = SHIP_PDFS + AUSTERE_PDFS + PFA_PDFS + NURSING_PDFS


def _theme(word):
    """The keys of one theme word (the index first, so every theme carries the guide)."""
    return lambda: [f"{PREFIX}:index"] + [f"{PREFIX}:{e['name']}" for e in THEMES[word]]


WORDS = {word: _theme(word) for word in THEMES}
WORDS["remote-medicine"] = lambda: [f"{PREFIX}:index"] + [f"{PREFIX}:{e['name']}" for e in GUIDES + PDFS]
COLLECTION = K.Collection(PREFIX, GROUP, guides=GUIDES, pdfs=PDFS, makers=MAKERS, words=WORDS)

LICENCE_LINES = {
    "rmed_us_gov": "Works of the US government (17 U.S.C. 105): the Ship's Medicine Chest (1940, 2003), the NOAA "
                   "Diving Manual (1991), the VA National Center for PTSD's pages; govinfo.gov's quotation of the law "
                   "checked at every build; archive.org's and ptsd.va.gov's robots.txt allow the files (checked "
                   "2026-11-23).",
    "rmed_military": "Joint Trauma System guidelines (read from jts.health.mil, which has no robots.txt and answers "
                     "without a login), Emergency War Surgery 2004 (DTIC copy, prints Distribution Statement A), the "
                     "SOF Medical Handbook 2001 and the USARIEM technical notes (Internet Archive copies): judged at "
                     "every build by the release rule of military_release.py (the owner's decision of 22 November "
                     "2026), read whole.",
    "rmed_cdc_fda": "CDC's terms (as mind_cdc; the pages kept whole) and the FDA's website policies (\"They are in "
                    "the public domain\"), checked at every build; robots.txt allows the pages (checked 2026-11-23).",
    "rmed_ogl": "gov.uk publication pages: \"All content is available under the Open Government Licence v3.0, except "
                "where otherwise stated\" (checked at every build on each page).",
    "rmed_nctsn": "The NCTSN and National Center for PTSD field guides print: \"You are welcome to copy or "
                  "redistribute this material in print or electronically provided the text is not modified, the "
                  "authors ... are cited in any use, and no fee is charged for copies of this publication\" (checked "
                  "in each PDF at every build): kept whole and unchanged, credited, personal use only.",
    "rmed_old_books": "Internet Archive items dated before 1931 (checked at every build): the 1904 and 1929 Ship's "
                      "Medicine Chest and three home nursing books.",
    "rmed_index": "The index (rmed:index) is the toolkit's own facts and links, CC0.",
}
NOT_INCLUDED = [
    ("World Health Organization: International Medical Guide for Ships (3rd edition, 2007) and Psychological first "
     "aid: Guide for field workers (2011)", "WHO's copyright (\"All rights reserved\" in the 2011 guide; the "
     "Internet Archive's 1967 guide is a lending-library scan), and www.who.int's robots.txt shuts out AI companies' "
     "readers. Link-only from the index. Index: https://www.who.int/publications/i/item/9789241547208"),
    ("UK Ship Captain's Medical Guide (24th edition, 2024)", "The MCA's notice MIN 718 says it \"is not freely "
     "available from www.gov.uk\" and \"may not be reproduced without the permission of TSO\"; its 22nd edition "
     "copy on the Internet Archive is the same Crown copyright work. The MCA's notices on medical stores and medical "
     "advice at sea are built. Index: https://www.gov.uk/government/publications/min-718-mf-the-ship-captains-"
     "medical-guide-24th-edition"),
    ("The Ship's Medicine Chest, 1947, 1955 and 1978 editions", "The Internet Archive's copies are lending-library "
     "scans that cannot be downloaded (checked 2026-11-23); the 1904, 1929, 1940 and 2003 editions are built. Index: "
     "https://archive.org/search?query=title%3A%28ship%27s+medicine+chest%29"),
    ("Borden Institute: Emergency War Surgery 5th edition (2018) and Medical Aspects of Harsh Environments (2001 and "
     "2002)", "They print \"Certain parts of this publication pertain to copyright restrictions. All rights "
     "reserved.\" Link-only. The 2004 third revision of Emergency War Surgery, which prints no such line and "
     "carries Distribution Statement A, is built. Index: https://medcoe.army.mil/borden"),
    ("Emergency War Surgery, first United States revision (1975)", "Superseded by the 2004 revision, which is built. "
     "Index: https://archive.org/details/emergencywarsurg00unit_0"),
    ("Open RN nursing textbooks (WisTech Open: Nursing Fundamentals, Nursing Skills, Pharmacology, Mental Health "
     "and Community Concepts, Management and Professional Concepts, Advanced Skills; CC BY 4.0)", "Already in the "
     "library through LibreTexts' medicine shelf (course:libretexts:med-0, med-1 and med-3, linked from the index); "
     "not built twice. Open RN's Health Promotion book is not on LibreTexts, and wtcs.pressbooks.pub refuses "
     "programs (403) and its robots.txt forbids its API: link-only. Index: https://wtcs.pressbooks.pub/"
     "nursingfundamentals/"),
    ("NCTSN and VA handouts: Psychological First Aid handouts (VA_NCPTSD_ALL_508.pdf) and the PFA mobile app",
     "The handouts are already inside the field guide (appendix F), and the VA's copy's text layer repeats one page's "
     "words on every page. Index: https://www.ptsd.va.gov/disaster_events/for_providers/index.asp"),
    ("Alaska Community Health Aide/Practitioner Manual (1987)", "A fine remote-care manual, but it prints \"1987 "
     "Alaska Area Native Health Service. All rights reserved under International and Pan American Copyright "
     "Conventions\": link-only. Index: https://archive.org/details/Alaska-community-health-aide-practitioner-"
     "manual-1987"),
    ("US Coast Guard Medical Manual (COMDTINST M6000.1) and Military Sealift Command medical guides", "The Coast "
     "Guard manual is the service's health-care administration rules, not a treatment guide; no Coast Guard, NOAA or "
     "Military Sealift Command guide to treating the sick at sea was found as an open copy (searched 2026-11-23). "
     "Index: https://archive.org/details/Coast_Guard_Medical_Manual"),
    ("US Navy Diving Manual", "No recent revision with a text layer was found on the Internet Archive (only "
     "research reports about it, searched 2026-11-23), and navsea.navy.mil refuses programs. The NOAA Diving Manual "
     "(1991) is built. Index: https://www.navsea.navy.mil/"),
    ("NOAA Diving Manual, 4th edition (2001) and later", "The 2001 copy has no text layer the builder could check "
     "here, and later editions are sold by a private publisher. Index: https://archive.org/details/"
     "NOAA_Diving_Manual-4e-2001"),
    ("Tactical Combat Casualty Care (TCCC) guidelines and the Center for Army Lessons Learned TCCC Handbook (2017)",
     "Care under fire for combat medics: not built in this pass, so as not to cross the military medic collections "
     "(the Army Medical Department's courses, request word service-skills-medical, and the Navy's Hospital "
     "Corpsman manuals); the CALL handbook has an Internet Archive copy (17-13-tactical-combat-casualty-care-"
     "handbook-ver-5-may-2017) for a later pass, and the TCCC guidelines themselves are published in a book reader "
     "(books.allogy.com) that offers no file. "
     "Index: https://jts.health.mil/index.cfm/committees/cotccc"),
    ("Joint Trauma System guidelines not chosen", "The surgical and hospital ones (REBOA, thoracotomy, cranial "
     "surgery, ventilators and others), the military working dog ones, and Unexploded Ordnance Management (about "
     "explosives) are not built; the prolonged-care, environmental and first-care ones are. Index: "
     "https://jts.health.mil/index.cfm/CPGs/cpgs"),
    ("Indian Health Service field guides", "No openly published IHS field or community health guide with a text "
     "layer was found (searched 2026-11-23). Index: https://www.ihs.gov/"),
    ("SAMHSA disaster distress leaflets", "Already built in govinfo_fill.py (gpo:samhsa_trouble_coping_after_disaster"
     "_2007 and the others), linked from the index. Index: https://www.samhsa.gov/find-help/disaster-distress-"
     "helpline"),
    ("FDA: Don't Be Tempted to Use Expired Medicines and medicine disposal", "The FDA's disposal pages are in the "
     "recycling collection (recycle:); not repeated. Index: https://www.fda.gov/drugs/safe-disposal-medicines/"
     "dont-be-tempted-use-expired-medicines"),
]


def main(argv=None):
    """The command line (see the module docstring)."""
    return K.main_for(COLLECTION, __doc__, argv)


if __name__ == "__main__":
    sys.exit(main())
